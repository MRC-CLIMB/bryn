import datetime
import uuid

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from phonenumber_field.modelfields import PhoneNumberField
from tinymce import models as tinymce_models

from core import hashids
from .tokens import account_activation_token

User = get_user_model()


class Region(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=40)
    disabled = models.BooleanField(default=False)
    disable_new_instances = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=100)


class Team(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Group or team name", unique=True,
    )
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

    @property
    def hashid(self):
        return hashids.encode(self.id)

    @property
    def admin_users(self):
        """
        Return users with admin privileges for this team (queryset)
        """
        return self.users.filter(teammember__is_admin=True)

    @property
    def regular_users(self):
        """
        Return users with regular privileges for this team (queryset)
        """
        return self.users.filter(teammember__is_admin=False)

    @property
    def latest_licence_acceptance(self):
        if self.licence_acceptances.count():
            return self.licence_acceptances.latest("accepted_at")
        return None

    @property
    def licence_expiry(self):
        if self.latest_licence_acceptance:
            return self.latest_licence_acceptance.expiry
        return None

    @property
    def licence_is_valid(self):
        if self.latest_licence_acceptance:
            return not self.latest_licence_acceptance.has_expired
        return False

    def send_new_team_admin_email(self):
        if not settings.NEW_REGISTRATION_ADMIN_EMAILS:
            return

        context = {"user": self.creator, "team": self}
        subject = render_to_string(
            "userdb/email/new_registration_admin_subject.txt", context
        )
        text_content = render_to_string(
            "userdb/email/new_registration_admin_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/new_registration_admin_email.html", context
        )

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            settings.NEW_REGISTRATION_ADMIN_EMAILS,
            html_message=html_content,
            fail_silently=True,
        )

    def verify_and_send_notification_email(self):
        """Admin script: mark team as verified and notify the primary user"""
        context = {"user": self.creator, "team": self}
        subject = render_to_string(
            "userdb/email/notify_team_verified_subject.txt", context
        )
        text_content = render_to_string(
            "userdb/email/notify_team_verified_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/notify_team_verified_email.html", context
        )

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

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    def send_invitation_email(self):
        context = {
            "invitation": self,
            "url": reverse("user:accept_invitation", args=[self.uuid]),
        }
        subject = render_to_string("userdb/email/user_invite_subject.txt", context)
        text_content = render_to_string("userdb/email/user_invite_email.txt", context)
        html_content = render_to_string("userdb/email/user_invite_email.html", context)

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
        "openstack.KeyPair", on_delete=models.SET_NULL, blank=True, null=True
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
        )
        text_content = render_to_string(
            "userdb/email/user_verification_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/user_verification_email.html", context
        )

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
            "validation_link": request.build_absolute_uri(
                reverse(
                    "user:validate_email_change",
                    kwargs={
                        "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                        "token": account_activation_token.make_token(user),
                    },
                )
            ),
        }
        subject = render_to_string(
            "userdb/email/user_email_change_verification_subject.txt", context
        )
        text_content = render_to_string(
            "userdb/email/user_email_change_verification_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/user_email_change_verification_email.html", context
        )
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
        )
        text_content = render_to_string(
            "userdb/email/user_email_change_notification_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/user_email_change_notification_email.html", context
        )
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
        now = timezone.now()
        return (
            super()
            .get_queryset()
            .filter(effective_date__lte=now)
            .latest("effective_date")
        )


class LicenceVersion(models.Model):
    version_number = models.CharField(max_length=15, unique=True)
    licence_terms = tinymce_models.HTMLField()
    effective_date = models.DateField(default=timezone.now)
    validity_period_days = models.IntegerField(default="90")

    objects = LicenceVersionManager()

    def __str__(self):
        return f"Licence Version {self.version_number}"


class LicenceAcceptance(models.Model):
    version = models.ForeignKey(
        LicenceVersion,
        default=LicenceVersion.objects.current,
        on_delete=models.PROTECT,
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="licence_acceptances"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="licence_acceptances"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Licence acceptance for team {self.team.name}, by {self.user.email}"

    @property
    def expiry(self):
        return self.accepted_at + datetime.timedelta(
            days=self.version.validity_period_days
        )

    @property
    def has_expired(self):
        return timezone.now() > self.expiry


# Legacy user profile (uneditable due complex migration issues after 3.1 upgrade)
# TODO: delete model after data copied over
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    validation_link = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True
    )
    email_validated = models.BooleanField(default=False)
    current_region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def copy_to_new_profile(self):
        # Check for existing Profile row
        if len(Profile.objects.filter(user=self.user)) == 1:
            return
        Profile.objects.create(
            user=self.user,
            validation_link=self.validation_link,
            email_validated=self.email_validated,
        )

    def send_validation_link(self, user):
        self.user = user
        self.email_validated = False
        self.save()

        context = {
            "user": user,
            "validation_link": reverse(
                "user:validate_email", args=[self.validation_link]
            ),
        }
        subject = render_to_string(
            "userdb/email/user_verification_subject.txt", context
        )
        text_content = render_to_string(
            "userdb/email/user_verification_email.txt", context
        )
        html_content = render_to_string(
            "userdb/email/user_verification_email.html", context
        )

        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_content,
            fail_silently=False,
        )
