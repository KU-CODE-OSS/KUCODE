"""Score one course-semester from the latest crawled database data.

Usage (inside the backend container):
    python manage.py score_course --course-id COSE341-01 --year 2026 --semester 1

Use this after crawling one affected course. A successful run becomes that
course-semester's canonical run and refreshes the affected aptitude scores.
"""

from django.core.management.base import BaseCommand, CommandError

from course.models import Course
from scoring.services.pipeline import run_course_scoring


class Command(BaseCommand):
    help = "Calculate and save prototype-v1 scores for one course and semester."

    def add_arguments(self, parser):
        parser.add_argument("--course-id", required=True)
        parser.add_argument("--year", required=True, type=int)
        parser.add_argument("--semester", required=True, type=int)

    def handle(self, *args, **options):
        try:
            course = Course.objects.get(
                course_id=options["course_id"],
                year=options["year"],
                semester=options["semester"],
            )
        except Course.DoesNotExist as exc:
            raise CommandError("The requested course/year/semester was not found.") from exc

        self.stdout.write(
            f"Scoring {course.course_id} ({course.year}-{course.semester}) with prototype-v1..."
        )
        try:
            run = run_course_scoring(course)
        except Exception as exc:
            raise CommandError(f"Scoring failed: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Scoring run {run.id} completed: "
                f"{run.summary.get('repository_score_count', 0)} repositories, "
                f"{run.summary.get('student_course_score_count', 0)} students."
            )
        )
