from collections import defaultdict

from django.http import JsonResponse

from account.models import Student
from login.models import Student as LoginStudent
from scoring.models import (
    FORMULA_VERSION,
    ScoringRun,
    StudentAptitudeScore,
    StudentCourseScore,
    StudentRepositoryScore,
)


def _optional_integer_filter(request, name):
    value = request.GET.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def course_ranking(request):
    """Return canonical StudentCourseScore rows grouped by course-semester."""
    if request.method != "GET":
        return JsonResponse({"error": "GET method required."}, status=405)

    try:
        year = _optional_integer_filter(request, "year")
        semester = _optional_integer_filter(request, "semester")
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    runs = ScoringRun.objects.filter(
        formula_version=FORMULA_VERSION,
        status=ScoringRun.Status.COMPLETED,
        is_canonical=True,
    ).select_related("course")
    if year is not None:
        runs = runs.filter(course__year=year)
    if semester is not None:
        runs = runs.filter(course__semester=semester)
    course_id = (request.GET.get("course_id") or "").strip()
    if course_id:
        runs = runs.filter(course__course_id=course_id)
    runs = list(
        runs.order_by(
            "-course__year",
            "-course__semester",
            "course__name",
            "course__course_id",
        )
    )

    run_ids = [run.id for run in runs]
    course_scores_by_run = defaultdict(list)
    for score in StudentCourseScore.objects.filter(run_id__in=run_ids).select_related(
        "student"
    ):
        course_scores_by_run[score.run_id].append(score)

    personal_activity_by_student_run = defaultdict(
        lambda: {"personal_commits": 0, "personal_changed_lines": 0}
    )
    for row in StudentRepositoryScore.objects.filter(run_id__in=run_ids).values(
        "run_id", "student_id", "details"
    ):
        activity = personal_activity_by_student_run[(row["run_id"], row["student_id"])]
        details = row["details"] or {}
        activity["personal_commits"] += int(details.get("personal_commit_count") or 0)
        activity["personal_changed_lines"] += int(
            details.get("personal_changed_lines") or 0
        )

    payload = []
    for run in runs:
        course = run.course
        students = []
        for score in course_scores_by_run[run.id]:
            student = score.student
            details = score.component_details or {}
            activity = personal_activity_by_student_run[(run.id, student.pk)]
            students.append(
                {
                    "student_id": student.pk,
                    "name": student.name,
                    "department": student.department or "",
                    "github": student.github_id or "",
                    "enrollment": student.enrollment or "",
                    "overall_score": score.overall_score,
                    "productivity_score": score.productivity_score,
                    "collaboration_score": score.collaboration_score,
                    "problem_solving_score": score.problem_solving_score,
                    "project_average": details.get("project_average"),
                    "collaboration_stability": details.get(
                        "collaboration_stability"
                    ),
                    "contributed_repository_count": details.get(
                        "contributed_repository_count",
                        details.get("repository_count", 0),
                    ),
                    "owned_repository_count": details.get(
                        "owned_repository_count", 0
                    ),
                    "representative_repository_count": details.get(
                        "representative_repository_count", 0
                    ),
                    "personal_commits": activity["personal_commits"],
                    "personal_changed_lines": activity["personal_changed_lines"],
                    "warnings": score.warnings or [],
                }
            )

        payload.append(
            {
                "year": course.year,
                "semester": course.semester,
                "course_id": course.course_id,
                "course_name": course.name,
                "prof": course.prof or "",
                "run_id": run.id,
                "formula_version": run.formula_version,
                "scored_at": run.completed_at,
                "students": students,
            }
        )

    return JsonResponse(payload, safe=False)


def student_aptitude(request):
    """Return the current cross-course aptitude score for one EProfile student."""
    if request.method != "GET":
        return JsonResponse({"error": "GET method required."}, status=405)

    student_id = (request.GET.get("student_id") or "").strip()
    uuid = (request.GET.get("uuid") or "").strip()
    if not student_id and not uuid:
        return JsonResponse(
            {"error": "student_id or uuid is required."},
            status=400,
        )

    if not student_id:
        try:
            student_id = LoginStudent.objects.get(member_id=uuid).pk
        except LoginStudent.DoesNotExist:
            return JsonResponse({"error": "Login student not found."}, status=404)

    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found."}, status=404)

    score = StudentAptitudeScore.objects.filter(
        student=student,
        formula_version=FORMULA_VERSION,
    ).first()
    if score is None:
        return JsonResponse(
            {
                "available": False,
                "student_id": student.pk,
                "formula_version": FORMULA_VERSION,
            }
        )

    details = score.component_details or {}
    return JsonResponse(
        {
            "available": True,
            "student_id": student.pk,
            "formula_version": score.formula_version,
            "overall_score": score.overall_score,
            "productivity_score": score.productivity_score,
            "collaboration_score": score.collaboration_score,
            "problem_solving_score": score.problem_solving_score,
            "project_count": score.project_count,
            "course_count": score.course_count,
            "project_average": details.get("project_average"),
            "collaboration_stability": details.get("collaboration_stability"),
            "owned_repository_count": details.get("owned_repository_count", 0),
            "aggregation_scope": details.get("aggregation_scope"),
            "growth_included": details.get("growth_included", False),
            "source_run_ids": score.source_run_ids or [],
            "warnings": score.warnings or [],
            "updated_at": score.updated_at,
        }
    )
