import statistics

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from course.models import Course, Course_project, Course_registration
from repo.models import (
    Repo_commit,
    Repo_contributor,
    Repo_issue,
    Repo_pr,
    RepoCommitFileChange,
    RepositorySnapshot,
)
from scoring.models import (
    FORMULA_VERSION,
    RepositoryScore,
    ScoringParameterSet,
    ScoringRun,
    StudentAptitudeScore,
    StudentCourseScore,
    StudentRepositoryScore,
)
from scoring.services.calculator import (
    activity_score,
    churn_rate,
    cohort_parameters,
    collaboration_score,
    difficulty_weighted_average,
    language_difficulty_multiplier,
    personal_multiplier,
    problem_solving_score,
    productivity_score,
    project_score,
    prototype_student_overall,
)


def _closed_issue_resolution_days(repository_id):
    durations = []
    issues = Repo_issue.objects.filter(
        repo_id=repository_id,
        created_at__isnull=False,
        closed_at__isnull=False,
    ).values_list("created_at", "closed_at")
    for created_at, closed_at in issues:
        seconds = (closed_at - created_at).total_seconds()
        if seconds >= 0:
            durations.append(seconds / 86400.0)
    return durations


def collect_repository_metrics(repository):
    commit_totals = Repo_commit.objects.filter(repo=repository).aggregate(
        commit_count=Count("id"),
        added_lines=Sum("added_lines"),
        deleted_lines=Sum("deleted_lines"),
    )
    commit_count = commit_totals["commit_count"] or 0
    added_lines = commit_totals["added_lines"] or 0
    deleted_lines = commit_totals["deleted_lines"] or 0

    merged_pr_count = Repo_pr.objects.filter(
        repo=repository, merged_at__isnull=False
    ).count()
    closed_unmerged_pr_count = Repo_pr.objects.filter(
        repo=repository, state__iexact="closed", merged_at__isnull=True
    ).count()
    open_pr_count = Repo_pr.objects.filter(repo=repository, state__iexact="open").count()
    unmerged_pr_count = closed_unmerged_pr_count + open_pr_count

    issue_count = Repo_issue.objects.filter(repo=repository).count()
    resolution_days = _closed_issue_resolution_days(repository.id)
    contributor_rows = list(
        Repo_contributor.objects.filter(repo=repository).values(
            "contributor_id", "contribution_count"
        )
    )

    snapshot = RepositorySnapshot.objects.filter(repo=repository).order_by("-collected_at").first()
    workflow_commit_count = (
        RepoCommitFileChange.objects.filter(repo=repository, is_workflow_yaml=True)
        .values("sha")
        .distinct()
        .count()
    )
    workflow_count = snapshot.workflow_yaml_count if snapshot else 0
    language_bytes = (
        snapshot.language_bytes
        if snapshot and snapshot.language_bytes
        else repository.language_bytes or {}
    )

    return {
        "repository_id": str(repository.id),
        "commit_count": commit_count,
        "added_lines": added_lines,
        "deleted_lines": deleted_lines,
        "changed_lines": added_lines + deleted_lines,
        "churn_rate": churn_rate(added_lines, deleted_lines),
        "merged_pr_count": merged_pr_count,
        "closed_unmerged_pr_count": closed_unmerged_pr_count,
        "open_pr_count": open_pr_count,
        "unmerged_pr_count": unmerged_pr_count,
        "pr_weighted_count": merged_pr_count + 0.4 * unmerged_pr_count,
        "issue_count": issue_count,
        "closed_issue_resolution_days": resolution_days,
        "average_issue_resolution_days": (
            statistics.fmean(resolution_days) if resolution_days else None
        ),
        "contributors": contributor_rows,
        "workflow_count": workflow_count or 0,
        "workflow_commit_count": workflow_commit_count,
        "has_snapshot": snapshot is not None,
        "language_bytes": language_bytes,
    }


def _create_parameter_set(course, metrics):
    frozen = (
        ScoringParameterSet.objects.filter(
            course=course,
            formula_version=FORMULA_VERSION,
            status=ScoringParameterSet.Status.FROZEN,
        )
        .order_by("-frozen_at", "-created_at")
        .first()
    )
    if frozen:
        return frozen

    values = cohort_parameters(metrics)
    return ScoringParameterSet.objects.create(
        course=course,
        formula_version=FORMULA_VERSION,
        status=ScoringParameterSet.Status.DRAFT,
        commit_p95=values["commit_p95"],
        changed_lines_p95=values["changed_lines_p95"],
        pr_weighted_p95=values["pr_weighted_p95"],
        churn_mean=values["churn_mean"],
        churn_stddev=values["churn_stddev"],
        issue_resolution_median_days=values["issue_resolution_median_days"],
        values={
            "team_size_reference": 4,
            "issue_cap": 5,
            "workflow_reference": 2,
            "workflow_update_reference": 3,
            "representative_min_share": 0.15,
            "representative_min_commits": 5,
            "representative_limit": 7,
            "difficulty_mode": "language_only",
            "repeated_file_enabled": False,
            "course_activity_window_enabled": False,
        },
    )


