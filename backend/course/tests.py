import json
from io import StringIO

from django.core.management import call_command
from django.test import RequestFactory, TestCase

from course.api.views import course_project_update
from course.models import Course, Course_project
from course.services import (
    reconcile_repository_course_categories,
    repositories_matching_course_name,
)
from repo.models import Repository


class RepositoryCourseCategoryTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.course = Course.objects.create(
            course_id="COSE474-00",
            year=2026,
            semester=1,
            name="딥러닝(영강)",
            prof="Professor",
            course_repo_name="261RCOSE47400",
        )

    def create_repository(self, repository_id, name, **kwargs):
        return Repository.objects.create(
            id=repository_id,
            name=name,
            owner_github_id=f"owner-{repository_id}",
            **kwargs,
        )

    def test_discovery_uses_complete_case_insensitive_contiguous_token(self):
        exact = self.create_repository("exact", "261RCOSE47400")
        prefixed = self.create_repository("prefixed", "20261RCOSE47400")
        mixed_case = self.create_repository("mixed", "team-261rcose47400-project")
        self.create_repository("generic", "team-COSE47400-project")
        self.create_repository("reordered", "COSE47400-261R")

        matched_ids = set(
            repositories_matching_course_name(self.course).values_list("id", flat=True)
        )

        self.assertEqual(matched_ids, {exact.id, prefixed.id, mixed_case.id})

    def test_course_project_update_creates_links_and_cached_categories(self):
        matching = self.create_repository("matching", "20261RCOSE47400")
        non_matching = self.create_repository("non-matching", "personal-COSE-project")

        response = course_project_update(self.factory.get("/course/course_project_update"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(
            Course_project.objects.filter(course=self.course, repo=matching).exists()
        )
        self.assertFalse(
            Course_project.objects.filter(course=self.course, repo=non_matching).exists()
        )
        matching.refresh_from_db()
        non_matching.refresh_from_db()
        self.assertIs(matching.is_course, True)
        self.assertEqual(matching.category, self.course.name)
        self.assertIs(non_matching.is_course, False)
        self.assertEqual(non_matching.category, "-")

        response_data = json.loads(response.content)
        self.assertEqual(response_data["category_sync"]["course_repository_count"], 1)

    def test_saved_course_project_remains_authoritative_after_repo_rename(self):
        repository = self.create_repository(
            "renamed",
            "CPU_scheduler",
            is_course=False,
            category="-",
        )
        Course_project.objects.create(
            course=self.course,
            course_year=self.course.year,
            course_semester=self.course.semester,
            repo=repository,
            repo_name="261RCOSE47400",
        )

        result = reconcile_repository_course_categories()

        repository.refresh_from_db()
        self.assertIs(repository.is_course, True)
        self.assertEqual(repository.category, self.course.name)
        self.assertEqual(result["changed_repository_count"], 1)

    def test_reconciliation_is_idempotent(self):
        repository = self.create_repository("course-repo", "261RCOSE47400")
        Course_project.objects.create(
            course=self.course,
            course_year=self.course.year,
            course_semester=self.course.semester,
            repo=repository,
            repo_name=repository.name,
        )

        first_result = reconcile_repository_course_categories()
        second_result = reconcile_repository_course_categories()

        self.assertEqual(first_result["changed_repository_count"], 1)
        self.assertEqual(second_result["changed_repository_count"], 0)

    def test_sync_repo_categories_management_command(self):
        repository = self.create_repository("command-repo", "renamed-repository")
        Course_project.objects.create(
            course=self.course,
            course_year=self.course.year,
            course_semester=self.course.semester,
            repo=repository,
            repo_name="261RCOSE47400",
        )
        output = StringIO()

        call_command("sync_repo_categories", stdout=output)

        repository.refresh_from_db()
        self.assertIs(repository.is_course, True)
        self.assertEqual(repository.category, self.course.name)
        self.assertIn("1 changed", output.getvalue())
