# Generated by Django 4.1.7 on 2023-04-10 06:51

import django.contrib.auth.models
from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):
    dependencies = [
        ("login_system", "0002_doctor"),
    ]

    operations = [
        migrations.CreateModel(
            name="Nurse",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("login_system.user",),
            managers=[
                ("nurse", django.db.models.manager.Manager()),
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