def _repository_warnings(metrics, problem_details, difficulty_details):
    warnings = []
    if metrics["changed_lines"] == 0:
        warnings.append("no_changed_line_data")
    if problem_details["issue_resolution"] is None:
        warnings.append("missing_closed_issue_sample")
    decided_pr_count = metrics["merged_pr_count"] + metrics["closed_unmerged_pr_count"]
    if decided_pr_count == 0:
        warnings.append("missing_decided_pr_sample")
    elif decided_pr_count < 3:
        warnings.append("low_confidence_pr_sample")
    if problem_details["cicd"] is None:
        warnings.append("missing_repository_snapshot")
    if difficulty_details["unmapped_languages"]:
        warnings.append("unmapped_languages_defaulted_to_1_0")
    warnings.append("repeated_file_metric_deferred")
    return warnings


def _create_repository_score(run, repository, metrics, parameter_set):
    productivity, productivity_details = productivity_score(
        metrics["commit_count"],
        metrics["added_lines"],
        metrics["deleted_lines"],
        parameter_set.commit_p95,
        parameter_set.changed_lines_p95,
        parameter_set.churn_mean,
        parameter_set.churn_stddev,
    )
    collaboration, collaboration_details = collaboration_score(
        metrics["merged_pr_count"],
        metrics["unmerged_pr_count"],
        [row["contribution_count"] for row in metrics["contributors"]],
        metrics["issue_count"],
        parameter_set.pr_weighted_p95,
    )
    problem_solving, problem_details = problem_solving_score(
        metrics["average_issue_resolution_days"],
        parameter_set.issue_resolution_median_days,
        metrics["merged_pr_count"],
        metrics["closed_unmerged_pr_count"],
        metrics["workflow_count"],
        metrics["workflow_commit_count"],
        has_snapshot=metrics["has_snapshot"],
    )
    difficulty, difficulty_details = language_difficulty_multiplier(metrics["language_bytes"])
    final = project_score(productivity, collaboration, problem_solving, difficulty)

    raw_metrics = dict(metrics)
    raw_metrics["contributors"] = [
        {
            "github_username": row["contributor_id"],
            "contribution_count": row["contribution_count"] or 0,
        }
        for row in metrics["contributors"]
    ]
    return RepositoryScore.objects.create(
        run=run,
        repository=repository,
        raw_metrics=raw_metrics,
        component_details={
            "productivity": productivity_details,
            "collaboration": collaboration_details,
            "problem_solving": problem_details,
            "difficulty": difficulty_details,
        },
        productivity_score=productivity,
        collaboration_score=collaboration,
        problem_solving_score=problem_solving,
        difficulty_multiplier=difficulty,
        final_score=final,
        warnings=_repository_warnings(metrics, problem_details, difficulty_details),
    )


def _create_student_repository_score(run, repository_score, metrics, student):
    github_username = (student.github_id or "").strip()
    if not github_username:
        return None

    contributor_by_username = {
        (row["contributor_id"] or "").strip().lower(): max(0, row["contribution_count"] or 0)
        for row in metrics["contributors"]
        if (row["contributor_id"] or "").strip()
    }
    personal_commits = Repo_commit.objects.filter(
        repo=repository_score.repository,
        author_github_id__iexact=github_username,
    ).aggregate(
        count=Count("id"),
        additions=Sum("added_lines"),
        deletions=Sum("deleted_lines"),
    )
    recorded_contributions = contributor_by_username.get(github_username.lower(), 0)
    personal_commit_count = personal_commits["count"] or recorded_contributions
    student_contributions = max(recorded_contributions, personal_commit_count)
    if student_contributions <= 0:
        return None

    total_contributions = sum(contributor_by_username.values()) + max(
        0, student_contributions - recorded_contributions
    )
    share = student_contributions / total_contributions if total_contributions > 0 else 0.0
    positive_contributors = sum(
        1 for count in contributor_by_username.values() if count > 0
    )
    student_already_counted = recorded_contributions > 0
    team_size = max(1, positive_contributors + (0 if student_already_counted else 1))
    multiplier = personal_multiplier(share, team_size)

    personal_changed_lines = (personal_commits["additions"] or 0) + (
        personal_commits["deletions"] or 0
    )
    personal_activity = activity_score(personal_commit_count, personal_changed_lines)
    eligible = share >= 0.15 and personal_commit_count >= 5

    return StudentRepositoryScore.objects.create(
        run=run,
        repository_score=repository_score,
        student=student,
        github_username=github_username,
        contribution_share=share,
        team_size=team_size,
        personal_multiplier=multiplier,
        personal_project_score=min(100.0, repository_score.final_score * multiplier),
        productivity_score=min(100.0, repository_score.productivity_score * multiplier),
        collaboration_score=min(100.0, repository_score.collaboration_score * multiplier),
        problem_solving_score=(
            None
            if repository_score.problem_solving_score is None
            else min(100.0, repository_score.problem_solving_score * multiplier)
        ),
        activity_score=personal_activity,
        representative_eligible=eligible,
        details={
            "personal_commit_count": personal_commit_count,
            "personal_changed_lines": personal_changed_lines,
            "total_team_contributions": total_contributions,
            "is_repository_owner": (
                (repository_score.repository.owner_github_id or "").strip().lower()
                == github_username.lower()
            ),
            "identity_mode": "github_username_only",
        },
    )


