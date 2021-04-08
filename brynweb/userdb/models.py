import datetime
import uuid

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from phonenumber_field.modelfields import PhoneNumberField
from tinymce import models as tinymce_models

from core import hashids
from core.tasks import send_mail
from core.utils import main_text_from_html
from .tokens import account_activation_token

User = get_user_model()


class Region(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=40)
    disabled = models.BooleanField(default=False)
    new_instances_disabled = models.BooleanField(default=False)
    unshelving_disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=100)


def licence_expiry_default():
    return timezone.now() + datetime.timedelta(days=30)


class TeamQuerySet(models.QuerySet):
    def verified(self):
        return self.filter(verified=True)

    def licence_expired(self):
        return self.verified().filter(licence_expiry__lt=timezone.now())

    def licence_valid(self):
        return self.verified().filter(licence_expiry__gte=timezone.now())


class Team(models.Model):
    name = models.CharField(max_length=50, verbose_name="Group or team name")
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.CharField(
        max_length=50, verbose_name="Position (e.g. Professor)"
    )  # TODO: should be on user model
    department = models.CharField(max_length=50, verbose_name="Department")
    institution = models.CharField(max_length=100, verbose_name="Institution")
    phone_number = PhoneNumberField(
        max_length=20, verbose_name="Phone number"
    )  # TODO: should be on user model
    research_interests = models.TextField(
        verbose_name="Research interests",
        help_text="Please supply a brief synopsis of your research programme",
    )
    intended_climb_use = models.TextField(
        verbose_name="Intended use of CLIMB",
        help_text="Please let us know how you or your group intend to " "use CLIMB",
    )
    held_mrc_grants = models.TextField(
        verbose_name="Held MRC grants",
        help_text="If you currently or recent have held grant funding from "
        "the Medical Research Council it would be very helpful if you can "
        "detail it here to assist with reporting use of CLIMB",
    )
    verified = models.BooleanField(default=False)
    default_region = models.ForeignKey(
        Region, null=True, blank=True, on_delete=models.SET_NULL
    )
    tenants_available = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through="TeamMember", related_name="teams")
    licence_expiry = models.DateTimeField(default=licence_expiry_default)
    licence_last_reminder_sent_at = models.DateTimeField(
        blank=True, null=True, editable=False
    )

    # managers
    objects = TeamQuerySet.as_manager()

    @property
    def hashid(self):
        """
        Hashid used for urls
        """
        return hashids.encode(self.id)

    @property
    def admin_users(self):
        """
        Return users with admin privileges for this team (queryset)
        """
        return self.users.filter(team_memberships__is_admin=True)

    @property
    def regular_users(self):
        """
        Return users with regular privileges for this team (queryset)
        """
        return self.users.filter(team_memberships__is_admin=False)

    @property
    def latest_licence_acceptance(self):
        """
        Latest licence acceptance
        """
        if self.licence_acceptances.count():
            return self.licence_acceptances.latest("accepted_at")
        return None

    @property
    def licence_is_valid(self):
        """
        Licence is valid/not expired
        """
        return timezone.now() <= self.licence_expiry

    def send_new_team_admin_email(self):
        """
        Notify admin(s) of new team registration
        """
        if not settings.NEW_REGISTRATION_ADMIN_EMAILS:
            return

        context = {"user": self.creator, "team": self}
        subject = render_to_string(
            "userdb/email/new_registration_admin_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "userdb/email/new_registration_admin_email.html", context
        )
        text_content = main_text_from_html(html_content)

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            settings.NEW_REGISTRATION_ADMIN_EMAILS,
            html_message=html_content,
            fail_silently=True,
        )

    def verify_and_send_notification_email(self):
        """
        Admin script: mark team as verified and notify the primary user
        """
        context = {"user": self.creator, "team": self}
        subject = render_to_string(
            "userdb/email/notify_team_verified_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "userdb/email/notify_team_verified_email.html", context
        )
        text_content = main_text_from_html(html_content)

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.creator.email],
            html_message=html_content,
            fail_silently=False,
        )

        self.verified = True
        self.save()

    def send_team_licence_reminder_emails(self):
        """
        Send team licence expiry reminder emails to primary and secondary users
        """
        context = {
            "team": self,
            "team_management_url": f"/teams/{self.hashid}/team",  # Vue route, can't use reverse
            "time_remaining": (self.licence_expiry - timezone.now()),
            "termination_date": self.licence_expiry
            + datetime.timedelta(days=settings.LICENCE_TERMINATION_DAYS),
        }

        # Email each team member
        for user in self.users.all():
            context["user"] = user
            subject = render_to_string(
                "userdb/email/team_licence_reminder_subject.txt", context
            ).strip()
            if user in self.admin_users.all():
                html_content = render_to_string(
                    "userdb/email/team_licence_reminder_primary_user_email.html",
                    context,
                )
            else:
                html_content = render_to_string(
                    "userdb/email/team_licence_reminder_secondary_user_email.html",
                    context,
                )
            text_content = main_text_from_html(html_content)
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_content,
                fail_silently=True,
            )

        # Update team
        self.licence_last_reminder_sent_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="team_memberships"
    )
    is_admin = models.BooleanField(default=False)

    @property
    def hashid(self):
        return hashids.encode(self.id)

    def __str__(self):
        return "%s belongs to %s" % (self.user, self.team)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="unique_teammember")
        ]


