# Generated by Django 4.2.11 on 2024-09-11 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0024_repository_closed_pr_count_repository_open_pr_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='contributors',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]
