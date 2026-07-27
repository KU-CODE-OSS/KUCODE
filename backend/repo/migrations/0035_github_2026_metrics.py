# Generated manually for GitHub 2026 metrics collection.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0034_repository_pushed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='default_branch',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='repo_issue',
            name='closed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='repo_issue',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='repo_issue',
            name='issue_number',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='repo_pr',
            name='closed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='repo_pr',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='repo_pr',
            name='merged_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='repo_pr',
            name='merged_by',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='repo_pr',
            name='pr_number',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='repo_commit',
            name='committed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.CreateModel(
            name='RepositorySnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collected_at', models.DateTimeField()),
                ('default_branch', models.CharField(max_length=255, null=True)),
                ('branch_count', models.IntegerField(null=True)),
                ('language_bytes', models.JSONField(null=True)),
                ('language_percentage', models.JSONField(null=True)),
                ('workflow_yaml_count', models.IntegerField(null=True)),
                ('workflow_yaml_total_size', models.IntegerField(null=True)),
                ('workflow_yaml_paths', models.JSONField(blank=True, default=list)),
                ('has_readme', models.BooleanField(null=True)),
                ('readme_dependency_mentioned', models.BooleanField(null=True)),
                ('dependency_evidence', models.JSONField(null=True)),
                ('dependabot_config_present', models.BooleanField(null=True)),
                ('repo', models.ForeignKey(db_column='repo_id', on_delete=django.db.models.deletion.CASCADE, to='repo.repository')),
            ],
            options={
                'db_table': 'repo_repository_snapshot',
            },
        ),
        migrations.CreateModel(
            name='RepoDependabotAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_alert_number', models.IntegerField()),
                ('state', models.CharField(max_length=100, null=True)),
                ('package_name', models.CharField(max_length=500, null=True)),
                ('ecosystem', models.CharField(max_length=255, null=True)),
                ('manifest_path', models.CharField(max_length=1000, null=True)),
                ('severity', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('fixed_at', models.DateTimeField(null=True)),
                ('dismissed_at', models.DateTimeField(null=True)),
                ('collected_at', models.DateTimeField()),
                ('repo', models.ForeignKey(db_column='repo_id', on_delete=django.db.models.deletion.CASCADE, to='repo.repository')),
            ],
            options={
                'db_table': 'repo_dependabot_alert',
            },
        ),
        migrations.CreateModel(
            name='RepoReviewComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pr_id', models.CharField(max_length=255, null=True)),
                ('pr_number', models.IntegerField(null=True)),
                ('comment_id', models.CharField(max_length=255)),
                ('author_github_id', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('path', models.CharField(max_length=1000, null=True)),
                ('position', models.IntegerField(null=True)),
                ('comment_type', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=100, null=True)),
                ('repo', models.ForeignKey(db_column='repo_id', on_delete=django.db.models.deletion.CASCADE, to='repo.repository')),
            ],
            options={
                'db_table': 'repo_review_comment',
            },
        ),
        migrations.CreateModel(
            name='RepoCommitFileChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha', models.CharField(max_length=255)),
                ('committed_at', models.DateTimeField(null=True)),
                ('path', models.CharField(max_length=1000)),
                ('filename', models.CharField(max_length=255, null=True)),
                ('extension', models.CharField(max_length=50, null=True)),
                ('status', models.CharField(max_length=100, null=True)),
                ('additions', models.IntegerField(null=True)),
                ('deletions', models.IntegerField(null=True)),
                ('changes', models.IntegerField(null=True)),
                ('is_workflow_yaml', models.BooleanField(default=False)),
                ('is_test_file', models.BooleanField(default=False)),
                ('is_readme', models.BooleanField(default=False)),
                ('is_dependency_manifest', models.BooleanField(default=False)),
                ('repo', models.ForeignKey(db_column='repo_id', on_delete=django.db.models.deletion.CASCADE, to='repo.repository')),
            ],
            options={
                'db_table': 'repo_commit_file_change',
            },
        ),
        migrations.AddIndex(
            model_name='repositorysnapshot',
            index=models.Index(fields=['repo', 'collected_at'], name='repo_reposi_repo_id_4bb457_idx'),
        ),
        migrations.AddIndex(
            model_name='repodependabotalert',
            index=models.Index(fields=['repo', 'state'], name='repo_depend_repo_id_1abc71_idx'),
        ),
        migrations.AddIndex(
            model_name='repodependabotalert',
            index=models.Index(fields=['repo', 'severity'], name='repo_depend_repo_id_46050d_idx'),
        ),
        migrations.AddIndex(
            model_name='reporeviewcomment',
            index=models.Index(fields=['repo', 'pr_number'], name='repo_review_repo_id_fa64c0_idx'),
        ),
        migrations.AddIndex(
            model_name='reporeviewcomment',
            index=models.Index(fields=['repo', 'created_at'], name='repo_review_repo_id_fabf73_idx'),
        ),
        migrations.AddIndex(
            model_name='repocommitfilechange',
            index=models.Index(fields=['repo', 'committed_at'], name='repo_commit_repo_id_bf52f4_idx'),
        ),
        migrations.AddIndex(
            model_name='repocommitfilechange',
            index=models.Index(fields=['repo', 'path'], name='repo_commit_repo_id_77b5ec_idx'),
        ),
        migrations.AddConstraint(
            model_name='repodependabotalert',
            constraint=models.UniqueConstraint(fields=('repo', 'github_alert_number'), name='unique_repo_dependabot_alert'),
        ),
        migrations.AddConstraint(
            model_name='reporeviewcomment',
            constraint=models.UniqueConstraint(fields=('comment_type', 'comment_id'), name='unique_repo_review_comment'),
        ),
        migrations.AddConstraint(
            model_name='repocommitfilechange',
            constraint=models.UniqueConstraint(fields=('repo', 'sha', 'path'), name='unique_repo_commit_file_change'),
        ),
    ]
