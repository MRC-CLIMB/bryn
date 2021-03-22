# Generated by Django 3.1.1 on 2021-03-22 13:27

from django.db import migrations, models
import userdb.models


class Migration(migrations.Migration):

    dependencies = [
        ("userdb", "0031_licenceacceptance_licenceversion"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="licence_expiry",
            field=models.DateTimeField(default=userdb.models.licence_expiry_default),
        ),
        migrations.AddField(
            model_name="team",
            name="licence_last_reminder_sent_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