def _create_student_course_score(run, student, student_repository_scores):
    warnings = []
    if not (student.github_id or "").strip():
        warnings.append("missing_github_username")

    eligible = sorted(
        [score for score in student_repository_scores if score.representative_eligible],
        key=lambda score: score.activity_score,
        reverse=True,
    )[:7]
    for rank, score in enumerate(eligible, 1):
        score.representative_rank = rank
        score.save(update_fields=["representative_rank"])

    overall, overall_details = prototype_student_overall(
        [score.personal_project_score for score in student_repository_scores],
        [score.repository_score.collaboration_score for score in student_repository_scores],
    )
    if not student_repository_scores:
        warnings.append("no_contributed_repository")
    if not eligible:
        warnings.append("no_representative_repository")

    productivity = difficulty_weighted_average(
        [
            (score.productivity_score, score.repository_score.difficulty_multiplier)
            for score in eligible
        ]
    )
    collaboration = difficulty_weighted_average(
        [
            (score.collaboration_score, score.repository_score.difficulty_multiplier)
            for score in eligible
        ]
    )
    problem_solving = difficulty_weighted_average(
        [
            (score.problem_solving_score, score.repository_score.difficulty_multiplier)
            for score in eligible
        ]
    )
    return StudentCourseScore.objects.create(
        run=run,
        student=student,
        overall_score=overall,
        productivity_score=productivity,
        collaboration_score=collaboration,
        problem_solving_score=problem_solving,
        representative_repository_ids=[str(score.repository_score.repository_id) for score in eligible],
        component_details={
            **overall_details,
            "repository_count": len(student_repository_scores),
            "contributed_repository_count": len(student_repository_scores),
            "owned_repository_count": sum(
                1
                for score in student_repository_scores
                if score.details.get("is_repository_owner")
            ),
            "representative_repository_count": len(eligible),
        },
        warnings=warnings,
    )


def rebuild_student_aptitude(student, formula_version=FORMULA_VERSION):
    rows = list(
        StudentRepositoryScore.objects.filter(
            student=student,
            run__formula_version=formula_version,
            run__status=ScoringRun.Status.COMPLETED,
            run__is_canonical=True,
            contribution_share__gt=0,
        ).select_related("run", "repository_score", "repository_score__repository")
    )

    warnings = []
    overall, overall_details = prototype_student_overall(
        [row.personal_project_score for row in rows],
        [row.repository_score.collaboration_score for row in rows],
    )
    if not rows:
        warnings.append("no_contributed_repository")

    productivity = difficulty_weighted_average(
        [
            (row.productivity_score, row.repository_score.difficulty_multiplier)
            for row in rows
        ]
    )
    collaboration = difficulty_weighted_average(
        [
            (row.collaboration_score, row.repository_score.difficulty_multiplier)
            for row in rows
        ]
    )
    problem_solving = difficulty_weighted_average(
        [
            (row.problem_solving_score, row.repository_score.difficulty_multiplier)
            for row in rows
        ]
    )
    source_run_ids = sorted({row.run_id for row in rows})
    course_count = len({row.run.course_id for row in rows})
    owned_repository_count = sum(
        1 for row in rows if row.details.get("is_repository_owner")
    )

    aptitude, _ = StudentAptitudeScore.objects.update_or_create(
        student=student,
        formula_version=formula_version,
        defaults={
            "overall_score": overall,
            "productivity_score": productivity,
            "collaboration_score": collaboration,
            "problem_solving_score": problem_solving,
            "project_count": len(rows),
            "course_count": course_count,
            "source_run_ids": source_run_ids,
            "component_details": {
                **overall_details,
                "owned_repository_count": owned_repository_count,
                "aggregation_scope": "canonical_course_runs_only",
                "growth_included": False,
            },
            "warnings": warnings,
        },
    )
    return aptitude


