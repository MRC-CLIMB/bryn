from django.conf import settings
from django.utils import timezone

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from .models import HypervisorStats, Region, ServerLease
from .service import OpenstackService


@db_periodic_task(crontab(minute="10", hour="*/1"))
def update_hypervisor_stats():
    for region in Region.objects.filter(disabled=False):
        service = OpenstackService(region=region)
        stats = service.nova.hypervisors.statistics()
        defaults = {
            "hypervisor_count": stats.count,
            "disk_available_least": stats.disk_available_least,
            "free_disk_gb": stats.free_disk_gb,
            "free_ram_mb": stats.free_ram_mb,
            "local_gb": stats.local_gb,
            "local_gb_used": stats.local_gb_used,
            "memory_mb": stats.memory_mb,
            "memory_mb_used": stats.memory_mb_used,
            "running_vms": stats.running_vms,
            "vcpus": stats.vcpus,
            "vcpus_used": stats.vcpus_used,
        }
        HypervisorStats.objects.update_or_create(defaults=defaults, region=region)


@db_periodic_task(crontab(minute="*/30"))
def send_server_lease_expiry_reminder_emails():
    """Send server lease expiry reminder emails, on specified days until expiry"""
    reminder_days = settings.SERVER_LEASE_REMINDER_DAYS
    due_leases = ServerLease.objects.active_due()
    for lease in due_leases:
        if lease.time_remaining.days in reminder_days:
            last_reminder = lease.last_reminder_sent_at
            if last_reminder and (timezone.now() - last_reminder).days < 1:
                continue  # Don't send reminder more than once every 24 hours
            lease.send_email_renewal_reminder()
