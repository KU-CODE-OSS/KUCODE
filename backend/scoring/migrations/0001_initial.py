# Generated manually for the prototype scoring pipeline.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("account", "0017_rename_introduction_student_account_introduction"),
        ("course", "0015_course_course_repo_name"),
        ("repo", "0035_github_2026_metrics"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScoringParameterSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("formula_version", models.CharField(default="prototype-v1", max_length=50)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("frozen", "Frozen")], default="draft", max_length=20)),
                ("commit_p95", models.FloatField(default=0)),
                ("changed_lines_p95", models.FloatField(default=0)),
                ("pr_weighted_p95", models.FloatField(default=0)),
                ("churn_mean", models.FloatField(default=0.2)),
                ("churn_stddev", models.FloatField(default=0.15)),
                ("issue_resolution_median_days", models.FloatField(null=True)),
                ("values", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("frozen_at", models.DateTimeField(blank=True, null=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="course.course")),
            ],
        ),
        migrations.CreateModel(
            name="ScoringRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("formula_version", models.CharField(default="prototype-v1", max_length=50)),
                ("trigger", models.CharField(choices=[("manual", "Manual"), ("crawl", "Crawl"), ("scheduled", "Scheduled")], default="manual", max_length=20)),
                ("status", models.CharField(choices=[("running", "Running"), ("completed", "Completed"), ("partial", "Partial"), ("failed", "Failed")], default="running", max_length=20)),
                ("affected_repository_ids", models.JSONField(blank=True, default=list)),
                ("summary", models.JSONField(blank=True, default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="course.course")),
                ("parameter_set", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="scoring.scoringparameterset")),
            ],
        ),
        migrations.CreateModel(
            name="RepositoryScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("raw_metrics", models.JSONField(default=dict)),
                ("component_details", models.JSONField(default=dict)),
                ("productivity_score", models.FloatField()),
                ("collaboration_score", models.FloatField()),
                ("problem_solving_score", models.FloatField(null=True)),
                ("difficulty_multiplier", models.FloatField(default=1.0)),
                ("final_score", models.FloatField()),
                ("warnings", models.JSONField(blank=True, default=list)),
                ("repository", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="repo.repository")),
                ("run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="repository_scores", to="scoring.scoringrun")),
            ],
        ),
        migrations.CreateModel(
            name="StudentRepositoryScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("github_username", models.CharField(max_length=255)),
                ("contribution_share", models.FloatField(default=0)),
                ("team_size", models.PositiveIntegerField(default=1)),
                ("personal_multiplier", models.FloatField(default=0)),
                ("personal_project_score", models.FloatField(default=0)),
                ("productivity_score", models.FloatField(default=0)),
                ("collaboration_score", models.FloatField(default=0)),
                ("problem_solving_score", models.FloatField(null=True)),
                ("activity_score", models.FloatField(default=0)),
                ("representative_eligible", models.BooleanField(default=False)),
                ("representative_rank", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("repository_score", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="scoring.repositoryscore")),
                ("run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_repository_scores", to="scoring.scoringrun")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="account.student")),
            ],
        ),
        migrations.CreateModel(
            name="StudentScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("overall_score", models.FloatField(default=0)),
                ("productivity_score", models.FloatField(null=True)),
                ("collaboration_score", models.FloatField(null=True)),
                ("problem_solving_score", models.FloatField(null=True)),
                ("representative_repository_ids", models.JSONField(blank=True, default=list)),
                ("component_details", models.JSONField(blank=True, default=dict)),
                ("warnings", models.JSONField(blank=True, default=list)),
                ("run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_scores", to="scoring.scoringrun")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="account.student")),
            ],
        ),
        migrations.AddIndex(
            model_name="scoringparameterset",
            index=models.Index(fields=["course", "formula_version", "status"], name="scoring_sco_course__203a1c_idx"),
        ),
        migrations.AddIndex(
            model_name="scoringrun",
            index=models.Index(fields=["course", "-started_at"], name="scoring_sco_course__89655f_idx"),
        ),
        migrations.AddIndex(
            model_name="repositoryscore",
            index=models.Index(fields=["repository", "-id"], name="scoring_rep_reposit_5cc48a_idx"),
        ),
        migrations.AddIndex(
            model_name="studentrepositoryscore",
            index=models.Index(fields=["student", "run"], name="scoring_stu_student_bb3d01_idx"),
        ),
        migrations.AddIndex(
            model_name="studentscore",
            index=models.Index(fields=["student", "-id"], name="scoring_stu_student_4c9555_idx"),
        ),
        migrations.AddConstraint(
            model_name="repositoryscore",
            constraint=models.UniqueConstraint(fields=("run", "repository"), name="unique_run_repository_score"),
        ),
        migrations.AddConstraint(
            model_name="studentrepositoryscore",
            constraint=models.UniqueConstraint(fields=("run", "repository_score", "student"), name="unique_run_repository_student_score"),
        ),
        migrations.AddConstraint(
            model_name="studentscore",
            constraint=models.UniqueConstraint(fields=("run", "student"), name="unique_run_student_score"),
        ),
    ]
