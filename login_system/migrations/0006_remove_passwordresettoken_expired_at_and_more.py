# Generated by Django 4.1.7 on 2023-04-11 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("login_system", "0005_passwordresettoken"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="passwordresettoken",
            name="expired_at",
        ),
        migrations.AlterField(
            model_name="passwordresettoken",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="passwordresettoken",
            name="token",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