class Invitation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name="Team to invite user to",
        related_name="invitations",
    )
    made_by = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    message = models.TextField()
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def create_team_membership(self, user):
        """Create a team membership from an invitation"""
        teammember = TeamMember(user=user, team=self.to_team, is_admin=False)
        teammember.save()
        self.accepted = True
        self.save()
        return teammember

    def send_invitation_email(self):
        context = {
            "invitation": self,
            "url": reverse("user:accept_invitation", args=[self.uuid]),
        }
        subject = render_to_string(
            "userdb/email/user_invite_subject.txt", context
        ).strip()
        html_content = render_to_string("userdb/email/user_invite_email.html", context)
        text_content = main_text_from_html(html_content)

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_content,
            fail_silently=False,
        )

    def __str__(self):
        return "%s to %s" % (self.email, self.to_team)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
        related_query_name="profile",
    )
    email_validated = models.BooleanField(default=False)
    default_keypair = models.ForeignKey(
        "openstack.KeyPair", on_delete=models.SET_NULL, null=True, blank=True
    )
    default_team_membership = models.ForeignKey(
        TeamMember, on_delete=models.SET_NULL, null=True, blank=True
    )
    new_email_pending_verification = models.EmailField(blank=True, null=True)

    def send_validation_link(self):
        user = self.user
        context = {
            "user": user,
            "validation_link": reverse(
                "user:validate_email",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                    "token": account_activation_token.make_token(user),
                },
            ),
        }
        subject = render_to_string(
            "userdb/email/user_verification_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "userdb/email/user_verification_email.html", context
        )
        text_content = main_text_from_html(html_content)

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_content,
            fail_silently=False,
        )

    def initiate_email_change(self, request, new_email):
        """Initiate an email addres change"""
        # Check email is unique
        if User.objects.filter(email=new_email).count():
            raise ValueError(
                "There is already a user account associated with this email"
            )

        # Temporarily store the new email on the users profile record, pending verificaction
        self.new_email_pending_verification = new_email
        self.save()

        # Notifiy existing email
        self.send_email_change_notification(request)

        # Send verification email to new email
        self.send_email_change_verification(request)

    def confirm_email_change(self):
        """Confirm a change of email address (updating username where appropriate)"""
        new_email = self.new_email_pending_verification
        self.new_email_pending_verification = None
        if self.user.username == self.user.email:
            self.user.username = new_email
        self.user.email = new_email
        self.user.save()  # signal will save profile

    def send_email_change_verification(self, request):
        """Send a verification email to the new email address"""
        user = self.user
        context = {
            "user": user,
            "validation_link": reverse(
                "user:validate_email_change",
                kwargs={
                    "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                    "token": account_activation_token.make_token(user),
                },
            ),
        }
        subject = render_to_string(
            "userdb/email/user_email_change_verification_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "userdb/email/user_email_change_verification_email.html", context
        )
        text_content = main_text_from_html(html_content)
        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.new_email_pending_verification],
            html_message=html_content,
            fail_silently=False,
        )

    def send_email_change_notification(self, request):
        """Send an email change notification to the existing/previous email address"""
        user = self.user
        context = {
            "user": user,
        }
        subject = render_to_string(
            "userdb/email/user_email_change_notification_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "userdb/email/user_email_change_notification_email.html", context
        )
        text_content = main_text_from_html(html_content)
        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_content,
            fail_silently=False,
        )

    def mark_email_validated(self):
        self.email_validated = True
        self.user.is_active = True
        self.user.save()  # Profile saves via signal

    def __str__(self):
        return f"{str(self.user)} profile"


class LicenceVersionManager(models.Manager):
    def current(self):
        today = timezone.now().date()
        return (
            super()
            .get_queryset()
            .filter(effective_date__lte=today)
            .latest("effective_date")
        )  # may raise LicenceVersion.DoesNotExist


class LicenceVersion(models.Model):
    version_number = models.CharField(max_length=15, unique=True)
    licence_terms = tinymce_models.HTMLField()
    effective_date = models.DateField(default=timezone.now)
    validity_period_days = models.IntegerField(default="90")

    objects = LicenceVersionManager()

    def __str__(self):
        return f"Licence Version {self.version_number}"


class LicenceAcceptance(models.Model):
    licence_version = models.ForeignKey(LicenceVersion, on_delete=models.PROTECT,)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="licence_acceptances"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="licence_acceptances"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Set the current licence version if not specified.
        """
        if not self.licence_version_id:
            self.licence_version = LicenceVersion.objects.current()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Licence acceptance for team {self.team.name}, by {self.user.email}"

    @property
    def expiry(self):
        return self.accepted_at + datetime.timedelta(
            days=self.licence_version.validity_period_days
        )

    @property
    def has_expired(self):
        return timezone.now() > self.expiry
