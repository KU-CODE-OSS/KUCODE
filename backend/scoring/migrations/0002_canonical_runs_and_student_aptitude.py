from django.db import migrations, models
import django.db.models.deletion


def mark_latest_completed_runs_canonical(apps, schema_editor):
    ScoringRun = apps.get_model("scoring", "ScoringRun")
    course_formula_pairs = ScoringRun.objects.values_list(
        "course_id", "formula_version"
    ).distinct()
    for course_id, formula_version in course_formula_pairs.iterator():
        latest = (
            ScoringRun.objects.filter(
                course_id=course_id,
                formula_version=formula_version,
                status="completed",
            )
            .order_by("-completed_at", "-started_at", "-id")
            .first()
        )
        if latest is not None:
            ScoringRun.objects.filter(pk=latest.pk).update(
                is_canonical=True,
                canonicalized_at=latest.completed_at or latest.started_at,
            )


def clear_canonical_runs(apps, schema_editor):
    ScoringRun = apps.get_model("scoring", "ScoringRun")
    ScoringRun.objects.update(is_canonical=False, canonicalized_at=None)


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0017_rename_introduction_student_account_introduction"),
        ("scoring", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="scoringrun",
            name="canonicalized_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scoringrun",
            name="is_canonical",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_latest_completed_runs_canonical, clear_canonical_runs),
        migrations.AddConstraint(
            model_name="scoringrun",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_canonical", True)),
                fields=("course", "formula_version"),
                name="unique_canonical_course_formula_run",
            ),
        ),
        migrations.CreateModel(
            name="StudentAptitudeScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("formula_version", models.CharField(default="prototype-v1", max_length=50)),
                ("overall_score", models.FloatField(default=0)),
                ("productivity_score", models.FloatField(null=True)),
                ("collaboration_score", models.FloatField(null=True)),
                ("problem_solving_score", models.FloatField(null=True)),
                ("project_count", models.PositiveIntegerField(default=0)),
                ("course_count", models.PositiveIntegerField(default=0)),
                ("source_run_ids", models.JSONField(blank=True, default=list)),
                ("component_details", models.JSONField(blank=True, default=dict)),
                ("warnings", models.JSONField(blank=True, default=list)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aptitude_scores",
                        to="account.student",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="studentaptitudescore",
            constraint=models.UniqueConstraint(
                fields=("student", "formula_version"),
                name="unique_student_aptitude_formula",
            ),
        ),
    ]
