"""Reconcile cached repository course categories from Course_project rows.

Usage (inside the backend container):
    python manage.py sync_repo_categories

This command reads existing Course_project relationships and does not contact
GitHub or create/delete Course_project rows.
"""

from django.core.management.base import BaseCommand

from course.services import reconcile_repository_course_categories


class Command(BaseCommand):
    help = "Refresh Repository.is_course and category from Course_project relationships."

    def handle(self, *args, **options):
        result = reconcile_repository_course_categories()
        self.stdout.write(
            self.style.SUCCESS(
                "Repository category synchronization completed: "
                f"{result['changed_repository_count']} changed, "
                f"{result['course_repository_count']} course, "
                f"{result['non_course_repository_count']} non-course, "
                f"{result['multiple_course_repository_count']} linked to multiple courses."
            )
        )
