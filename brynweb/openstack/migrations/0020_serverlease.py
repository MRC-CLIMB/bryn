# Generated by Django 3.1.1 on 2021-03-10 12:00

from django.db import migrations, models
import django.db.models.deletion
import openstack.models


class Migration(migrations.Migration):

    dependencies = [
        ("userdb", "0031_licenceacceptance_licenceversion"),
        ("openstack", "0019_regionsettings_max_volume_size_gb"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServerLease",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("server_id", models.UUIDField(editable=False, unique=True)),
                ("server_name", models.CharField(editable=False, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_renewed_at", models.DateTimeField(auto_now=True)),
                (
                    "expiry",
                    models.DateTimeField(
                        blank=True,
                        default=openstack.models.get_default_server_lease_expiry,
                        null=True,
                    ),
                ),
                (
                    "renewal_count",
                    models.PositiveIntegerField(default=0, editable=False),
                ),
                (
                    "assigned_teammember",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="server_leases",
                        to="userdb.teammember",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="server_leases",
                        to="openstack.tenant",
                    ),
                ),
            ],
        ),
    ]