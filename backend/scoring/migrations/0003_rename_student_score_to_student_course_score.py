from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("scoring", "0002_canonical_runs_and_student_aptitude"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="StudentScore",
            new_name="StudentCourseScore",
        ),
        migrations.AlterField(
            model_name="studentcoursescore",
            name="run",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_course_scores",
                to="scoring.scoringrun",
            ),
        ),
        migrations.RenameIndex(
            model_name="studentcoursescore",
            old_name="scoring_stu_student_4c9555_idx",
            new_name="scoring_stu_student_b962cb_idx",
        ),
    ]
