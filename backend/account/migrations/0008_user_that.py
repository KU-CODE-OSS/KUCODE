# Generated by Django 4.2.11 on 2024-07-10 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_user_hello'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='that',
            field=models.CharField(default='null', max_length=255),
        ),
    ]
