from collections import defaultdict

from course.models import Course_project
from repo.models import Repository


def repositories_matching_course_name(course):
    """Find repositories containing the course's complete naming token."""
    course_repo_name = (course.course_repo_name or "").strip()
    if not course_repo_name:
        return Repository.objects.none()
    return Repository.objects.filter(name__icontains=course_repo_name)


def _course_project_recency(course_project):
    course = course_project.course
    return (
        course_project.course_year or course.year or 0,
        course_project.course_semester or course.semester or 0,
        course_project.pk or 0,
    )


def reconcile_repository_course_categories(repository_ids=None):
    """Refresh cached Repository course flags from Course_project relations."""
    repositories = Repository.objects.all()
    if repository_ids is not None:
        repository_ids = list({str(repository_id) for repository_id in repository_ids})
        repositories = repositories.filter(pk__in=repository_ids)

    repositories = list(repositories)
    selected_ids = [repository.pk for repository in repositories]
    projects = (
        Course_project.objects.filter(repo_id__in=selected_ids)
        .exclude(repo_id__isnull=True)
        .select_related("course")
    )

    projects_by_repository = defaultdict(list)
    for project in projects:
        projects_by_repository[str(project.repo_id)].append(project)

    changed_repositories = []
    course_repository_count = 0
    non_course_repository_count = 0
    multiple_course_repository_count = 0

    for repository in repositories:
        repository_projects = projects_by_repository.get(str(repository.pk), [])
        if repository_projects:
            course_repository_count += 1
            if len(repository_projects) > 1:
                multiple_course_repository_count += 1
            selected_project = max(repository_projects, key=_course_project_recency)
            new_is_course = True
            new_category = selected_project.course.name
        else:
            non_course_repository_count += 1
            new_is_course = False
            new_category = repository.category if repository.category is not None else "-"

        if repository.is_course != new_is_course or repository.category != new_category:
            repository.is_course = new_is_course
            repository.category = new_category
            changed_repositories.append(repository)

    if changed_repositories:
        Repository.objects.bulk_update(
            changed_repositories,
            ["is_course", "category"],
        )

    return {
        "repository_count": len(repositories),
        "changed_repository_count": len(changed_repositories),
        "course_repository_count": course_repository_count,
        "non_course_repository_count": non_course_repository_count,
        "multiple_course_repository_count": multiple_course_repository_count,
    }
