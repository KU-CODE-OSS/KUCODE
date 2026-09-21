from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0017_rename_introduction_student_account_introduction'),
        ('repo', '0036_repository_summary_freshness'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentRepositoryTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=30)),
                ('normalized_tag', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_tags', to='repo.repository')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repository_tags', to='account.student')),
            ],
            options={
                'db_table': 'repo_student_repository_tag',
                'ordering': ['created_at', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='studentrepositorytag',
            constraint=models.UniqueConstraint(fields=('student', 'repository', 'normalized_tag'), name='unique_student_repository_tag'),
        ),
    ]
