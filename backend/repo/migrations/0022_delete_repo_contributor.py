# Generated by Django 4.2.11 on 2024-05-27 04:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0021_repo_contributor_unique_repo_contributor'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Repo_contributor',
        ),
    ]
