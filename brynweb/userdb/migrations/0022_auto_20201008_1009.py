# Generated by Django 3.1.1 on 2020-10-08 10:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("userdb", "0021_explicit_on_delete_for_userdb_model_fks"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="users",
            field=models.ManyToManyField(
                related_name="teams",
                through="userdb.TeamMember",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="accepted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.UniqueConstraint(
                fields=("to_team", "email"), name="unique_invitation"
            ),
        ),
    ]