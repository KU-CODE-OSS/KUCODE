# Generated by Django 4.2.11 on 2024-05-14 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_student'),
        ('course', '0002_course_registration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course_registration',
            old_name='course_id',
            new_name='course',
        ),
        migrations.RemoveField(
            model_name='course_registration',
            name='numbwer',
        ),
        migrations.AddField(
            model_name='course_registration',
            name='student',
            field=models.ForeignKey(default='null', on_delete=django.db.models.deletion.CASCADE, to='account.student'),
            preserve_default=False,
        ),
    ]
