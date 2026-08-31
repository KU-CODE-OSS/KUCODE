"""Score all courses with repositories, optionally limited by filters.

Usage (inside the backend container):
    python manage.py score_all_courses
    python manage.py score_all_courses --year 2026 --semester 1
    python manage.py score_all_courses --course-id COSE341-01
    python manage.py score_all_courses --stop-on-error

Use this for a manual full or filtered refresh. By default, failures are
reported after the remaining matching courses have been attempted.
"""

from django.core.management.base import BaseCommand, CommandError

from course.models import Course, Course_project
from scoring.services.pipeline import run_course_scoring


class Command(BaseCommand):
    help = "Score every course that has at least one repository."

    def add_arguments(self, parser):
        parser.add_argument("--course-id")
        parser.add_argument("--year", type=int)
        parser.add_argument("--semester", type=int)
        parser.add_argument(
            "--stop-on-error",
            action="store_true",
            help="Stop immediately when one course fails instead of continuing.",
        )

    def handle(self, *args, **options):
        course_pks_with_repositories = (
            Course_project.objects.exclude(repo_id__isnull=True)
            .values_list("course_id", flat=True)
            .distinct()
        )
        courses = Course.objects.filter(pk__in=course_pks_with_repositories)
        if options["course_id"]:
            courses = courses.filter(course_id=options["course_id"])
        if options["year"] is not None:
            courses = courses.filter(year=options["year"])
        if options["semester"] is not None:
            courses = courses.filter(semester=options["semester"])
        courses = list(courses.order_by("year", "semester", "course_id", "pk"))

        if not courses:
            self.stdout.write(self.style.WARNING("No matching courses with repositories found."))
            return

        completed = []
        failures = []
        for index, course in enumerate(courses, 1):
            label = f"{course.course_id} ({course.year}-{course.semester})"
            self.stdout.write(f"[{index}/{len(courses)}] Scoring {label}...")
            try:
                run = run_course_scoring(course)
            except Exception as exc:
                failures.append((label, str(exc)))
                self.stderr.write(self.style.ERROR(f"Failed {label}: {exc}"))
                if options["stop_on_error"]:
                    raise CommandError(f"Stopped after failure in {label}.") from exc
                continue

            completed.append((label, run.id))
            self.stdout.write(
                self.style.SUCCESS(f"Completed {label}: canonical run {run.id}.")
            )

        self.stdout.write(
            f"Finished: {len(completed)} succeeded, {len(failures)} failed."
        )
        if failures:
            failed_labels = ", ".join(label for label, _ in failures)
            raise CommandError(f"Some courses failed: {failed_labels}")
