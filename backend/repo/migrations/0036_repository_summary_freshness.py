from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('repo', '0035_github_2026_metrics'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='summary_generated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='summary_source_fingerprint',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='summary_source_kind',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='summary_last_attempt_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='summary_last_error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='github_availability',
            field=models.CharField(default='unknown', max_length=20),
        ),
    ]
