# Generated by Django 4.2.11 on 2024-05-10 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_github_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
    ]
