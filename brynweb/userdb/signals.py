from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from openstack.models import KeyPair
from .models import LicenceAcceptance, Profile, Team


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile on User creation.
    Auto-save Profile on User save
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=LicenceAcceptance)
def update_team_licence_expiry(sender, instance, created, **kwargs):
    """
    Update team.licence_expiry on LicenceAcceptance save.
    De-normalized to allow for more convenient querying.
    """
    if created:
        instance.team.licence_expiry = instance.expiry
        instance.team.save()


@receiver(post_save, sender=Profile)
def send_email_validation_link(sender, instance, created, **kwargs):
    """Send email validation link on profile creation"""
    if created:
        instance.send_validation_link()


@receiver(post_save, sender=Team)
def send_new_registration_admin_email(sender, instance, created, **kwargs):
    """Send email to notify admin of new registration"""
    if created:
        instance.send_new_team_admin_email()


@receiver(post_save, sender=KeyPair)
def set_first_keypair_as_default(sender, instance, created, **kwargs):
    """Set first keypair as a user's default"""
    if not created:
        return

    if KeyPair.objects.filter(user=instance.user).count() == 1:
        # Set first keypair as the user default
        profile = instance.user.profile
        profile.default_keypair = instance
        profile.save()


@receiver(post_delete, sender=KeyPair)
def replace_default_keypair_on_deletion(sender, instance, **kwargs):
    """Assign a new default for the user, if the current one is deleted"""
    user = instance.user
    profile = user.profile
    remaining_keypairs = user.keypairs
    if profile.default_keypair is None and remaining_keypairs.count():
        profile.default_keypair = remaining_keypairs.first()
        profile.save()
