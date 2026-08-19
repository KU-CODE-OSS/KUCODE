from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from course.models import Course, Course_project
from repo.models import Repository


class ScoreAllCoursesCommandTests(TestCase):
    def setUp(self):
        self.first_course = Course.objects.create(
            course_id="TEST101",
            year=2025,
            semester=2,
            name="First Test Course",
            prof="Professor",
        )
        self.second_course = Course.objects.create(
            course_id="TEST201",
            year=2026,
            semester=1,
            name="Second Test Course",
            prof="Professor",
        )
        Course.objects.create(
            course_id="EMPTY101",
            year=2026,
            semester=1,
            name="Course Without Repositories",
            prof="Professor",
        )
        for index, course in enumerate([self.first_course, self.second_course], 1):
            repository = Repository.objects.create(
                id=f"repo-{index}",
                name=f"repository-{index}",
                owner_github_id="student-one",
            )
            Course_project.objects.create(
                course=course,
                course_year=course.year,
                course_semester=course.semester,
                repo=repository,
                repo_name=repository.name,
            )

    @patch("scoring.management.commands.score_all_courses.run_course_scoring")
    def test_scores_only_courses_with_repositories_in_stable_order(self, score_course):
        score_course.side_effect = [SimpleNamespace(id=11), SimpleNamespace(id=12)]
        stdout = StringIO()

        call_command("score_all_courses", stdout=stdout)

        self.assertEqual(score_course.call_count, 2)
        scored_courses = [call.args[0] for call in score_course.call_args_list]
        self.assertEqual(scored_courses, [self.first_course, self.second_course])
        self.assertIn("Finished: 2 succeeded, 0 failed.", stdout.getvalue())

    @patch("scoring.management.commands.score_all_courses.run_course_scoring")
    def test_year_filter_limits_courses(self, score_course):
        score_course.return_value = SimpleNamespace(id=21)

        call_command("score_all_courses", year=2026, stdout=StringIO())

        score_course.assert_called_once_with(self.second_course)

    @patch("scoring.management.commands.score_all_courses.run_course_scoring")
    def test_continues_after_failure_and_returns_command_error(self, score_course):
        score_course.side_effect = [ValueError("broken course"), SimpleNamespace(id=22)]

        with self.assertRaises(CommandError):
            call_command(
                "score_all_courses",
                stdout=StringIO(),
                stderr=StringIO(),
            )

        self.assertEqual(score_course.call_count, 2)
