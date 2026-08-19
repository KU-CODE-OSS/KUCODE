import json

from django.test import RequestFactory, TestCase
from django.utils import timezone

from account.models import Student
from course.models import Course
from scoring.api.views import course_ranking
from scoring.models import (
    ScoringParameterSet,
    ScoringRun,
    StudentCourseScore,
)


class CourseRankingApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.course = Course.objects.create(
            course_id="TEST101",
            year=2026,
            semester=1,
            name="Test Course",
            prof="Professor",
        )
        self.student = Student.objects.create(
            id="student-1",
            name="Student One",
            github_id="student-one",
            department="Software",
        )
        parameters = ScoringParameterSet.objects.create(course=self.course)
        self.old_run = ScoringRun.objects.create(
            course=self.course,
            parameter_set=parameters,
            status=ScoringRun.Status.COMPLETED,
            completed_at=timezone.now(),
            is_canonical=False,
        )
        self.canonical_run = ScoringRun.objects.create(
            course=self.course,
            parameter_set=parameters,
            status=ScoringRun.Status.COMPLETED,
            completed_at=timezone.now(),
            is_canonical=True,
        )
        StudentCourseScore.objects.create(
            run=self.old_run,
            student=self.student,
            overall_score=12,
        )
        StudentCourseScore.objects.create(
            run=self.canonical_run,
            student=self.student,
            overall_score=84.25,
            productivity_score=80,
            collaboration_score=70,
            problem_solving_score=60,
            component_details={
                "project_average": 80.31,
                "collaboration_stability": 100,
                "contributed_repository_count": 2,
                "owned_repository_count": 1,
                "representative_repository_count": 1,
            },
        )

    def test_returns_only_canonical_course_scores(self):
        response = course_ranking(self.factory.get("/api/scoring/course-ranking"))

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["run_id"], self.canonical_run.id)
        self.assertEqual(payload[0]["students"][0]["overall_score"], 84.25)
        self.assertEqual(
            payload[0]["students"][0]["contributed_repository_count"],
            2,
        )

    def test_supports_course_filters(self):
        response = course_ranking(
            self.factory.get(
                "/api/scoring/course-ranking",
                {"year": 2025, "semester": 1},
            )
        )

        self.assertEqual(json.loads(response.content), [])

    def test_rejects_invalid_integer_filter(self):
        response = course_ranking(
            self.factory.get("/api/scoring/course-ranking", {"year": "invalid"})
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_non_get_requests(self):
        response = course_ranking(self.factory.post("/api/scoring/course-ranking"))

        self.assertEqual(response.status_code, 405)
