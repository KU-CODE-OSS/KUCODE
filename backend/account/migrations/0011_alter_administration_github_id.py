# Generated by Django 4.2.11 on 2024-07-16 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_administration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administration',
            name='github_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
