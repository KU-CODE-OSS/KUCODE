# Generated by Django 4.2.11 on 2024-07-10 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_student_college_alter_student_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hello',
            field=models.CharField(default='null', max_length=255),
        ),
    ]