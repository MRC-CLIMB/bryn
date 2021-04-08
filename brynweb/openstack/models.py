import datetime
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from slugify import slugify
from sshpubkeys import SSHKey

# from .service import OpenstackService
from .validators import validate_public_key
from core.tasks import send_mail
from core.utils import main_text_from_html
from userdb.models import Region, Team, TeamMember


User = get_user_model()

# Region model would ideally be in this app, but to avoid legacy migration issues it remains in userdb


class Tenant(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tenants")
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created_tenant_id = models.CharField(max_length=50)
    created_tenant_name = models.CharField(max_length=255, null=True, blank=True)
    created_network_id = models.CharField(max_length=50, blank=True)

    def get_tenant_name(self):
        """Generate slugified tenant name to when creating openstack project"""
        return f"bryn:{self.team.pk}_{slugify(self.team.name)}"

    def get_tenant_description(self):
        return f"{self.get_tenant_name()} ({self.team.creator.last_name})"

    def get_network_id(self):
        if self.region.regionsettings.requires_network_setup:
            return self.created_network_id
        else:
            # i.e. warwick
            return self.region.regionsettings.public_network_id

    def __str__(self):
        return self.created_tenant_name


class KeyPair(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name="keypairs",
        related_query_name="keypair",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("Keypair name"), max_length=50, unique=True)
    public_key = models.TextField(_("SSH public key"), validators=[validate_public_key])
    fingerprint = models.CharField(max_length=47, editable=False)

    class Meta:
        unique_together = [["user", "public_key"]]

    def save(self, *args, **kwargs):
        # Set fingerprint
        ssh = SSHKey(self.public_key)
        ssh.parse()
        self.fingerprint = ssh.hash_md5()[4:]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def get_default_server_lease_expiry():
    return timezone.now() + datetime.timedelta(days=settings.SERVER_LEASE_DEFAULT_DAYS)


class ServerLeaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False, shelved=False)

    def active_with_expiry(self):
        return self.active().filter(expiry__isnull=False)

    def active_overdue(self):
        return self.active_with_expiry().filter(expiry__lte=timezone.now())

    def active_due(self):
        return self.active_with_expiry().filter(expiry__gte=timezone.now())

    def active_indefinite(self):
        return self.active().filter(expiry__isnull=True)

    def deleted(self):
        return self.filter(deleted=True)

    def shelved(self):
        return self.filter(shelved=True)

    def inactive(self):
        return self.filter(Q(deleted=True) | Q(shelved=True))


class ServerLease(models.Model):
    server_id = models.UUIDField(unique=True, editable=False)
    server_name = models.CharField(max_length=255, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_renewed_at = models.DateTimeField(auto_now=True, editable=False)
    expiry = models.DateTimeField(
        default=get_default_server_lease_expiry, blank=True, null=True
    )
    renewal_count = models.PositiveIntegerField(default=0, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="server_leases", editable=False
    )
    assigned_teammember = models.ForeignKey(
        TeamMember, on_delete=models.PROTECT, related_name="server_leases",
    )
    shelved = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    last_reminder_sent_at = models.DateTimeField(blank=True, null=True, editable=False)

    objects = ServerLeaseQuerySet.as_manager()

    @property
    def time_remaining(self):
        if self.expiry:
            return self.expiry - timezone.now()
        return None

    @property
    def has_expired(self):
        if self.expiry is None:
            return False
        return timezone.now() > self.expiry

    @property
    def renewal_url(self):
        return reverse(
            "openstack:server_lease_renewal",
            kwargs={"server_id": self.server_id, "renewal_count": self.renewal_count},
        )

    def renew_lease(self, days=settings.SERVER_LEASE_DEFAULT_DAYS, user=None):
        self.expiry = timezone.now() + datetime.timedelta(days=days)
        self.renewal_count += 1
        if user:
            self.user = user
        self.last_reminder_sent_at = None
        self.save()

    def shelve_server(self):
        pass

    def send_email_renewal_reminder(self):
        """Send an email renewal reminder"""
        user = self.assigned_teammember.user
        context = {
            "user": user,
            "server_name": self.server_name,
            "renewal_url": self.renewal_url,
            "expiry": self.expiry,
            "days_remaining": self.time_remaining.days,
            "hours_remaining": self.time_remaining.days * 24
            + self.time_remaining.seconds // 3600,
        }
        subject = render_to_string(
            "openstack/email/server_lease_expiry_reminder_subject.txt", context
        ).strip()
        html_content = render_to_string(
            "openstack/email/server_lease_expiry_reminder_email.html", context
        )
        text_content = main_text_from_html(html_content)
        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_content,
            fail_silently=False,
        )
        self.last_reminder_sent_at = timezone.now()
        self.save()

    def __str__(self):
        return (
            f"Lease for server '{self.server_name}', belonging to '{self.tenant.team.name}' "
            f"at {self.tenant.region.name}"
        )


