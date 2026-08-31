from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from account.models import Student
from course.models import Course, Course_project, Course_registration
from repo.models import (
    Repo_commit,
    Repo_contributor,
    Repo_issue,
    Repo_pr,
    Repository,
    RepositorySnapshot,
)
from scoring.models import (
    RepositoryScore,
    ScoringParameterSet,
    ScoringRun,
    StudentAptitudeScore,
    StudentCourseScore,
    StudentRepositoryScore,
)
from scoring.services.pipeline import run_course_scoring


class CourseScoringPipelineTests(TestCase):
    def setUp(self):
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
        )
        Course_registration.objects.create(
            course=self.course,
            course_year=2026,
            course_semester=1,
            student=self.student,
        )
        self.repository = Repository.objects.create(
            id="repo-1",
            name="course-project",
            url="https://github.com/student-one/course-project",
            owner_github_id="student-one",
            language_bytes={"Python": 750, "JavaScript": 250},
        )
        Course_project.objects.create(
            course=self.course,
            course_year=2026,
            course_semester=1,
            repo=self.repository,
            repo_name=self.repository.name,
        )
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="student-one",
            contribution_count=5,
        )
        now = timezone.now()
        for index in range(5):
            Repo_commit.objects.create(
                sha=f"sha-{index}",
                repo=self.repository,
                repo_url=self.repository.url,
                owner_github_id="student-one",
                author_github_id="student-one",
                added_lines=20,
                deleted_lines=5,
                committed_at=now - timedelta(days=5 - index),
                last_update=(now - timedelta(days=5 - index)).isoformat(),
            )
        Repo_issue.objects.create(
            id="issue-1",
            repo=self.repository,
            issue_number=1,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            state="closed",
            title="Issue",
            publisher_github_id="student-one",
            created_at=now - timedelta(days=3),
            closed_at=now - timedelta(days=1),
        )
        for index in range(3):
            Repo_pr.objects.create(
                id=f"pr-{index}",
                repo=self.repository,
                pr_number=index + 1,
                repo_url=self.repository.url,
                owner_github_id="student-one",
                title=f"PR {index}",
                requester_id="student-one",
                created_at=now - timedelta(days=3),
                closed_at=now - timedelta(days=1),
                merged_at=now - timedelta(days=1) if index < 2 else None,
                state="closed",
            )
        RepositorySnapshot.objects.create(
            repo=self.repository,
            collected_at=now,
            default_branch="main",
            workflow_yaml_count=1,
            language_bytes=self.repository.language_bytes,
            language_percentage={"Python": 75, "JavaScript": 25},
        )

    def test_run_persists_versioned_repository_and_student_course_scores(self):
        run = run_course_scoring(self.course)

        self.assertEqual(run.status, ScoringRun.Status.COMPLETED)
        self.assertTrue(run.is_canonical)
        self.assertEqual(ScoringParameterSet.objects.count(), 1)
        self.assertEqual(RepositoryScore.objects.filter(run=run).count(), 1)
        self.assertEqual(StudentRepositoryScore.objects.filter(run=run).count(), 1)
        self.assertEqual(StudentCourseScore.objects.filter(run=run).count(), 1)
        self.assertEqual(StudentAptitudeScore.objects.count(), 1)

        repository_score = RepositoryScore.objects.get(run=run)
        self.assertAlmostEqual(repository_score.difficulty_multiplier, 1.15)
        self.assertGreater(repository_score.final_score, 0)

        personal_score = StudentRepositoryScore.objects.get(run=run)
        self.assertTrue(personal_score.representative_eligible)
        self.assertEqual(personal_score.representative_rank, 1)
        self.assertEqual(personal_score.personal_multiplier, 1.0)

        student_course_score = StudentCourseScore.objects.get(run=run)
        self.assertEqual(
            student_course_score.representative_repository_ids,
            [self.repository.id],
        )
        self.assertIsNotNone(student_course_score.productivity_score)

        aptitude = StudentAptitudeScore.objects.get(student=self.student)
        self.assertEqual(aptitude.project_count, 1)
        self.assertEqual(aptitude.course_count, 1)
        self.assertEqual(aptitude.source_run_ids, [run.id])
        self.assertFalse(aptitude.component_details["growth_included"])

    def test_non_contributed_course_repository_is_not_added_to_student_totals(self):
        unrelated_repository = Repository.objects.create(
            id="repo-2",
            name="unrelated-project",
            url="https://github.com/someone-else/unrelated-project",
            owner_github_id="someone-else",
            language_bytes={"Python": 100},
        )
        Course_project.objects.create(
            course=self.course,
            course_year=2026,
            course_semester=1,
            repo=unrelated_repository,
            repo_name=unrelated_repository.name,
        )

        run = run_course_scoring(self.course)

        self.assertEqual(RepositoryScore.objects.filter(run=run).count(), 2)
        self.assertEqual(StudentRepositoryScore.objects.filter(run=run).count(), 1)
        student_course_score = StudentCourseScore.objects.get(
            run=run,
            student=self.student,
        )
        self.assertEqual(student_course_score.component_details["repository_count"], 1)
        self.assertEqual(
            student_course_score.component_details["owned_repository_count"],
            1,
        )

    def test_rerun_keeps_history_but_only_latest_run_feeds_aptitude(self):
        first_run = run_course_scoring(self.course)
        second_run = run_course_scoring(self.course)

        first_run.refresh_from_db()
        second_run.refresh_from_db()
        self.assertFalse(first_run.is_canonical)
        self.assertTrue(second_run.is_canonical)
        self.assertEqual(ScoringRun.objects.count(), 2)
        self.assertEqual(StudentCourseScore.objects.count(), 2)

        aptitude = StudentAptitudeScore.objects.get(student=self.student)
        self.assertEqual(aptitude.project_count, 1)
        self.assertEqual(aptitude.course_count, 1)
        self.assertEqual(aptitude.source_run_ids, [second_run.id])
