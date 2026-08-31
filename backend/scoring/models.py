from django.db import models

from account.models import Student
from course.models import Course
from repo.models import Repository


FORMULA_VERSION = "prototype-v1"


class ScoringParameterSet(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FROZEN = "frozen", "Frozen"

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    formula_version = models.CharField(max_length=50, default=FORMULA_VERSION)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    commit_p95 = models.FloatField(default=0)
    changed_lines_p95 = models.FloatField(default=0)
    pr_weighted_p95 = models.FloatField(default=0)
    churn_mean = models.FloatField(default=0.20)
    churn_stddev = models.FloatField(default=0.15)
    issue_resolution_median_days = models.FloatField(null=True)
    values = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    frozen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["course", "formula_version", "status"]),
        ]

    def __str__(self):
        return f"{self.course_id}:{self.formula_version}:{self.status}"


class ScoringRun(models.Model):
    class Trigger(models.TextChoices):
        MANUAL = "manual", "Manual"
        CRAWL = "crawl", "Crawl"
        SCHEDULED = "scheduled", "Scheduled"

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        PARTIAL = "partial", "Partial"
        FAILED = "failed", "Failed"

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    parameter_set = models.ForeignKey(ScoringParameterSet, on_delete=models.PROTECT)
    formula_version = models.CharField(max_length=50, default=FORMULA_VERSION)
    trigger = models.CharField(max_length=20, choices=Trigger.choices, default=Trigger.MANUAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    affected_repository_ids = models.JSONField(default=list, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    is_canonical = models.BooleanField(default=False)
    canonicalized_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "formula_version"],
                condition=models.Q(is_canonical=True),
                name="unique_canonical_course_formula_run",
            ),
        ]
        indexes = [
            models.Index(fields=["course", "-started_at"]),
        ]

    def __str__(self):
        return f"run:{self.pk}:{self.course_id}:{self.status}"


class RepositoryScore(models.Model):
    run = models.ForeignKey(ScoringRun, on_delete=models.CASCADE, related_name="repository_scores")
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    raw_metrics = models.JSONField(default=dict)
    component_details = models.JSONField(default=dict)
    productivity_score = models.FloatField()
    collaboration_score = models.FloatField()
    problem_solving_score = models.FloatField(null=True)
    difficulty_multiplier = models.FloatField(default=1.0)
    final_score = models.FloatField()
    warnings = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["run", "repository"], name="unique_run_repository_score"),
        ]
        indexes = [models.Index(fields=["repository", "-id"])]

    def __str__(self):
        return f"{self.run_id}:{self.repository_id}:{self.final_score:.2f}"


class StudentRepositoryScore(models.Model):
    run = models.ForeignKey(ScoringRun, on_delete=models.CASCADE, related_name="student_repository_scores")
    repository_score = models.ForeignKey(RepositoryScore, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    github_username = models.CharField(max_length=255)
    contribution_share = models.FloatField(default=0)
    team_size = models.PositiveIntegerField(default=1)
    personal_multiplier = models.FloatField(default=0)
    personal_project_score = models.FloatField(default=0)
    productivity_score = models.FloatField(default=0)
    collaboration_score = models.FloatField(default=0)
    problem_solving_score = models.FloatField(null=True)
    activity_score = models.FloatField(default=0)
    representative_eligible = models.BooleanField(default=False)
    representative_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["run", "repository_score", "student"],
                name="unique_run_repository_student_score",
            ),
        ]
        indexes = [models.Index(fields=["student", "run"])]

    def __str__(self):
        return f"{self.run_id}:{self.student_id}:{self.repository_score_id}"


class StudentCourseScore(models.Model):
    run = models.ForeignKey(
        ScoringRun,
        on_delete=models.CASCADE,
        related_name="student_course_scores",
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    overall_score = models.FloatField(default=0)
    productivity_score = models.FloatField(null=True)
    collaboration_score = models.FloatField(null=True)
    problem_solving_score = models.FloatField(null=True)
    representative_repository_ids = models.JSONField(default=list, blank=True)
    component_details = models.JSONField(default=dict, blank=True)
    warnings = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["run", "student"], name="unique_run_student_score"),
        ]
        indexes = [models.Index(fields=["student", "-id"])]

    def __str__(self):
        return f"{self.run_id}:{self.student_id}:{self.overall_score:.2f}"


class StudentAptitudeScore(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="aptitude_scores",
    )
    formula_version = models.CharField(max_length=50, default=FORMULA_VERSION)
    overall_score = models.FloatField(default=0)
    productivity_score = models.FloatField(null=True)
    collaboration_score = models.FloatField(null=True)
    problem_solving_score = models.FloatField(null=True)
    project_count = models.PositiveIntegerField(default=0)
    course_count = models.PositiveIntegerField(default=0)
    source_run_ids = models.JSONField(default=list, blank=True)
    component_details = models.JSONField(default=dict, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "formula_version"],
                name="unique_student_aptitude_formula",
            ),
        ]
    def __str__(self):
        return f"{self.student_id}:{self.formula_version}:{self.overall_score:.2f}"
