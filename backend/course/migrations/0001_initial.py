# Generated by Django 4.2.11 on 2024-05-13 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.CharField(max_length=20)),
                ('year', models.IntegerField()),
                ('semester', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('prof', models.CharField(max_length=100)),
                ('ta', models.CharField(blank=True, max_length=100, null=True)),
                ('student_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.UniqueConstraint(fields=('course_id', 'year', 'semester'), name='unique_course'),
        ),
    ]
