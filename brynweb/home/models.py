from django.db import models
from django.contrib.auth import get_user_model
from tinymce import models as tinymce_models

User = get_user_model()


class Announcement(models.Model):
    class Category(models.TextChoices):
        SERVICE_OUTAGE = "SE"
        SERVICE_RESTORED = "SR"
        SERIVCE_INFO = "SI"
        NEWS = "NS"

    category = models.CharField(
        max_length=2, choices=Category.choices, default=Category.NEWS
    )
    author = models.ForeignKey(
        User, editable=False, null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=255)
    content = tinymce_models.HTMLField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    expiry = models.DateTimeField(null=True, blank=True)


class FrequentlyAskedQuestion(models.Model):
    class Category(models.TextChoices):
        SERVERS = "SV"
        VOLUMES = "VL"
        KEYPAIRS = "KP"

    category = models.CharField(
        max_length=2, choices=Category.choices, default=Category.SERVERS
    )
    author = models.ForeignKey(
        User, editable=False, null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=255)
    content = tinymce_models.HTMLField()
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