class ServerLeaseRequest(models.Model):
    server_lease = models.ForeignKey(
        ServerLease, on_delete=models.CASCADE, editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lease_requests", editable=False,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    closed = models.BooleanField(default=False)
    responded_at = models.DateTimeField(null=True, blank=True, editable=False)
    response = models.TextField()
    granted = models.BooleanField(default=False, editable=False)
    actioned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lease_request_responses",
        null=True,
        editable=False,
    )

    def send_admin_notification_email(self):
        admin_emails = settings.REGION_ADMINS.get(self.server_lease.tenant.region.name)
        if not admin_emails:
            return
        context = {"server_lease_request": self}
        subject = render_to_string(
            "openstack/email/server_lease_request_admin_notification_subject.txt",
            context,
        ).strip()
        text_content = render_to_string(
            "openstack/email/server_lease_request_admin_notification_email.txt", context
        )
        send_mail(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )

    def grant(self, request):
        lease = self.server_lease
        lease.expiry = None
        lease.save()

        self.granted = True
        self.closed = True
        self.responded_at = timezone.now()
        self.actioned_by = request.user
        self.save()

        self.send_lease_granted_email()

    def send_lease_granted_email(self):
        context = {"server_lease_request": self}
        subject = render_to_string(
            "openstack/email/server_lease_request_granted_subject.txt", context,
        ).strip()
        html_content = render_to_string(
            "openstack/email/server_lease_request_granted_email.html", context
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

    def reject(self, request):
        self.closed = True
        self.responded_at = timezone.now()
        self.actioned_by = request.user
        self.save()

        self.send_lease_rejected_email()

    def send_lease_rejected_email(self):
        context = {"server_lease_request": self}
        subject = render_to_string(
            "openstack/email/server_lease_request_rejected_subject.txt", context,
        ).strip()
        html_content = render_to_string(
            "openstack/email/server_lease_request_rejected_email.html", context
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

    def __str__(self):
        return f"Indefinite lease request for {self.server_lease.server_name}"


class HypervisorStats(models.Model):
    region = models.OneToOneField(Region, on_delete=models.CASCADE)

    last_updated = models.DateTimeField(auto_now=True)

    hypervisor_count = models.IntegerField()
    disk_available_least = models.IntegerField()
    free_disk_gb = models.IntegerField()
    free_ram_mb = models.IntegerField()
    local_gb = models.IntegerField()
    local_gb_used = models.IntegerField()
    memory_mb = models.IntegerField()
    memory_mb_used = models.IntegerField()
    running_vms = models.IntegerField()
    vcpus = models.IntegerField()
    vcpus_used = models.IntegerField()

    class Meta:
        verbose_name_plural = "Hypervisor Stats"


class RegionSettings(models.Model):
    region = models.OneToOneField(Region, on_delete=models.CASCADE)
    public_network_name = models.CharField(max_length=50)
    public_network_id = models.CharField(max_length=50)
    requires_network_setup = models.BooleanField(default=False)
    floating_ip_pool = models.CharField(max_length=50, blank=True)
    horizon_endpoint = models.URLField(blank=True)  # TODO: remove blank after migration
    max_volume_size_gb = models.IntegerField(
        _("Maximum allowed volume size in GB"), default=5000
    )

    class Meta:
        verbose_name_plural = "Region Settings"

    def __str__(self):
        return str(self.region)


def get_tenant_for_team(team, region):  # TODO delete this once refactoring complete
    tenant = Tenant.objects.filter(team=team, region=Region.objects.get(name=region))
    if not tenant:
        return None
    if len(tenant) > 1:
        return None
    return tenant[0]
