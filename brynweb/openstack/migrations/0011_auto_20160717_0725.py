# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 07:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openstack", "0010_regionsettings_floating_ip_pool"),
    ]

    operations = [
        migrations.AlterField(
            model_name="regionsettings",
            name="floating_ip_pool",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
