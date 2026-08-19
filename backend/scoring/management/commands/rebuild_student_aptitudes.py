"""Rebuild EProfile aptitude aggregates without rescoring repositories.

Usage (inside the backend container):
    python manage.py rebuild_student_aptitudes
    python manage.py rebuild_student_aptitudes --formula-version prototype-v1

Use this after backfilling/migrating scoring data or repairing aptitude rows.
Normal score_course and score_all_courses runs refresh aptitude automatically.
"""

from django.core.management.base import BaseCommand

from scoring.models import FORMULA_VERSION
from scoring.services.pipeline import rebuild_all_student_aptitudes


class Command(BaseCommand):
    help = "Rebuild current EProfile aptitude scores from canonical course runs."

    def add_arguments(self, parser):
        parser.add_argument("--formula-version", default=FORMULA_VERSION)

    def handle(self, *args, **options):
        scores = rebuild_all_student_aptitudes(options["formula_version"])
        self.stdout.write(
            self.style.SUCCESS(f"Rebuilt {len(scores)} student aptitude scores.")
        )
