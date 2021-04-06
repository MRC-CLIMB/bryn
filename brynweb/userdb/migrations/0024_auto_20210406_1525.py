# Generated by Django 3.1.1 on 2021-04-06 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userdb", "0023_auto_20210330_1503"),
    ]

    operations = [
        migrations.RenameField(
            model_name="region",
            old_name="disable_new_instances",
            new_name="new_instances_disabled",
        ),
        migrations.AddField(
            model_name="region",
            name="unshelving_disabled",
            field=models.BooleanField(default=False),
        ),
    ]
