import json

from django.test import RequestFactory, TestCase
from django.utils import timezone

from account.models import Student
from login.models import Member, Student as LoginStudent
from course.models import Course
from scoring.api.views import course_ranking, student_aptitude
from scoring.models import (
    ScoringParameterSet,
    ScoringRun,
    StudentAptitudeScore,
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


class StudentAptitudeApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.student = Student.objects.create(
            id="student-1",
            name="Student One",
            github_id="student-one",
        )
        self.score = StudentAptitudeScore.objects.create(
            student=self.student,
            overall_score=81.5,
            productivity_score=80,
            collaboration_score=75,
            problem_solving_score=70,
            project_count=3,
            course_count=2,
            source_run_ids=[2, 4],
            component_details={
                "project_average": 78.25,
                "collaboration_stability": 94.5,
                "owned_repository_count": 2,
                "aggregation_scope": "canonical_course_runs_only",
                "growth_included": False,
            },
        )
        self.member = Member.objects.create(
            id="firebase-uuid",
            name="Student One",
            email="student@example.com",
        )
        LoginStudent.objects.create(member=self.member, id=self.student.pk)

    def test_returns_current_student_aptitude(self):
        response = student_aptitude(
            self.factory.get(
                "/api/scoring/student-aptitude",
                {"student_id": self.student.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload["available"])
        self.assertEqual(payload["overall_score"], 81.5)
        self.assertEqual(payload["project_count"], 3)
        self.assertFalse(payload["growth_included"])

    def test_returns_unavailable_for_unscored_student(self):
        unscored = Student.objects.create(id="student-2", name="Student Two")

        response = student_aptitude(
            self.factory.get(
                "/api/scoring/student-aptitude",
                {"student_id": unscored.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.loads(response.content)["available"])

    def test_resolves_logged_in_student_uuid(self):
        response = student_aptitude(
            self.factory.get(
                "/api/scoring/student-aptitude",
                {"uuid": self.member.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["student_id"], self.student.pk)

    def test_requires_student_identifier(self):
        response = student_aptitude(
            self.factory.get("/api/scoring/student-aptitude")
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_non_get_requests(self):
        response = student_aptitude(
            self.factory.post("/api/scoring/student-aptitude")
        )

        self.assertEqual(response.status_code, 405)
