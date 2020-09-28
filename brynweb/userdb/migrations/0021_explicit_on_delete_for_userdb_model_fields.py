# Generated by Django 3.1.1 on 2020-09-28 12:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("userdb", "0020_region_disable_new_instances"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="creator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="default_region",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="userdb.region",
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(
                help_text="e.g. Bacterial pathogenomics group",
                max_length=50,
                verbose_name="Group or team name",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="current_region",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="userdb.region",
            ),
        ),
    ]