def rebuild_all_student_aptitudes(formula_version=FORMULA_VERSION):
    from account.models import Student

    student_ids = set(
        StudentCourseScore.objects.filter(
            run__formula_version=formula_version,
            run__status=ScoringRun.Status.COMPLETED,
            run__is_canonical=True,
        ).values_list("student_id", flat=True)
    )
    student_ids.update(
        StudentAptitudeScore.objects.filter(
            formula_version=formula_version
        ).values_list("student_id", flat=True)
    )
    return [
        rebuild_student_aptitude(student, formula_version=formula_version)
        for student in Student.objects.filter(pk__in=student_ids).order_by("pk")
    ]


def run_course_scoring(course, trigger=ScoringRun.Trigger.MANUAL):
    repository_ids = list(
        dict.fromkeys(
            Course_project.objects.filter(course=course)
            .exclude(repo_id__isnull=True)
            .values_list("repo_id", flat=True)
        )
    )
    from repo.models import Repository

    repository_by_id = Repository.objects.in_bulk(repository_ids)
    repositories = [repository_by_id[repository_id] for repository_id in repository_ids if repository_id in repository_by_id]
    if not repositories:
        raise ValueError("The selected course has no repositories to score.")

    metrics_by_repository = {
        str(repository.id): collect_repository_metrics(repository) for repository in repositories
    }
    parameter_set = _create_parameter_set(course, list(metrics_by_repository.values()))
    run = ScoringRun.objects.create(
        course=course,
        parameter_set=parameter_set,
        formula_version=FORMULA_VERSION,
        trigger=trigger,
        status=ScoringRun.Status.RUNNING,
        affected_repository_ids=[str(repository.id) for repository in repositories],
    )

    try:
        with transaction.atomic():
            Course.objects.select_for_update().get(pk=course.pk)
            previous_canonical_runs = list(
                ScoringRun.objects.filter(
                    course=course,
                    formula_version=FORMULA_VERSION,
                    is_canonical=True,
                ).values_list("id", flat=True)
            )
            affected_student_ids = set(
                StudentCourseScore.objects.filter(
                    run_id__in=previous_canonical_runs
                ).values_list("student_id", flat=True)
            )

            repository_scores = {}
            for repository in repositories:
                repository_scores[str(repository.id)] = _create_repository_score(
                    run,
                    repository,
                    metrics_by_repository[str(repository.id)],
                    parameter_set,
                )

            students = list(
                registration.student
                for registration in Course_registration.objects.filter(course=course)
                .select_related("student")
                if registration.student is not None
            )
            students = list({student.pk: student for student in students}.values())
            student_repository_count = 0
            for student in students:
                rows = []
                for repository in repositories:
                    row = _create_student_repository_score(
                        run,
                        repository_scores[str(repository.id)],
                        metrics_by_repository[str(repository.id)],
                        student,
                    )
                    if row is not None:
                        rows.append(row)
                        student_repository_count += 1
                _create_student_course_score(run, student, rows)
                affected_student_ids.add(student.pk)

            ScoringRun.objects.filter(
                course=course,
                formula_version=FORMULA_VERSION,
                is_canonical=True,
            ).exclude(pk=run.pk).update(is_canonical=False)
            run.status = ScoringRun.Status.COMPLETED
            run.completed_at = timezone.now()
            run.is_canonical = True
            run.canonicalized_at = run.completed_at
            run.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "is_canonical",
                    "canonicalized_at",
                ]
            )

            from account.models import Student

            aptitude_count = 0
            for affected_student in Student.objects.filter(pk__in=affected_student_ids):
                rebuild_student_aptitude(affected_student)
                aptitude_count += 1

            run.summary = {
                "repository_score_count": len(repository_scores),
                "student_repository_score_count": student_repository_count,
                "student_course_score_count": len(students),
                # Temporary compatibility key for existing callers.
                "student_score_count": len(students),
                "student_aptitude_score_count": aptitude_count,
                "parameter_set_id": parameter_set.id,
                "is_canonical": True,
            }
            run.save(update_fields=["summary"])
    except Exception as exc:
        run.status = ScoringRun.Status.FAILED
        run.completed_at = timezone.now()
        run.error_message = str(exc)
        run.save(update_fields=["status", "completed_at", "error_message"])
        raise

    return run
