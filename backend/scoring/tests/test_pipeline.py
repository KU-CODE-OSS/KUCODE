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

    def test_one_commit_is_representative_eligible(self):
        Repo_commit.objects.filter(repo=self.repository).exclude(sha="sha-0").delete()
        Repo_contributor.objects.filter(repo=self.repository).update(
            contribution_count=1
        )

        run = run_course_scoring(self.course)

        personal_score = StudentRepositoryScore.objects.get(
            run=run,
            student=self.student,
        )
        self.assertEqual(personal_score.details["personal_commit_count"], 1)
        self.assertGreaterEqual(personal_score.contribution_share, 0.0)
        self.assertTrue(personal_score.representative_eligible)
        self.assertEqual(personal_score.representative_rank, 1)

    def test_claude_commits_are_shared_equally_between_human_contributors(self):
        teammate = Student.objects.create(
            id="student-2",
            name="Student Two",
            github_id="student-two",
        )
        Course_registration.objects.create(
            course=self.course,
            course_year=2026,
            course_semester=1,
            student=teammate,
        )
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="student-two",
            contribution_count=3,
        )
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="cLaUdE",
            contribution_count=5,
        )
        now = timezone.now()
        for index in range(3):
            Repo_commit.objects.create(
                sha=f"teammate-{index}",
                repo=self.repository,
                repo_url=self.repository.url,
                owner_github_id="student-one",
                author_github_id="student-two",
                added_lines=10,
                deleted_lines=2,
                committed_at=now,
                last_update=now.isoformat(),
            )
        for index in range(5):
            Repo_commit.objects.create(
                sha=f"claude-{index}",
                repo=self.repository,
                repo_url=self.repository.url,
                owner_github_id="student-one",
                author_github_id="CLAUDE" if index % 2 else "claude",
                added_lines=10,
                deleted_lines=2,
                committed_at=now,
                last_update=now.isoformat(),
            )

        run = run_course_scoring(self.course)

        first_score = StudentRepositoryScore.objects.get(
            run=run, student=self.student
        )
        teammate_score = StudentRepositoryScore.objects.get(
            run=run, student=teammate
        )
        repository_score = RepositoryScore.objects.get(run=run)

        self.assertEqual(first_score.team_size, 2)
        self.assertEqual(first_score.details["personal_commit_count"], 5)
        self.assertEqual(first_score.details["claude_commit_count"], 5)
        self.assertAlmostEqual(first_score.details["claude_commit_allocation"], 2.5)
        self.assertAlmostEqual(first_score.details["credited_contribution_count"], 7.5)
        self.assertAlmostEqual(first_score.contribution_share, 7.5 / 13)
        self.assertAlmostEqual(teammate_score.details["credited_contribution_count"], 5.5)
        self.assertAlmostEqual(teammate_score.contribution_share, 5.5 / 13)
        self.assertEqual(
            repository_score.component_details["collaboration"]["contributor_count"],
            2,
        )
        self.assertEqual(
            repository_score.component_details["collaboration"]["contribution_basis"],
            "claude_redistributed",
        )

    def test_claude_match_is_exact_and_case_insensitive(self):
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="claude-helper",
            contribution_count=2,
        )
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="Claude",
            contribution_count=1,
        )
        now = timezone.now()
        Repo_commit.objects.create(
            sha="claude-helper-sha",
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            author_github_id="claude-helper",
            added_lines=1,
            deleted_lines=0,
            committed_at=now,
            last_update=now.isoformat(),
        )
        Repo_commit.objects.create(
            sha="claude-uppercase-sha",
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            author_github_id="CLAUDE",
            added_lines=1,
            deleted_lines=0,
            committed_at=now,
            last_update=now.isoformat(),
        )

        run = run_course_scoring(self.course)
        repository_score = RepositoryScore.objects.get(run=run)
        redistribution = repository_score.raw_metrics["claude_redistribution"]

        self.assertEqual(redistribution["claude_commit_count"], 1)
        self.assertEqual(redistribution["human_contributor_count"], 2)
        self.assertAlmostEqual(redistribution["per_human_allocation"], 0.5)
        adjusted_names = {
            row["github_username"].casefold()
            for row in redistribution["adjusted_contributors"]
        }
        self.assertIn("claude-helper", adjusted_names)
        self.assertNotIn("claude", adjusted_names)

    def test_claude_only_repository_records_warning_without_allocation(self):
        Repo_commit.objects.filter(repo=self.repository).delete()
        Repo_contributor.objects.filter(repo=self.repository).delete()
        Repo_contributor.objects.create(
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            contributor_id="claude",
            contribution_count=1,
        )
        now = timezone.now()
        Repo_commit.objects.create(
            sha="claude-only-sha",
            repo=self.repository,
            repo_url=self.repository.url,
            owner_github_id="student-one",
            author_github_id="Claude",
            added_lines=1,
            deleted_lines=0,
            committed_at=now,
            last_update=now.isoformat(),
        )

        run = run_course_scoring(self.course)

        repository_score = RepositoryScore.objects.get(run=run)
        self.assertIn(
            "claude_commits_without_human_contributors",
            repository_score.warnings,
        )
        self.assertEqual(
            StudentRepositoryScore.objects.filter(run=run).count(), 0
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
