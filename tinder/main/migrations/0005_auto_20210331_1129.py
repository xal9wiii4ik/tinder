# Generated by Django 3.1.7 on 2021-03-31 11:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_auto_20210331_1121'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CanMessage',
            new_name='Like',
        ),
    ]
