import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now as timezone_now
from django.db.models import Sum, Count, Q

from repo.models import (
    Repository,
    Repo_contributor,
    Repo_issue,
    Repo_pr,
    Repo_commit,
    RepositorySnapshot,
    RepoCommitFileChange,
    RepoReviewComment,
    RepoDependabotAlert,
)
from account.models import Student
from account.api.views import get_students_for_crawling
from login.models import Student as LoginStudent
from course.models import Course, Course_project, Course_registration
from operator import itemgetter
import requests
import json
import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv("~/KUCODE/.env")


def get_repositories_for_crawling(request):
    repositories = list(Repository.objects.all())
    if request.GET.get("student_order") != "recent_courses":
        return repositories

    students = get_students_for_crawling(request)
    github_id_priority = {}
    for index, student in enumerate(students):
        if student.github_id:
            github_id_priority.setdefault(student.github_id, index)
    default_priority = len(github_id_priority)

    return sorted(
        repositories,
        key=lambda repository: github_id_priority.get(
            repository.owner_github_id,
            default_priority,
        ),
    )


GITHUB_BASELINE_TIMESTAMP = "2008-01-01T00:00:00Z"


def parse_github_timestamp(value):
    if not value or value == "Unknown":
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = make_aware(parsed)
    return parsed


def is_remote_timestamp_newer(remote_value, local_value):
    remote_dt = parse_github_timestamp(remote_value)
    if remote_dt is None:
        return False
    local_dt = parse_github_timestamp(local_value)
    if local_dt is None:
        return True
    return remote_dt > local_dt


def max_github_timestamp(*values):
    latest_value = None
    latest_dt = None
    for value in values:
        parsed = parse_github_timestamp(value)
        if parsed is None:
            continue
        if latest_dt is None or parsed > latest_dt:
            latest_dt = parsed
            latest_value = value
    return latest_value


def get_latest_model_timestamp(model, repo_id):
    return (
        model.objects.filter(repo_id=repo_id)
        .exclude(last_update__isnull=True)
        .exclude(last_update="")
        .order_by('-last_update')
        .values_list('last_update', flat=True)
        .first()
    )


def get_latest_commit_timestamp(repo_id):
    return get_latest_model_timestamp(Repo_commit, repo_id)


def get_latest_issue_pr_timestamp(repo_id):
    return max_github_timestamp(
        get_latest_model_timestamp(Repo_issue, repo_id),
        get_latest_model_timestamp(Repo_pr, repo_id),
    ) or GITHUB_BASELINE_TIMESTAMP


def check_issue_pr_activity(github_id, repo_name, since, activity_type='all'):
    response = requests.get(
        f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/activity",
        params={
            'github_id': github_id,
            'repo_name': repo_name,
            'since': since,
            'activity_type': activity_type,
        },
        timeout=30,
    )
    response.raise_for_status()
    activity_data = response.json()
    return bool(activity_data.get('has_updates')), activity_data


def should_crawl_repository(repo_record, repo_payload):
    if repo_record is None:
        return True, ['new_repository']

    reasons = []
    remote_updated_at = repo_payload.get('updated_at')
    remote_pushed_at = repo_payload.get('pushed_at')

    if is_remote_timestamp_newer(remote_updated_at, repo_record.updated_at):
        reasons.append('repository_updated')

    pushed_baseline = repo_record.pushed_at or get_latest_commit_timestamp(repo_record.id)
    if is_remote_timestamp_newer(remote_pushed_at, pushed_baseline):
        reasons.append('repository_pushed')

    if reasons:
        return True, reasons

    since = get_latest_issue_pr_timestamp(repo_record.id)
    try:
        has_activity, activity_data = check_issue_pr_activity(
            repo_record.owner_github_id,
            repo_record.name,
            since,
        )
    except Exception as exc:
        print(f"  [WARN] Failed to check issue/PR activity for {repo_record.name}: {exc}")
        return True, ['activity_check_failed']

    if has_activity:
        latest_type = activity_data.get('latest_type') or 'issue_or_pr'
        return True, [f'{latest_type}_updated']

    return False, []


def update_lightweight_repo_state(repo_record, repo_payload):
    if repo_record is None:
        return

    fields_to_update = []
    remote_pushed_at = repo_payload.get('pushed_at')
    if remote_pushed_at and repo_record.pushed_at != remote_pushed_at:
        repo_record.pushed_at = remote_pushed_at
        fields_to_update.append('pushed_at')

    remote_name = repo_payload.get('name')
    if remote_name and repo_record.name != remote_name:
        repo_record.name = remote_name
        fields_to_update.append('name')

    if fields_to_update:
        repo_record.save(update_fields=fields_to_update)


def is_full_sync_requested(request):
    scope = (
        request.GET.get('scope')
        or request.GET.get('sync_scope')
        or request.GET.get('crawl_scope')
        or ''
    ).lower()
    force_full = (request.GET.get('force_full') or '').lower()
    return scope in ('all', 'full') or force_full in ('1', 'true', 'yes')


def get_sync_scope(request):
    return 'all' if is_full_sync_requested(request) else 'changed'


def github_timestamp_for_api(value):
    parsed = parse_github_timestamp(value)
    if parsed is None:
        return GITHUB_BASELINE_TIMESTAMP
    return parsed.strftime('%Y-%m-%dT%H:%M:%SZ')


def fetch_remote_repo_payloads(github_id):
    response = requests.get(
        f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
        params={'github_id': github_id},
        timeout=60,
    )
    response.raise_for_status()
    remote_repos = response.json()
    if not isinstance(remote_repos, list):
        raise ValueError(f"Invalid repository list for GitHub user {github_id}")
    return {str(repo.get('id')): repo for repo in remote_repos if repo.get('id') is not None}


def should_sync_related_repository(repo_record, repo_payload, sync_kind):
    if repo_payload is None:
        return True, ['remote_metadata_missing']

    if sync_kind == 'commit':
        latest_commit_at = get_latest_commit_timestamp(repo_record.id)
        if latest_commit_at is None:
            return True, ['no_local_commits']
        if is_remote_timestamp_newer(repo_payload.get('pushed_at'), latest_commit_at):
            return True, ['repository_pushed']
        return False, []

    if sync_kind == 'contributor':
        has_contributors = Repo_contributor.objects.filter(repo_id=repo_record.id).exists()
        if not has_contributors:
            return True, ['no_local_contributors']
        latest_commit_at = get_latest_commit_timestamp(repo_record.id)
        if latest_commit_at and is_remote_timestamp_newer(repo_payload.get('pushed_at'), latest_commit_at):
            return True, ['repository_pushed']
        return False, []

    if sync_kind in ('issue', 'pr'):
        model = Repo_issue if sync_kind == 'issue' else Repo_pr
        since = get_latest_model_timestamp(model, repo_record.id) or GITHUB_BASELINE_TIMESTAMP
        try:
            has_activity, activity_data = check_issue_pr_activity(
                repo_record.owner_github_id,
                repo_record.name,
                since,
                activity_type=sync_kind,
            )
        except Exception as exc:
            print(f"  [WARN] Failed to check {sync_kind} activity for {repo_record.name}: {exc}")
            return True, [f'{sync_kind}_activity_check_failed']
        if has_activity:
            latest_type = activity_data.get('latest_type') or sync_kind
            return True, [f'{latest_type}_updated']
        return False, []

    should_sync, reasons = should_crawl_repository(repo_record, repo_payload)
    return should_sync, reasons


def get_repositories_for_sync(request, sync_kind):
    repositories = get_repositories_for_crawling(request)
    if is_full_sync_requested(request):
        return repositories, {
            'sync_scope': 'all',
            'candidate_repo_count': len(repositories),
            'skipped_repo_count': 0,
            'skipped_repo_sample': [],
        }

    remote_by_owner = {}
    filtered_repositories = []
    skipped_sample = []

    for repository in repositories:
        github_id = repository.owner_github_id
        if github_id not in remote_by_owner:
            try:
                remote_by_owner[github_id] = fetch_remote_repo_payloads(github_id)
            except Exception as exc:
                print(f"  [WARN] Failed to fetch repository metadata for {github_id}: {exc}")
                remote_by_owner[github_id] = None

        owner_payloads = remote_by_owner[github_id]
        repo_payload = None if owner_payloads is None else owner_payloads.get(str(repository.id))
        if owner_payloads is None:
            filtered_repositories.append(repository)
            continue

        should_sync, reasons = should_sync_related_repository(repository, repo_payload, sync_kind)
        if should_sync:
            filtered_repositories.append(repository)
        elif len(skipped_sample) < 20:
            skipped_sample.append({
                'github_id': github_id,
                'repo_id': repository.id,
                'repo_name': repository.name,
                'reason': 'no_remote_changes',
            })

    return filtered_repositories, {
        'sync_scope': 'changed',
        'candidate_repo_count': len(filtered_repositories),
        'skipped_repo_count': len(repositories) - len(filtered_repositories),
        'skipped_repo_sample': skipped_sample,
    }


class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

# ========================================
# Backend Function
# ========================================
# ------------Repo--------------#
def sync_repo_db(request):
    # Exception handling block for the entire process
    try:
        # 1. Fetch all student information from the database.
        students = get_students_for_crawling(request, reverse_default=True)
        students_list = [{'id': student.id, 'github_id': student.github_id} for student in students]

        # 2. Initialize counters and lists to track synchronization results.
        total_student_count = len(students_list)
        student_count = total_student_count + 1

        success_student_count = 0
        failure_student_count = 0
        failure_student_details = []

        sync_scope = get_sync_scope(request)
        success_repo_count = 0
        skipped_repo_count = 0
        skipped_repo_sample = []
        failure_repo_count = 0
        failure_repo_details = []

        # 3. Start the synchronization process for each student.
        for student in students_list:
            student_count -= 1
            print(f'\n{"="*10} [{student_count}/{total_student_count}] Processing GitHub user: {student["github_id"]} {"="*10}')
            id = student['id']
            github_id = student['github_id']
            
            # 4. Fetch the latest repository list for the student from the FastAPI endpoint.
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos", params={'github_id': github_id})
            if response.status_code != 200:
                message = f"Failed to fetch repositories for GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue
            
            data = response.json()
            # Handle error if the API response format is not a list
            if not isinstance(data, list):
                message = f"Invalid response format for repositories of GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue

            total_repo_count = len(data)
            repo_list = [
                {
                    'id': str(repo['id']),
                    'name': repo['name'],
                    'updated_at': repo.get('updated_at'),
                    'pushed_at': repo.get('pushed_at'),
                    'default_branch': repo.get('default_branch'),
                }
                for repo in data
            ]

            # 5. Compare the list of repositories stored in the DB with the list from the API to find repositories to delete.
            repos_in_db = list(Repository.objects.filter(owner_github_id=github_id))
            repos_by_id = {str(repo.id): repo for repo in repos_in_db}
            repo_ids_in_db = set(repos_by_id.keys())
            repos_in_db_sorted = sorted(repo_ids_in_db)
            print("-"*5 + f"\nDB: {repos_in_db_sorted}")

            # List of the latest repository IDs from FastAPI
            repo_ids_in_list = sorted([repo['id'] for repo in repo_list])
            print("-"*5 + f"\nFASTAPI: {repo_ids_in_list}")

            # Repositories that are in the DB but not in the FastAPI list (targets for deletion)
            missing_in_fastapi = repo_ids_in_db - set(repo_ids_in_list)

            if missing_in_fastapi:
                print("-"*5 + f"\n Need to Remove: {missing_in_fastapi}\n"+"-"*5)
            else:
                print("-"*5 + f"\n No repositories need to be removed.\n"+"-"*5)

            # 6. Iterate through repositories that need to be deleted and call the delete function.
            for repo_id in missing_in_fastapi:
                remove_repository(github_id, Repository(id=repo_id))
                print(f" Repository {repo_id} removed for GitHub ID: {github_id}\n"+"-"*5)

            # 7. Process only repositories with detected changes.
            repo_count = 0
            for repo in repo_list:
                repo_name = repo['name']
                repo_id = repo['id']
                repo_count += 1
                existing_repo = repos_by_id.get(repo_id)
                print(f"  [{repo_count}/{total_repo_count}] Checking repository: {repo_name} (ID: {repo_id})")

                if is_full_sync_requested(request):
                    should_crawl, crawl_reasons = True, ['full_sync']
                else:
                    should_crawl, crawl_reasons = should_crawl_repository(existing_repo, repo)
                if not should_crawl:
                    update_lightweight_repo_state(existing_repo, repo)
                    skipped_repo_count += 1
                    if len(skipped_repo_sample) < 20:
                        skipped_repo_sample.append({
                            "github_id": github_id,
                            "repo_id": repo_id,
                            "repo_name": repo_name,
                            "reason": "no_remote_changes",
                        })
                    print(f"  [SKIP] No remote changes detected for repo: {repo_name}.")
                    continue

                print(f"  [CRAWL] Change detected for repo: {repo_name}. reasons={crawl_reasons}")
                
                # 7-1. Fetch detailed data for the individual repository.
                repo_response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos", params={'github_id': github_id, 'repo_id': repo_id})
                if repo_response.status_code != 200:
                    message = f"Failed to fetch data for repo {repo_id} of GitHub user {github_id}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_id": repo_id, "message": message})
                    continue

                repo_data = repo_response.json()

                language_percentage = {}
                try:
                    language_bytes = repo_data.get('language_bytes', {})
                    if language_bytes:
                        total_bytes = sum(language_bytes.values())

                        for language, bytes in language_bytes.items():
                            percentage = (bytes / total_bytes) * 100
                            # Round to one decimal place
                            language_percentage[language] = round(percentage, 1)

                except Exception as e:
                    # Log an error if one occurs while processing a repository
                    message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

                try:
                    print(f"  {github_id}/{repo_name}: {repo_data}")
                    # 7-2. Use `update_or_create` to create or update repository information in the database.
                    repository_record, created = Repository.objects.update_or_create(
                        owner_github_id=github_id,
                        id=repo_id,
                        defaults={
                            'name': repo_name,
                            'url': repo_data.get('url'),
                            'default_branch': repo_data.get('default_branch') or repo.get('default_branch'),
                            'created_at': repo_data.get('created_at'),
                            'updated_at': repo_data.get('updated_at'),
                            'pushed_at': repo_data.get('pushed_at') or repo.get('pushed_at'),
                            'forked': repo_data.get('forked'),
                            'fork_count': repo_data.get('forks_count'),
                            'star_count': repo_data.get('stars_count'),
                            'commit_count': repo_data.get('commit_count'),
                            'open_issue_count': repo_data.get('open_issue_count'),
                            'closed_issue_count': repo_data.get('closed_issue_count'),
                            'open_pr_count': repo_data.get('open_pr_count'),
                            'closed_pr_count': repo_data.get('closed_pr_count'),
                            'contributed_commit_count': repo_data.get('contributed_commit_count'),
                            'contributed_open_issue_count': repo_data.get('contributed_open_issue_count'),
                            'contributed_closed_issue_count': repo_data.get('contributed_closed_issue_count'),
                            'contributed_open_pr_count': repo_data.get('contributed_open_pr_count'),
                            'contributed_closed_pr_count': repo_data.get('contributed_closed_pr_count'),
                            'language': ', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None',
                            'language_bytes': repo_data.get('language_bytes', {}),
                            'language_percentage': language_percentage,
                            'contributors': ', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None',
                            'license': repo_data.get('license'),
                            'has_readme': repo_data.get('has_readme'),
                            'description': repo_data.get('description'),
                            'release_version': repo_data.get('release_version'),
                            'crawled_date': repo_data.get('crawled_date'),
                        }
                    )
                    
                    action = "Created" if created else "Updated"
                    print(f"  {action} repository: {repo_name} (ID: {repo_id})")
                    success_repo_count += 1

                except Exception as e:
                    # Log an error if one occurs while processing a repository
                    message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

            # 8. Calculate the total star count for all of the student's repositories and update the student's record.
            total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count'] or 0
            student_record = Student.objects.get(id=id)
            student_record.starred_count = total_star_count
            student_record.save()

            print(f"  Total star count ({total_star_count}) for GitHub user {github_id} saved.")
            success_student_count += 1
            print(f'{"-"*5} Processed GitHub user: {github_id} {"-"*5}')

        # 9. Return a summary of the operation in JSON format.
        return JsonResponse({
            "status": "OK",
            "message": "Repositories updated successfully",
            "success_student_count": success_student_count,
            "failure_student_count": failure_student_count,
            "failure_student_details": failure_student_details,
            "sync_scope": sync_scope,
            "success_repo_count": success_repo_count,
            "skipped_repo_count": skipped_repo_count,
            "skipped_repo_sample": skipped_repo_sample,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle unexpected errors during the entire process
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

# ---------------------------------------------

# ========================================
# Backend Function
# ========================================
# ------------Repo--------------#
@csrf_exempt
def sync_repo_db_optional(request):
    # Exception handling block for the entire process
    try:
        # 1. Fetch student information.
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                if isinstance(data, list):
                    students_list = data
                elif isinstance(data, dict) and 'students' in data:
                    students_list = data['students']
                else:
                    return JsonResponse({"status": "Error", "message": "Invalid data format. Expected a list or 'students' key."}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({"status": "Error", "message": "Invalid JSON"}, status=400)
        else:
            students = get_students_for_crawling(request, reverse_default=True)
            students_list = [{'id': student.id, 'github_id': student.github_id} for student in students]

        # 2. Initialize counters and lists to track synchronization results.
        total_student_count = len(students_list)
        student_count = total_student_count + 1

        success_student_count = 0
        failure_student_count = 0
        failure_student_details = []

        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        # 3. Start the synchronization process for each student.
        for student in students_list:
            student_count -= 1
            print(f'\n{"="*10} [{student_count}/{total_student_count}] Processing GitHub user: {student["github_id"]} {"="*10}')
            id = student['id']
            github_id = student['github_id']
            
            # 4. Fetch the latest repository list for the student from the FastAPI endpoint.
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos", params={'github_id': github_id})
            if response.status_code != 200:
                message = f"Failed to fetch repositories for GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue
            
            data = response.json()
            # Handle error if the API response format is not a list
            if not isinstance(data, list):
                message = f"Invalid response format for repositories of GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue

            total_repo_count = len(data)
            repo_list = [
                {
                    'id': repo['id'],
                    'name': repo['name'],
                    'default_branch': repo.get('default_branch'),
                }
                for repo in data
            ]

            
            # 5. Compare the list of repositories stored in the DB with the list from the API to find repositories to delete.
            # List of repository IDs currently in the database
            repos_in_db = Repository.objects.filter(owner_github_id=github_id).values_list('id', flat=True)
            repos_in_db_sorted = sorted(repos_in_db) 
            print("-"*5 + f"\nDB: {repos_in_db_sorted}")

            # List of the latest repository IDs from FastAPI
            repo_ids_in_list = sorted([str(repo['id']) for repo in repo_list])
            print("-"*5 + f"\nFASTAPI: {repo_ids_in_list}")

            # Repositories that are in the DB but not in the FastAPI list (targets for deletion)
            missing_in_fastapi = set(repos_in_db) - set(repo_ids_in_list)

            if missing_in_fastapi:
                print("-"*5 + f"\n Need to Remove: {missing_in_fastapi}\n"+"-"*5)
            else:
                print("-"*5 + f"\n No repositories need to be removed.\n"+"-"*5)

            # 6. Iterate through repositories that need to be deleted and call the delete function.
            for repo_id in repos_in_db:
                if repo_id not in repo_ids_in_list:
                    # Deletes the repository along with all linked child data (commits, issues, etc.)
                    remove_repository(github_id, Repository(id=repo_id))
                    print(f" Repository {repo_id} removed for GitHub ID: {github_id}\n"+"-"*5)

            # 7. Process each repository's information received from the API.
            repo_count = 0
            for repo in repo_list:
                repo_name = repo['name']
                repo_id = repo['id']
                repo_count += 1
                print(f"  [{repo_count}/{total_repo_count}] Processing repository: {repo_name} (ID: {repo_id})")
                
                # 7-1. Fetch detailed data for the individual repository.
                repo_response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos", params={'github_id': github_id, 'repo_id': repo_id})
                if repo_response.status_code != 200:
                    message = f"Failed to fetch data for repo {repo_id} of GitHub user {github_id}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_id": repo_id, "message": message})
                    continue

                repo_data = repo_response.json()

                language_percentage = {}
                try:
                    language_bytes = repo_data.get('language_bytes', {})
                    if language_bytes:
                        total_bytes = sum(language_bytes.values())

                        for language, bytes in language_bytes.items():
                            percentage = (bytes / total_bytes) * 100
                            # 소수점 1자리
                            language_percentage[language] = round(percentage, 1)

                except Exception as e:
                    # Log an error if one occurs while processing a repository
                    message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

                try:
                    print(f"  {github_id}/{repo_name}: {repo_data}")
                    # 7-2. Use `update_or_create` to create or update repository information in the database.
                    repository_record, created = Repository.objects.update_or_create(
                        owner_github_id=github_id,
                        id=repo_id,
                        defaults={
                            'name': repo_name,
                            'url': repo_data.get('url'),
                            'default_branch': repo_data.get('default_branch') or repo.get('default_branch'),
                            'created_at': repo_data.get('created_at'),
                            'updated_at': repo_data.get('updated_at'),
                            'forked': repo_data.get('forked'),
                            'fork_count': repo_data.get('forks_count'),
                            'star_count': repo_data.get('stars_count'),
                            'commit_count': repo_data.get('commit_count'),
                            'open_issue_count': repo_data.get('open_issue_count'),
                            'closed_issue_count': repo_data.get('closed_issue_count'),
                            'open_pr_count': repo_data.get('open_pr_count'),
                            'closed_pr_count': repo_data.get('closed_pr_count'),
                            'contributed_commit_count': repo_data.get('contributed_commit_count'),
                            'contributed_open_issue_count': repo_data.get('contributed_open_issue_count'),
                            'contributed_closed_issue_count': repo_data.get('contributed_closed_issue_count'),
                            'contributed_open_pr_count': repo_data.get('contributed_open_pr_count'),
                            'contributed_closed_pr_count': repo_data.get('contributed_closed_pr_count'),
                            'language': ', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None',
                            'language_bytes': repo_data.get('language_bytes', {}),
                            'language_percentage': language_percentage,
                            'contributors': ', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None',
                            'license': repo_data.get('license'),
                            'has_readme': repo_data.get('has_readme'),
                            'description': repo_data.get('description'),
                            'release_version': repo_data.get('release_version'),
                            'crawled_date': repo_data.get('crawled_date'),
                        }
                    )
                    
                    action = "Created" if created else "Updated"
                    print(f"  {action} repository: {repo_name} (ID: {repo_id})")
                    success_repo_count += 1

                except Exception as e:
                    # Log an error if one occurs while processing a repository
                    message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

            # 8. Calculate the total star count for all of the student's repositories and update the student's record.
            # Calculate the sum of `star_count` for all repositories of the student.
            total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count'] or 0
            student_record = Student.objects.get(id=id)
            # Update the `starred_count` field of the Student model.
            student_record.starred_count = total_star_count
            student_record.save()

            print(f"  Total star count ({total_star_count}) for GitHub user {github_id} saved.")
            success_student_count += 1
            print(f'{"-"*5} Processed GitHub user: {github_id} {"-"*5}')

        # 9. Return a summary of the operation in JSON format.
        return JsonResponse({
            "status": "OK",
            "message": "Repositories updated successfully",
            "success_student_count": success_student_count,
            "failure_student_count": failure_student_count,
            "failure_student_details": failure_student_details,
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle unexpected errors during the entire process
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------DELETE--------------#
def remove_repository(github_id, repository):

    # 1. First, check if linked to a Course_project
    if Course_project.objects.filter(repo=repository.id).exists():
        print(f"  [Skipped] Repo ID {repository.id} ('{repository.name}') is part of a Course_project and will not be deleted.")
        return {
            "status": "Skipped",
            "message": f"Repository '{repository.name}' is part of a course project and was not deleted."
        }

    # Deletion logic proceeds only if not linked to a Course_project
    try:
        # 2. Delete all related child data (more concisely)
        deleted_contributors, _ = Repo_contributor.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_contributors} contributor(s) for repo ID: {repository.id}")

        deleted_issues, _ = Repo_issue.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_issues} issue(s) for repo ID: {repository.id}")

        deleted_prs, _ = Repo_pr.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_prs} pull request(s) for repo ID: {repository.id}")

        deleted_commits, _ = Repo_commit.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_commits} commit(s) for repo ID: {repository.id}")

        deleted_file_changes, _ = RepoCommitFileChange.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_file_changes} commit file change(s) for repo ID: {repository.id}")

        deleted_snapshots, _ = RepositorySnapshot.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_snapshots} repository snapshot(s) for repo ID: {repository.id}")

        deleted_review_comments, _ = RepoReviewComment.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_review_comments} review comment(s) for repo ID: {repository.id}")

        deleted_dependabot_alerts, _ = RepoDependabotAlert.objects.filter(repo=repository.id).delete()
        print(f"  Deleted {deleted_dependabot_alerts} Dependabot alert(s) for repo ID: {repository.id}")

        # 3. Finally, delete the Repository object itself
        try:
            repository_obj = Repository.objects.get(owner_github_id=github_id, id=repository.id)
            repo_name = repository_obj.name
            repository_obj.delete()
            print(f"  [Success] The repo '{repo_name}' (ID: {repository.id}) has been deleted successfully for GitHub user {github_id}")
            return {"status": "OK", "message": "The repo has been deleted successfully"}
        except Repository.DoesNotExist:
            print(f"  [Error] Repo with ID '{repository.id}' does not exist for GitHub user {github_id}")
            return {"status": "Error", "message": f"Repo with ID '{repository.id}' does not exist"}

    except Exception as e:
        print(f"  [Fatal Error] An unexpected error occurred while deleting repo ID '{repository.id}' for user {github_id}: {str(e)}")
        return {"status": "Error", "message": str(e)}

# ---------------------------------------------
    
# ------------REPO READ--------------#
def repo_read_db(request):
    try:
        # 1) 모든 데이터를 미리 로드
        repo_list = Repository.objects.select_related().prefetch_related(
            'repo_pr_set'
        ).all()
        
        # 2) Student 데이터를 github_id로 인덱싱
        all_github_ids = set()
        for r in repo_list:
            all_github_ids.add(r.owner_github_id)
            if r.contributors:
                all_github_ids.update([c.strip() for c in r.contributors.split(',') if c.strip()])
        
        students = Student.objects.filter(github_id__in=all_github_ids)
        students_by_github_id = {s.github_id: s for s in students}
        
        data = []
        
        # 3) 레포지토리별 처리
        for r in repo_list:
            # Owner 정보 (이미 로드된 데이터에서 조회)
            student = students_by_github_id.get(r.owner_github_id)
            if not student:
                continue  # Owner를 찾을 수 없으면 스킵
            
            # PR count (prefetch된 데이터 사용)
            pr_count = len(list(r.repo_pr_set.all()))
            
            # Contributors 처리
            contributors_list = [c.strip() for c in r.contributors.split(',') if c.strip()] if r.contributors else []
            contributors_count = len(contributors_list)
            
            if contributors_count == 0:
                contributors_total_info = []
            else:
                contributors_total_info = []
                for contributor_github_id in contributors_list:
                    contributor_student = students_by_github_id.get(contributor_github_id)
                    
                    if contributor_student:
                        contributors_total_info.append([
                            contributor_student.name,
                            contributor_student.department,
                            contributor_student.id,
                            contributor_student.github_id
                        ])
                    else:
                        contributors_total_info.append(['-', '-', '-', contributor_github_id])
                
                # 등록된 사용자만 필터링 및 정렬
                contributors_without_dash = [info for info in contributors_total_info if '-' not in info[0]]
                contributors_without_dash.sort(key=lambda x: x[0])
                contributors_total_info = contributors_without_dash
            
            # Repository 정보 조합
            repo_info = {
                'id': r.id,
                'name': r.name,
                'url': r.url,
                'student_id': student.id,
                'owner_github_id': r.owner_github_id,
                'default_branch': r.default_branch,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
                'fork_count': r.fork_count,
                'star_count': r.star_count,
                'commit_count': r.commit_count,
                'total_issue_count': int(r.open_issue_count) + int(r.closed_issue_count),
                'pr_count': pr_count,
                'language': r.language,
                'contributors': contributors_count,
                'contributors_list': contributors_total_info,
                'license': r.license,
                'has_readme': r.has_readme,
                'description': r.description,
                'release_version': r.release_version
            }
            
            data.append(repo_info)
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------
#-------------SYNC REPO CATEGORY-------------#
def sync_repo_category(request):
    updated_repos = []
    repositories = Repository.objects.all()
    for repo in repositories:
        try:
            course = Course.objects.get(course_repo_name=repo.name)
            repo.category = course.name
            repo.is_course = True 
        except ObjectDoesNotExist:
            repo.is_course = False
            if repo.category is None:
                repo.category = "-"
        updated_repos.append(repo)
    Repository.objects.bulk_update(updated_repos, ['category', 'is_course'])
    return JsonResponse({"status": "200", "message": "Repository categories synchronized successfully."})
# ---------------------------------------------
# ------------CONTRIBUTOR--------------#
def sync_repo_contributor_db(request):
    # 1. Initialization
    # Initialize counters and lists to track the outcome of the sync process.
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []

    try:
        # 2. Fetch all repositories from the database.
        repositories, filter_summary = get_repositories_for_sync(request, 'contributor')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)

        # 3. Iterate through each repository to sync its contributors.
        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{total_repo_count}] Syncing contributors for repo: {repo_name} {"="*10}')
            
            # Use a try-except block for each repo to prevent one failure from stopping the entire process.
            try:
                # 3a. Fetch contributor data for the repository from the API.
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/contributor",
                    params={'github_id': github_id, 'repo_name': repo_name}
                )
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                contributor_data = response.json()

                if not isinstance(contributor_data, list):
                    raise ValueError("Invalid response format: API did not return a list.")

                # 3b. Clear existing contributors for this repo to ensure a true synchronization.
                # This step is crucial for removing contributors who are no longer part of the project.
                deleted_count, _ = Repo_contributor.objects.filter(repo_id=repo_id).delete()
                if deleted_count > 0:
                    print(f"  Cleared {deleted_count} old contributor record(s) for repo {repo_name}.")

                # 3c. Process and save each contributor from the API response.
                for contributor in contributor_data:
                    # `update_or_create` finds a record using the unique keys (repo_id, contributor_id).
                    # If it exists, it's updated with `defaults`. If not, it's created.
                    _, created = Repo_contributor.objects.update_or_create(
                        repo_id=repo_id,
                        contributor_id=contributor.get('login'),
                        defaults={
                            'owner_github_id': github_id,
                            'contribution_count': contributor.get('contributions'),
                            'repo_url': contributor.get('repo_url')
                        }
                    )
                
                print(f'  [SUCCESS] Synced {len(contributor_data)} contributor(s) for repo: {repo_name}.')
                success_repo_count += 1

            except Exception as e:
                # Log the error for the specific repository and continue with the next one.
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        # 4. Return a summary of the entire synchronization process.
        return JsonResponse({
            "status": "OK",
            "message": "Contributor synchronization completed.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle fatal errors that prevent the script from starting or running properly.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------contributor READ--------------#
def repo_contributor_read_db(request):
    try:
        # 1. Fetch all contributor data directly as a list of dictionaries.
        # Using .values() is more efficient than fetching full objects and converting them manually,
        # as it lets the database do the work.
        contributor_list = list(Repo_contributor.objects.values(
            'id',
            'repo_id',
            'repo_url',
            'owner_github_id',
            'contributor_id',
            'contribution_count' # Corrected field name for consistency
        ))
        
        # 2. Return the list of contributors as a JSON response.
        return JsonResponse(contributor_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the database query.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ISSUE--------------#
def sync_repo_issue_db(request):
    # 1. Initialization
    # Initialize counters and lists to track the outcome of the sync process.
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []

    try:
        # 2. Fetch all repositories from the database.
        repositories, filter_summary = get_repositories_for_sync(request, 'issue')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)

        # 3. Iterate through each repository to sync its issues.
        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{total_repo_count}] Syncing issues for repo: {repo_name} {"="*10}')

            # Use a try-except block for each repo to prevent one failure from stopping the entire process.
            try:
                # 3a. Find the last update timestamp to fetch only new or updated issues.
                # This makes the API call more efficient by reducing the amount of data fetched.
                latest_issue = Repo_issue.objects.filter(repo_id=repo_id).order_by('-last_update').first()
                since = latest_issue.last_update if latest_issue else "2008-01-01T00:00:00Z"

                # 3b. Fetch issue data from the API.
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/issues",
                    params={'github_id': github_id, 'repo_name': repo_name, 'since': since}
                )
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                issue_data_list = response.json()

                if not isinstance(issue_data_list, list):
                    raise ValueError("Invalid response format: API did not return a list.")

                if not issue_data_list:
                    print(f"  No new issues to update for repo: {repo_name}.")
                    success_repo_count += 1
                    continue
                
                print(f"  Found {len(issue_data_list)} new/updated issue(s) to process.")

                # 3c. Process and save each issue from the API response.
                for issue_data in issue_data_list:
                    # `update_or_create` finds a record by its primary key ('id').
                    # If it exists, it's updated with `defaults`. If not, it's created.
                    _, created = Repo_issue.objects.update_or_create(
                        id=issue_data.get('id'),
                        defaults={
                            'repo_id': repo_id,
                            'issue_number': issue_data.get('issue_number'),
                            'repo_url': issue_data.get('repo_url') or issue_data.get('repository_url'),
                            'owner_github_id': issue_data.get('contributed_github_id'),
                            'state': issue_data.get('state'),
                            'title': issue_data.get('title'),
                            'publisher_github_id': issue_data.get('publisher_github_id'),
                            'created_at': parse_github_timestamp(issue_data.get('created_at')),
                            'closed_at': parse_github_timestamp(issue_data.get('closed_at')),
                            'last_update': issue_data.get('last_update')
                        }
                    )

                success_repo_count += 1
                print(f'  [SUCCESS] Finished processing issues for repo: {repo_name}.')

            except Exception as e:
                # Log the error for the specific repository and continue with the next one.
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        # 4. Return a summary of the entire synchronization process.
        return JsonResponse({
            "status": "OK",
            "message": "Repo issues synchronization completed.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle fatal errors that prevent the script from starting or running properly.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ISSUE READ--------------#
def repo_issue_read_db(request):
    try:
        # 1. Fetch all issue data directly as a list of dictionaries.
        # Using .values() is more efficient than fetching full model instances
        # and converting them in Python, as it performs the conversion at the database level.
        issue_list = list(Repo_issue.objects.values(
            'id',
            'repo_id',
            'issue_number',
            'repo_url',
            'owner_github_id',
            'state',
            'title',
            'publisher_github_id',
            'created_at',
            'closed_at',
            'last_update'
        ))
        
        # 2. Return the list of issues as a JSON response.
        return JsonResponse(issue_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the database query.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------PR--------------#
def sync_repo_pr_db(request):
    # 1. Initialization
    # Initialize counters and lists to track the outcome of the sync process.
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []

    try:
        # 2. Fetch all repositories from the database.
        repositories, filter_summary = get_repositories_for_sync(request, 'pr')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)

        # 3. Iterate through each repository to sync its pull requests (PRs).
        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{total_repo_count}] Syncing PRs for repo: {repo_name} {"="*10}')

            # Use a try-except block for each repo to prevent one failure from stopping the entire process.
            try:
                # 3a. Find the last update timestamp to fetch only new or updated PRs.
                # This makes the API call more efficient.
                latest_pr = Repo_pr.objects.filter(repo_id=repo_id).order_by('-last_update').first()
                since = latest_pr.last_update if latest_pr else "2008-01-01T00:00:00Z"

                # 3b. Fetch pull request data from the API.
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/pulls",
                    params={'github_id': github_id, 'repo_name': repo_name, 'since': since}
                )
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                pr_data_list = response.json()

                if not isinstance(pr_data_list, list):
                    raise ValueError("Invalid response format: API did not return a list.")

                if not pr_data_list:
                    print(f"  No new PRs to update for repo: {repo_name}.")
                    success_repo_count += 1
                    continue
                
                print(f"  Found {len(pr_data_list)} new/updated PR(s) to process.")

                # 3c. Process and save each PR from the API response.
                for pr_data in pr_data_list:
                    # `update_or_create` finds a record by its primary key ('id').
                    # If it exists, it's updated. If not, it's created.
                    _, created = Repo_pr.objects.update_or_create(
                        id=pr_data.get('id'),
                        defaults={
                            'repo_id': repo_id,
                            'pr_number': pr_data.get('pr_number'),
                            'repo_url': pr_data.get('repo_url') or pr_data.get('repository_url'),
                            'owner_github_id': pr_data.get('contributed_github_id'),
                            'title': pr_data.get('title'),
                            'requester_id': pr_data.get('requester_id'),
                            'created_at': parse_github_timestamp(pr_data.get('created_at')),
                            'closed_at': parse_github_timestamp(pr_data.get('closed_at')),
                            'merged_at': parse_github_timestamp(pr_data.get('merged_at')),
                            'merged_by': pr_data.get('merged_by'),
                            'published_date': pr_data.get('published_date'),
                            'state': pr_data.get('state'),
                            'last_update': pr_data.get('last_update')
                        }
                    )

                success_repo_count += 1
                print(f'  [SUCCESS] Finished processing PRs for repo: {repo_name}.')

            except Exception as e:
                # Log the error for the specific repository and continue with the next one.
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        # 4. Return a summary of the entire synchronization process.
        return JsonResponse({
            "status": "OK",
            "message": "Repo PRs synchronization completed.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle fatal errors that prevent the script from starting or running properly.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------PR READ--------------#
def repo_pr_read_db(request):
    try:
        # 1. Fetch all pull request data directly as a list of dictionaries.
        # Using .values() is more efficient than fetching full model instances
        # because it performs the data selection at the database level.
        pr_list = list(Repo_pr.objects.values(
            'id',
            'repo_id',
            'pr_number',
            'repo_url',
            'owner_github_id',
            'title',
            'requester_id',
            'created_at',
            'closed_at',
            'merged_at',
            'merged_by',
            'published_date',
            'state',
            'last_update'
        ))
        
        # 2. Return the list of pull requests as a JSON response.
        return JsonResponse(pr_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the database query.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------COMMIT--------------#
def sync_repo_commit_db(request):
    # 1. Initialization
    # Initialize counters and lists to track the outcome of the sync process.
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []

    try:
        # 2. Fetch all repositories from the database.
        repositories, filter_summary = get_repositories_for_sync(request, 'commit')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)

        # 3. Iterate through each repository to sync its commits.
        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{total_repo_count}] Syncing commits for repo: {repo_name} {"="*10}')

            # Use a try-except block for each repo to prevent one failure from stopping the entire process.
            try:
                # 3a. Find the last update timestamp to fetch only new commits.
                latest_commit = Repo_commit.objects.filter(repo_id=repo_id).order_by('-last_update').first()
                since = latest_commit.last_update if latest_commit else "2008-01-01T00:00:00Z"

                # 3b. Fetch commit data from the API.
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/commit",
                    params={
                        'github_id': github_id,
                        'repo_name': repo_name,
                        'since': since,
                        'include_files': True,
                    }
                )
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                commit_data_list = response.json()

                if not isinstance(commit_data_list, list):
                    raise ValueError("Invalid response format: API did not return a list.")

                if not commit_data_list:
                    print(f"  No new commits to update for repo: {repo_name}.")
                    success_repo_count += 1
                    continue
                
                print(f"  Found {len(commit_data_list)} new/updated commit(s) to process.")

                # 3c. Process and save each commit from the API response.
                for commit_data in commit_data_list:
                    # `update_or_create` finds a record by its unique key ('sha').
                    # If it exists, it's updated. If not, it's created.
                    _, created = Repo_commit.objects.update_or_create(
                        sha=commit_data.get('sha'),
                        defaults={
                            'repo_id': repo_id,
                            'repo_url': commit_data.get('repository_url'),
                            'owner_github_id': commit_data.get('contributed_github_id'),
                            'author_github_id': commit_data.get('author_github_id'),
                            'added_lines': commit_data.get('added_lines'),
                            'deleted_lines': commit_data.get('deleted_lines'),
                            'committed_at': parse_github_timestamp(commit_data.get('committed_at') or commit_data.get('last_update')),
                            'last_update': commit_data.get('last_update')
                        }
                    )
                    sync_commit_file_changes(repo_id, commit_data)

                success_repo_count += 1
                print(f'  [SUCCESS] Finished processing commits for repo: {repo_name}.')

            except Exception as e:
                # Log the error for the specific repository and continue with the next one.
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        # 4. Return a summary of the entire synchronization process.
        return JsonResponse({
            "status": "OK",
            "message": "Repo commits synchronization completed.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        # Handle fatal errors that prevent the script from starting or running properly.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------COMMIT READ--------------#
def repo_commit_read_db(request):
    try:
        # 1. Fetch all commit data directly as a list of dictionaries.
        # Using .values() is more efficient than fetching full model instances
        # and converting them in Python, as it performs the conversion at the database level.
        commit_list = list(Repo_commit.objects.values(
            'sha',
            'repo_id',
            'repo_url',
            'owner_github_id',
            'author_github_id',
            'added_lines',
            'deleted_lines',
            'committed_at',
            'last_update'
        ))
        
        # 2. Return the list of commits as a JSON response.
        return JsonResponse(commit_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the database query.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------


def sync_commit_file_changes(repo_id, commit_data):
    files = commit_data.get('files') or []
    if not isinstance(files, list):
        return 0

    synced_count = 0
    committed_at = parse_github_timestamp(commit_data.get('committed_at') or commit_data.get('last_update'))
    sha = commit_data.get('sha')
    if not sha:
        return synced_count

    for file_data in files:
        path = file_data.get('path')
        if not path:
            continue
        RepoCommitFileChange.objects.update_or_create(
            repo_id=repo_id,
            sha=sha,
            path=path,
            defaults={
                'committed_at': parse_github_timestamp(file_data.get('committed_at')) or committed_at,
                'filename': file_data.get('filename'),
                'extension': file_data.get('extension'),
                'status': file_data.get('status'),
                'additions': file_data.get('additions'),
                'deletions': file_data.get('deletions'),
                'changes': file_data.get('changes'),
                'is_workflow_yaml': bool(file_data.get('is_workflow_yaml')),
                'is_test_file': bool(file_data.get('is_test_file')),
                'is_readme': bool(file_data.get('is_readme')),
                'is_dependency_manifest': bool(file_data.get('is_dependency_manifest')),
            }
        )
        synced_count += 1
    return synced_count


def sync_repo_snapshot_db(request):
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []

    try:
        repositories, filter_summary = get_repositories_for_sync(request, 'snapshot')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]

        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{len(repo_list)}] Syncing 2026 snapshot for repo: {repo_name} {"="*10}')

            try:
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/snapshot",
                    params={'github_id': github_id, 'repo_name': repo_name},
                    timeout=120,
                )
                response.raise_for_status()
                snapshot_data = response.json()

                RepositorySnapshot.objects.create(
                    repo_id=repo_id,
                    collected_at=parse_github_timestamp(snapshot_data.get('collected_at')) or timezone_now(),
                    default_branch=snapshot_data.get('default_branch'),
                    branch_count=snapshot_data.get('branch_count'),
                    language_bytes=snapshot_data.get('language_bytes') or {},
                    language_percentage=snapshot_data.get('language_percentage') or {},
                    workflow_yaml_count=snapshot_data.get('workflow_yaml_count'),
                    workflow_yaml_total_size=snapshot_data.get('workflow_yaml_total_size'),
                    workflow_yaml_paths=snapshot_data.get('workflow_yaml_paths') or [],
                    has_readme=snapshot_data.get('has_readme'),
                    readme_dependency_mentioned=snapshot_data.get('readme_dependency_mentioned'),
                    dependency_evidence=snapshot_data.get('dependency_evidence') or {},
                    dependabot_config_present=snapshot_data.get('dependabot_config_present'),
                )

                Repository.objects.filter(id=repo_id).update(
                    default_branch=snapshot_data.get('default_branch'),
                    language_bytes=snapshot_data.get('language_bytes') or {},
                    language_percentage=snapshot_data.get('language_percentage') or {},
                    has_readme=snapshot_data.get('has_readme'),
                )
                success_repo_count += 1

            except Exception as e:
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        return JsonResponse({
            "status": "OK",
            "message": "Repository 2026 snapshots synchronized.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details,
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def repo_snapshot_read_db(request):
    try:
        snapshot_list = list(RepositorySnapshot.objects.values(
            'id',
            'repo_id',
            'collected_at',
            'default_branch',
            'branch_count',
            'language_bytes',
            'language_percentage',
            'workflow_yaml_count',
            'workflow_yaml_total_size',
            'workflow_yaml_paths',
            'has_readme',
            'readme_dependency_mentioned',
            'dependency_evidence',
            'dependabot_config_present',
        ))
        return JsonResponse(snapshot_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def repo_commit_file_change_read_db(request):
    try:
        file_change_list = list(RepoCommitFileChange.objects.values(
            'id',
            'repo_id',
            'sha',
            'committed_at',
            'path',
            'filename',
            'extension',
            'status',
            'additions',
            'deletions',
            'changes',
            'is_workflow_yaml',
            'is_test_file',
            'is_readme',
            'is_dependency_manifest',
        ))
        return JsonResponse(file_change_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def sync_repo_review_comment_db(request):
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []
    success_comment_count = 0

    try:
        repositories, filter_summary = get_repositories_for_sync(request, 'review_comment')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]

        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            latest_comment = RepoReviewComment.objects.filter(repo_id=repo_id).order_by('-updated_at').first()
            since = github_timestamp_for_api(latest_comment.updated_at if latest_comment else None)
            print(f'\n{"="*10} [{i}/{len(repo_list)}] Syncing review comments for repo: {repo_name} {"="*10}')

            try:
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/review-comments",
                    params={'github_id': github_id, 'repo_name': repo_name, 'since': since},
                    timeout=600,
                )
                response.raise_for_status()
                comment_data_list = response.json()
                if not isinstance(comment_data_list, list):
                    raise ValueError("Invalid response format: API did not return a list.")

                for comment_data in comment_data_list:
                    comment_id = comment_data.get('comment_id')
                    comment_type = comment_data.get('comment_type')
                    if not comment_id or not comment_type:
                        continue

                    RepoReviewComment.objects.update_or_create(
                        comment_type=comment_type,
                        comment_id=comment_id,
                        defaults={
                            'repo_id': repo_id,
                            'pr_id': comment_data.get('pr_id'),
                            'pr_number': comment_data.get('pr_number'),
                            'author_github_id': comment_data.get('author_github_id'),
                            'created_at': parse_github_timestamp(comment_data.get('created_at')),
                            'updated_at': parse_github_timestamp(comment_data.get('updated_at')),
                            'path': comment_data.get('path'),
                            'position': comment_data.get('position'),
                            'state': comment_data.get('state'),
                        }
                    )
                    success_comment_count += 1

                success_repo_count += 1

            except Exception as e:
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        return JsonResponse({
            "status": "OK",
            "message": "Repository review comments synchronized.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "success_comment_count": success_comment_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details,
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def repo_review_comment_read_db(request):
    try:
        comment_list = list(RepoReviewComment.objects.values(
            'id',
            'repo_id',
            'pr_id',
            'pr_number',
            'comment_id',
            'author_github_id',
            'created_at',
            'updated_at',
            'path',
            'position',
            'comment_type',
            'state',
        ))
        return JsonResponse(comment_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def sync_repo_dependabot_alert_db(request):
    success_repo_count = 0
    failure_repo_count = 0
    failure_repo_details = []
    success_alert_count = 0

    try:
        repositories, filter_summary = get_repositories_for_sync(request, 'dependabot_alert')
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]

        for i, repo in enumerate(repo_list, 1):
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            print(f'\n{"="*10} [{i}/{len(repo_list)}] Syncing Dependabot alerts for repo: {repo_name} {"="*10}')

            try:
                response = requests.get(
                    f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/dependabot-alerts",
                    params={'github_id': github_id, 'repo_name': repo_name},
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get('error'):
                    print(f"  [WARN] Dependabot alerts unavailable for {repo_name}: {payload.get('message')}")
                    success_repo_count += 1
                    continue

                alert_data_list = payload.get('alerts') or []
                if not isinstance(alert_data_list, list):
                    raise ValueError("Invalid response format: API did not return an alerts list.")

                for alert_data in alert_data_list:
                    alert_number = alert_data.get('github_alert_number')
                    if alert_number is None:
                        continue

                    RepoDependabotAlert.objects.update_or_create(
                        repo_id=repo_id,
                        github_alert_number=alert_number,
                        defaults={
                            'state': alert_data.get('state'),
                            'package_name': alert_data.get('package_name'),
                            'ecosystem': alert_data.get('ecosystem'),
                            'manifest_path': alert_data.get('manifest_path'),
                            'severity': alert_data.get('severity'),
                            'created_at': parse_github_timestamp(alert_data.get('created_at')),
                            'fixed_at': parse_github_timestamp(alert_data.get('fixed_at')),
                            'dismissed_at': parse_github_timestamp(alert_data.get('dismissed_at')),
                            'collected_at': parse_github_timestamp(alert_data.get('collected_at')) or timezone_now(),
                        }
                    )
                    success_alert_count += 1

                success_repo_count += 1

            except Exception as e:
                message = f"Failed to process repo {repo_name} (ID: {repo_id}): {str(e)}"
                print(f"  [ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

        return JsonResponse({
            "status": "OK",
            "message": "Repository Dependabot alerts synchronized.",
            "sync_scope": filter_summary['sync_scope'],
            "candidate_repo_count": filter_summary['candidate_repo_count'],
            "skipped_repo_count": filter_summary['skipped_repo_count'],
            "skipped_repo_sample": filter_summary['skipped_repo_sample'],
            "success_repo_count": success_repo_count,
            "success_alert_count": success_alert_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details,
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def repo_dependabot_alert_read_db(request):
    try:
        alert_list = list(RepoDependabotAlert.objects.values(
            'id',
            'repo_id',
            'github_alert_number',
            'state',
            'package_name',
            'ecosystem',
            'manifest_path',
            'severity',
            'created_at',
            'fixed_at',
            'dismissed_at',
            'collected_at',
        ))
        return JsonResponse(alert_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

# ------------Course_reated REPO READ--------------#
def repo_course_read_db(request):
    try:
        # 1. Get the IDs of all repositories that are linked to a course project.
        course_project_repo_ids = Course_project.objects.values_list('repo_id', flat=True)

        # 2. Fetch the repository data, annotating each with its pull request count.
        # This is highly efficient as it avoids making a separate DB query for each repo (N+1 problem).
        # The Count('repo_pr') calculates the number of related pull requests in the database.
        repo_list = Repository.objects.filter(id__in=course_project_repo_ids).annotate(
            pr_count=Count('repo_pr')
        )

        # 3. Format the data for the JSON response.
        data = []
        for r in repo_list:
            # Calculate contributor count from the comma-separated string.
            contributors_count = len(r.contributors.split(",")) if r.contributors else 0
            
            repo_info = {
                'id': r.id,
                'name': r.name,
                'url': r.url,
                'owner_github_id': r.owner_github_id,
                'default_branch': r.default_branch,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
                'fork_count': r.fork_count,
                'star_count': r.star_count,
                'commit_count': r.commit_count,
                'total_issue_count': int(r.open_issue_count) + int(r.closed_issue_count),
                'pr_count': r.pr_count,  # This value comes directly from the annotated query.
                'language': r.language,
                'contributors': contributors_count,
                'license': r.license,
                'has_readme': r.has_readme,
                'description': r.description,
                'release_version': r.release_version
            }
            data.append(repo_info)
            
        # 4. Return the complete list as a JSON response.
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the process.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ----------------------------------------------------- 

# ========================================
# Test Function
# ========================================
# ------------Repo Test--------------#
def sync_repo_db_test(request, student_id):
    print("-"*20)
    try:
        # 특정 학생 가져오기
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing GitHub user: {github_id} (Student ID: {student_id})")

        # FastAPI로부터 학생의 저장소 정보 가져오기
        response = requests.get(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
            params={'github_id': github_id}
        )
        
        if response.status_code != 200:
            message = f"Failed to fetch repositories for GitHub user {github_id}"
            print(f"[ERROR] {message}")
            return JsonResponse({"status": "Error", "message": message}, status=500)

        data = response.json()
        if not isinstance(data, list):
            message = f"Invalid response format for repositories of GitHub user {github_id}"
            print(f"[ERROR] {message}")
            return JsonResponse({"status": "Error", "message": message}, status=500)

        # 저장소 목록
        total_repo_count = len(data)
        repo_list = [{'id': repo['id'], 'name': repo['name']} for repo in data]
        print(f"Total repositories to process for {github_id}: {total_repo_count}")

        # 현재 DB에 저장된 저장소 목록과 비교
        repos_in_db = Repository.objects.filter(owner_github_id=github_id).values_list('id', flat=True)
        repos_in_db_sorted = sorted(repos_in_db)  # Sort the DB repository IDs in ascending order
        print(f"DB: {repos_in_db_sorted}")

        repo_ids_in_list = sorted([str(repo['id']) for repo in repo_list])  # Sort the list of IDs in ascending order
        print(f"FASTAPI: {repo_ids_in_list}")

        # DB와 FASTAPI 데이터를 비교하여 DB에는 있지만 FASTAPI에는 없는 값 찾기
        missing_in_fastapi = set(repos_in_db) - set(repo_ids_in_list)

        # 결과 출력
        print(f"DB에만 있는 값: {missing_in_fastapi}")

        
        # 기존에 없어진 저장소 삭제
        for repo_id in repos_in_db:
            if repo_id not in repo_ids_in_list:
                remove_repository(github_id, Repository(id=repo_id))
                print(f"Repository {repo_id} removed for GitHub ID: {github_id}")

        # 저장소 업데이트 또는 생성
        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        for index, repo in enumerate(repo_list, start=1):
            repo_name = repo['name']
            repo_id = repo['id']
            print(f"Processing repository [{index}/{total_repo_count}]: {repo_name} (ID: {repo_id})")
            
            repo_response = requests.get(
                f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos",
                params={'github_id': github_id, 'repo_id': repo_id}
            )
            
            if repo_response.status_code != 200:
                message = f"Failed to fetch data for repo {repo_id} of GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_id": repo_id, "message": message})
                continue

            repo_data = repo_response.json()
            print(repo_data)
            try:
                repository_record, created = Repository.objects.update_or_create(
                    owner_github_id=github_id,
                    id=repo_id,
                    defaults={
                        'name': repo_name,
                        'url': repo_data.get('url'),
                        'created_at': repo_data.get('created_at'),
                        'updated_at': repo_data.get('updated_at'),
                        'forked': repo_data.get('forked'),
                        'fork_count': repo_data.get('forks_count'),
                        'star_count': repo_data.get('stars_count'),
                        'commit_count': repo_data.get('commit_count'),
                        'open_issue_count': repo_data.get('open_issue_count'),
                        'closed_issue_count': repo_data.get('closed_issue_count'),
                        'open_pr_count': repo_data.get('open_pr_count'),
                        'closed_pr_count': repo_data.get('closed_pr_count'),
                        'contributed_commit_count': repo_data.get('contributed_commit_count'),
                        'contributed_open_issue_count': repo_data.get('contributed_open_issue_count'),
                        'contributed_closed_issue_count': repo_data.get('contributed_closed_issue_count'),
                        'contributed_open_pr_count': repo_data.get('contributed_open_pr_count'),
                        'contributed_closed_pr_count': repo_data.get('contributed_closed_pr_count'),
                        'language': ', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None',
                        'contributors': ', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None',
                        'license': repo_data.get('license'),
                        'has_readme': repo_data.get('has_readme'),
                        'description': repo_data.get('description'),
                        'release_version': repo_data.get('release_version'),
                        'crawled_date': repo_data.get('crawled_date'),
                    }
                )
                action = "Created" if created else "Updated"
                print(f"{action} repository: {repo_name} (ID: {repo_id})")
                success_repo_count += 1

            except Exception as e:
                message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                print(f"[ERROR] {message}")
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

        # 학생의 전체 star count 계산
        total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count'] or 0
        student.starred_count = total_star_count
        student.save()

        print(f"Total star count ({total_star_count}) for GitHub user {github_id} saved.")

        # 결과값 반환
        return JsonResponse({
            "status": "OK",
            "message": f"Repositories for GitHub user {github_id} updated successfully",
            "total_repositories": total_repo_count,
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Student.DoesNotExist:
        return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------Contributor Test--------------#
def sync_repo_contributor_db_test(request, student_id):
    print("-" * 20)
    try:
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing GitHub user: {github_id} (Student ID: {student_id})")

        response = requests.get(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
            params={'github_id': github_id}
        )
        if response.status_code != 200:
            return JsonResponse({"status": "Error", "message": "Failed to fetch repositories"}, status=500)

        data = response.json()
        if not isinstance(data, list):
            return JsonResponse({"status": "Error", "message": "Invalid response format"}, status=500)

        contributor_count_per_repo = {}
        success_contributor_count = 0
        failure_contributor_count = 0
        failure_contributor_details = []

        for repo in data:
            repo_id = repo['id']
            repo_name = repo['name']
            print(f"Processing contributors for repository: {repo_name} (ID: {repo_id})")

            response = requests.get(
                f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/contributor",
                params={'github_id': github_id, 'repo_name': repo_name}
            )
            if response.status_code != 200:
                failure_contributor_count += 1
                failure_contributor_details.append({"repo_id": repo_id, "repo_name": repo_name})
                continue

            contributor_data = response.json()
            contributor_count = 0

            for contributor in contributor_data:
                contributor_count += 1
                try:
                    Repo_contributor.objects.update_or_create(
                        owner_github_id=github_id,
                        repo_id=repo_id,
                        contributor_id=contributor.get('login'),
                        defaults={
                            'contribution_count': contributor.get('contributions'),
                            'repo_url': contributor.get('repo_url')
                        }
                    )
                    success_contributor_count += 1
                except Exception:
                    failure_contributor_count += 1

            contributor_count_per_repo[repo_name] = contributor_count
            
        print(contributor_count_per_repo)
        return JsonResponse({
            "status": "OK",
            "contributors_per_repo": contributor_count_per_repo,
            "success_contributor_count": success_contributor_count,
            "failure_contributor_count": failure_contributor_count,
            "failure_contributor_details": failure_contributor_details
        })

    except Student.DoesNotExist:
        return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------Issue Test--------------#
def sync_repo_issue_db_test(request, student_id):
    print("-" * 20)
    try:
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing GitHub user: {github_id} (Student ID: {student_id})")

        response = requests.get(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
            params={'github_id': github_id}
        )
        if response.status_code != 200:
            return JsonResponse({"status": "Error", "message": "Failed to fetch repositories"}, status=500)

        data = response.json()
        if not isinstance(data, list):
            return JsonResponse({"status": "Error", "message": "Invalid response format"}, status=500)

        issue_count_per_repo = {}
        success_issue_count = 0
        failure_issue_count = 0
        failure_issue_details = []

        for repo in data:
            repo_id = repo['id']
            repo_name = repo['name']
            print(f"Processing issues for repository: {repo_name} (ID: {repo_id})")

            response = requests.get(
                f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/issues",
                params={'github_id': github_id, 'repo_name': repo_name}
            )
            if response.status_code != 200:
                failure_issue_count += 1
                failure_issue_details.append({"repo_id": repo_id, "repo_name": repo_name})
                continue

            issue_data = response.json()
            issue_count = 0

            for issue in issue_data:
                issue_count += 1
                try:
                    Repo_issue.objects.update_or_create(
                        id=issue.get('id'),
                        defaults={
                            'repo_id': repo_id,
                            'state': issue.get('state'),
                            'title': issue.get('title'),
                            'publisher_github_id': issue.get('publisher_github_id'),
                            'last_update': issue.get('last_update')
                        }
                    )
                    success_issue_count += 1
                except Exception:
                    failure_issue_count += 1

            issue_count_per_repo[repo_name] = issue_count
            
        print(issue_count_per_repo)
        return JsonResponse({
            "status": "OK",
            "issues_per_repo": issue_count_per_repo,
            "success_issue_count": success_issue_count,
            "failure_issue_count": failure_issue_count,
            "failure_issue_details": failure_issue_details
        })

    except Student.DoesNotExist:
        return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------PR Test--------------#
def sync_repo_pr_db_test(request, student_id):
    print("-" * 20)
    try:
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing GitHub user: {github_id} (Student ID: {student_id})")

        response = requests.get(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
            params={'github_id': github_id}
        )
        if response.status_code != 200:
            return JsonResponse({"status": "Error", "message": "Failed to fetch repositories"}, status=500)

        data = response.json()
        if not isinstance(data, list):
            return JsonResponse({"status": "Error", "message": "Invalid response format"}, status=500)

        pr_count_per_repo = {}
        success_pr_count = 0
        failure_pr_count = 0
        failure_pr_details = []

        for repo in data:
            repo_id = repo['id']
            repo_name = repo['name']
            print(f"Processing PRs for repository: {repo_name} (ID: {repo_id})")

            response = requests.get(
                f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/pulls",
                params={'github_id': github_id, 'repo_name': repo_name}
            )
            if response.status_code != 200:
                failure_pr_count += 1
                failure_pr_details.append({"repo_id": repo_id, "repo_name": repo_name})
                continue

            pr_data = response.json()
            pr_count = 0

            for pr in pr_data:
                pr_count += 1
                try:
                    Repo_pr.objects.update_or_create(
                        id=pr.get('id'),
                        defaults={
                            'repo_id': repo_id,
                            'state': pr.get('state'),
                            'title': pr.get('title'),
                            'requester_id': pr.get('requester_id'),
                            'last_update': pr.get('last_update')
                        }
                    )
                    success_pr_count += 1
                except Exception:
                    failure_pr_count += 1

            pr_count_per_repo[repo_name] = pr_count
            
        print(pr_count_per_repo)
        return JsonResponse({
            "status": "OK",
            "prs_per_repo": pr_count_per_repo,
            "success_pr_count": success_pr_count,
            "failure_pr_count": failure_pr_count,
            "failure_pr_details": failure_pr_details
        })

    except Student.DoesNotExist:
        return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------commit Test--------------#
def sync_repo_commit_db_test(request, student_id):
    print("-" * 20)
    try:
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing GitHub user: {github_id} (Student ID: {student_id})")

        response = requests.get(
            f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos",
            params={'github_id': github_id}
        )
        if response.status_code != 200:
            return JsonResponse({"status": "Error", "message": "Failed to fetch repositories"}, status=500)

        data = response.json()
        if not isinstance(data, list):
            return JsonResponse({"status": "Error", "message": "Invalid response format"}, status=500)

        commit_count_per_repo = {}
        success_commit_count = 0
        failure_commit_count = 0
        failure_commit_details = []

        for repo in data:
            repo_id = repo['id']
            repo_name = repo['name']
            print(f"Processing commits for repository: {repo_name} (ID: {repo_id})")

            response = requests.get(
                f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/commit",
                params={'github_id': github_id, 'repo_name': repo_name}
            )
            if response.status_code != 200:
                failure_commit_count += 1
                failure_commit_details.append({"repo_id": repo_id, "repo_name": repo_name})
                continue

            commit_data = response.json()
            commit_count = 0

            for commit in commit_data:
                commit_count += 1
                try:
                    Repo_commit.objects.update_or_create(
                        sha=commit.get('sha'),
                        defaults={
                            'repo_id': repo_id,
                            'author_github_id': commit.get('author_github_id'),
                            'added_lines': commit.get('added_lines'),
                            'deleted_lines': commit.get('deleted_lines'),
                            'last_update': commit.get('last_update')
                        }
                    )
                    success_commit_count += 1
                except Exception:
                    failure_commit_count += 1

            commit_count_per_repo[repo_name] = commit_count
            
        print(commit_count_per_repo)
        return JsonResponse({
            "status": "OK",
            "commits_per_repo": commit_count_per_repo,
            "success_commit_count": success_commit_count,
            "failure_commit_count": failure_commit_count,
            "failure_commit_details": failure_commit_details
        })

    except Student.DoesNotExist:
        return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

#-----------------------------------------------READ DB per ACCOUNT-----------------------------------------------#
# ------------REPO READ per ACCOUNT--------------#
@csrf_exempt
def repo_account_read_db(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)

        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            uuid = body_data.get('uuid')
            student_id = body_data.get('student_num')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"status": "Error", "message": "Invalid JSON format or character encoding"}, status=400)
        
        if not uuid:
            return JsonResponse({"status": "Error", "message": "uuid is required in the request body"}, status=400)

        try:
            if (uuid == 'empty'):
                student = Student.objects.get(id=student_id)
            
            elif (uuid != 'empty'):
                login_student = LoginStudent.objects.get(member_id=uuid)
                student_id = login_student.id
                student = Student.objects.get(id=student_id)

            github_id = student.github_id
            student_id = student.id
            student_name = student.name
            student_primary_email = student.primary_email
            student_department = student.department
            
            # 1) 모든 레포지토리를 한 번에 로드 (owner + contributor)
            owner_repo_list = Repository.objects.filter(owner_github_id=github_id).prefetch_related(
                'repo_pr_set', 'repo_issue_set'
            )
            contributor_repo_list = Repository.objects.filter(contributors__icontains=github_id).prefetch_related(
                'repo_pr_set', 'repo_issue_set'
            )
            owner_contributor_repo_list = (owner_repo_list | contributor_repo_list).distinct()
            
            # 전체 언어 비율 처리
            if isinstance(student.total_language_percentage, dict) and student.total_language_percentage:
                sorted_total_language_percentages = sorted(student.total_language_percentage.items(), key=itemgetter(1), reverse=True)
                top_5_total_language_percentages = dict(sorted_total_language_percentages[:5])
                other_total_languages_percentage = sum(value for key, value in sorted_total_language_percentages[5:])
                top_5_total_language_percentages['others'] = round(other_total_languages_percentage, 1)
            else: 
                top_5_total_language_percentages = []
           
        except LoginStudent.DoesNotExist:
            return JsonResponse({"status": "Error", "message": f"Login student not found for uuid: {uuid}"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"status": "Error", "message": f"Account student not found for id: {student_id}"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "Error", "message": f"Error resolving uuid to github_id: {str(e)}"}, status=500)
        
        if not owner_repo_list.exists() and not contributor_repo_list.exists():
            return JsonResponse({"status": "Error", "message": f"No repositories found for github_id: {github_id}"}, status=404)

        owner_repo_ids = list(owner_repo_list.values_list('id', flat=True))
        contributor_repo_ids = list(contributor_repo_list.values_list('id', flat=True))
        all_repo_ids = list(set(owner_repo_ids + contributor_repo_ids))

        latest_snapshots_by_repo = {}
        for snapshot in RepositorySnapshot.objects.filter(repo_id__in=all_repo_ids).order_by('repo_id', '-collected_at'):
            if snapshot.repo_id not in latest_snapshots_by_repo:
                latest_snapshots_by_repo[snapshot.repo_id] = snapshot

        file_metrics_by_repo = {
            row['repo_id']: row
            for row in RepoCommitFileChange.objects.filter(repo_id__in=all_repo_ids).values('repo_id').annotate(
                workflow_yaml_commit_count=Count('id', filter=Q(is_workflow_yaml=True)),
                test_file_commit_count=Count('id', filter=Q(is_test_file=True)),
                dependency_manifest_commit_count=Count('id', filter=Q(is_dependency_manifest=True)),
            )
        }
        repeated_file_modifications_by_repo = {}
        repeated_rows = RepoCommitFileChange.objects.filter(repo_id__in=all_repo_ids).values(
            'repo_id',
            'path',
        ).annotate(change_count=Count('id')).filter(change_count__gt=1)
        for row in repeated_rows:
            repeated_file_modifications_by_repo[row['repo_id']] = repeated_file_modifications_by_repo.get(row['repo_id'], 0) + 1

        review_metrics_by_repo = {
            row['repo_id']: row
            for row in RepoReviewComment.objects.filter(repo_id__in=all_repo_ids).values('repo_id').annotate(
                review_count=Count('id', filter=Q(comment_type='review')),
                review_diff_comment_count=Count('id', filter=Q(comment_type='comment')),
                review_comment_count=Count('id'),
            )
        }
        dependabot_metrics_by_repo = {
            row['repo_id']: row
            for row in RepoDependabotAlert.objects.filter(repo_id__in=all_repo_ids).values('repo_id').annotate(
                dependabot_alert_count=Count('id'),
                open_dependabot_alert_count=Count('id', filter=Q(state='open')),
            )
        }
        
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        # 2) 모든 커밋을 한 번에 로드 (repo_id로 인덱싱)
        all_commits = Repo_commit.objects.filter(
            repo_id__in=all_repo_ids
        ).select_related('repo')
        
        # 커밋을 메모리에서 분류
        commits_by_repo = {}
        for commit in all_commits:
            repo_id = commit.repo.id
            if repo_id not in commits_by_repo:
                commits_by_repo[repo_id] = []
            commits_by_repo[repo_id].append(commit)

        # 3) 전체 통계 계산 (DB aggregation)
        all_commit_stats = all_commits.aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        
        owner_commit_stats = all_commits.filter(
            repo_id__in=owner_repo_ids,
            author_github_id=github_id
        ).aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        
        contributor_commit_stats = all_commits.filter(
            repo_id__in=contributor_repo_ids,
            author_github_id=github_id
        ).aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        
        total_stats = {
            'all_total_commits': all_commit_stats.get('total_commits', 0) or 0,
            'all_added_lines': all_commit_stats.get('added_lines', 0) or 0,
            'all_deleted_lines': all_commit_stats.get('deleted_lines', 0) or 0,
            'all_total_changed_lines': (all_commit_stats.get('added_lines', 0) or 0) + (all_commit_stats.get('deleted_lines', 0) or 0),
            'owner_total_commits': owner_commit_stats.get('total_commits', 0) or 0,
            'owner_added_lines': owner_commit_stats.get('added_lines', 0) or 0,
            'owner_deleted_lines': owner_commit_stats.get('deleted_lines', 0) or 0,
            'owner_total_changed_lines': (owner_commit_stats.get('added_lines', 0) or 0) + (owner_commit_stats.get('deleted_lines', 0) or 0),
            'contributor_total_commits': contributor_commit_stats.get('total_commits', 0) or 0,
            'contributor_added_lines': contributor_commit_stats.get('added_lines', 0) or 0,
            'contributor_deleted_lines': contributor_commit_stats.get('deleted_lines', 0) or 0,
            'contributor_total_changed_lines': (contributor_commit_stats.get('added_lines', 0) or 0) + (contributor_commit_stats.get('deleted_lines', 0) or 0),
        }

        # 4) 월별/히트맵 데이터 초기화
        monthly_commit_counts = {}
        monthly_added_lines = {}
        monthly_deleted_lines = {}
        monthly_changed_lines = {}
        repo_monthly_commits = {repo.id: {} for repo in owner_contributor_repo_list}
        
        days_of_week = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        heatmap_data = {day: {str(hour): 0 for hour in range(24)} for day in days_of_week.values()}
        
        # 5) 커밋 데이터 집계 (한 번만 순회)
        for commit in all_commits:
            if commit.author_github_id != github_id:
                continue
                
            try:
                commit_datetime = datetime.strptime(commit.last_update, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, TypeError):
                continue
            
            if commit_datetime >= one_year_ago:
                month_key = commit_datetime.strftime('%Y-%m')
                added = commit.added_lines if commit.added_lines is not None else 0
                deleted = commit.deleted_lines if commit.deleted_lines is not None else 0

                monthly_commit_counts[month_key] = monthly_commit_counts.get(month_key, 0) + 1
                monthly_added_lines[month_key] = monthly_added_lines.get(month_key, 0) + added
                monthly_deleted_lines[month_key] = monthly_deleted_lines.get(month_key, 0) + deleted
                monthly_changed_lines[month_key] = monthly_changed_lines.get(month_key, 0) + added + deleted

                weekday_index = commit_datetime.weekday()
                hour = commit_datetime.hour
                day_name = days_of_week[weekday_index]
                heatmap_data[day_name][str(hour)] += 1
        
        # 6) repo별 월별 커밋 계산
        for repo in owner_contributor_repo_list:
            repo_commits = commits_by_repo.get(repo.id, [])
            repo_user_commits = [c for c in repo_commits if c.author_github_id == github_id]
            
            if not repo_user_commits:
                continue
                
            latest_commit_date = max(
                (datetime.strptime(c.last_update, '%Y-%m-%dT%H:%M:%SZ') 
                 for c in repo_user_commits if c.last_update),
                default=datetime.now()
            )
            repo_one_year_ago = latest_commit_date - timedelta(days=365)
            
            for commit in repo_user_commits:
                try:
                    commit_datetime = datetime.strptime(commit.last_update, '%Y-%m-%dT%H:%M:%SZ')
                    if commit_datetime >= repo_one_year_ago:
                        month_key = commit_datetime.strftime('%Y-%m')
                        repo_monthly_commits[repo.id][month_key] = repo_monthly_commits[repo.id].get(month_key, 0) + 1
                except (ValueError, TypeError):
                    continue

        # 데이터 정렬
        sorted_commit_counts = sorted(monthly_commit_counts.items())
        sorted_added_lines = sorted(monthly_added_lines.items())
        sorted_deleted_lines = sorted(monthly_deleted_lines.items())
        sorted_changed_lines = sorted(monthly_changed_lines.items())

        # 7) 레포지토리별 상세 정보 (이미 prefetch된 데이터 사용)
        total_open_issue_count = 0
        total_closed_issue_count = 0
        owner_open_issue_count = 0
        owner_closed_issue_count = 0
        total_open_pr_count = 0
        total_closed_pr_count = 0
        owner_open_pr_count = 0
        owner_closed_pr_count = 0
        total_star_count = 0
        total_fork_count = 0
        total_contributors_count = {'1':0, '2':0, '3':0, '4':0, '5+':0}

        data = []
        for r in owner_contributor_repo_list:
            # 이미 prefetch된 데이터 사용
            repo_commits = commits_by_repo.get(r.id, [])
            repo_user_commit_count = len([c for c in repo_commits if c.author_github_id == github_id])
            
            # prefetch된 PR/Issue 사용
            repo_prs = list(r.repo_pr_set.all())
            repo_issues = list(r.repo_issue_set.all())
            
            repo_total_open_pr_count = len([pr for pr in repo_prs if pr.state == 'open'])
            repo_total_closed_pr_count = len([pr for pr in repo_prs if pr.state == 'closed'])
            repo_owner_open_pr_count = len([pr for pr in repo_prs if pr.requester_id == github_id and pr.state == 'open'])
            repo_owner_closed_pr_count = len([pr for pr in repo_prs if pr.requester_id == github_id and pr.state == 'closed'])
            
            repo_total_open_issue_count = len([issue for issue in repo_issues if issue.state == 'open'])
            repo_total_closed_issue_count = len([issue for issue in repo_issues if issue.state == 'closed'])
            repo_owner_open_issue_count = len([issue for issue in repo_issues if issue.publisher_github_id == github_id and issue.state == 'open'])
            repo_owner_closed_issue_count = len([issue for issue in repo_issues if issue.publisher_github_id == github_id and issue.state == 'closed'])
            
            contributors_list = r.contributors.split(",") if r.contributors else []
            contributors_count = len([c for c in contributors_list if c.strip()])

            total_open_pr_count += repo_total_open_pr_count
            total_closed_pr_count += repo_total_closed_pr_count
            owner_open_pr_count += repo_owner_open_pr_count
            owner_closed_pr_count += repo_owner_closed_pr_count
            total_open_issue_count += repo_total_open_issue_count
            total_closed_issue_count += repo_total_closed_issue_count
            owner_open_issue_count += repo_owner_open_issue_count
            owner_closed_issue_count += repo_owner_closed_issue_count
            total_star_count += r.star_count
            total_fork_count += r.fork_count

            # Contributors 정보
            if contributors_count == 0:
                contributors_total_info = []
            else:
                contributors_total_info = []
                for specific_contributor in contributors_list:
                    contributor_student_info = []
                    specific_contributor_trim = str(specific_contributor).strip()
                    if not specific_contributor_trim:
                        continue
                    try:
                        contributor_student = Student.objects.get(github_id=specific_contributor_trim)
                        contributor_student_info.extend([
                            contributor_student.name,
                            contributor_student.department,
                            contributor_student.id,
                            contributor_student.github_id
                        ])
                    except ObjectDoesNotExist:
                        contributor_student_info.extend(['-', '-', '-', specific_contributor_trim])
                    
                    contributors_total_info.append(contributor_student_info)
                
                contributors_without_dash = [info for info in contributors_total_info if '-' not in info[0]]
                contributors_without_dash.sort(key=lambda x: x[0])
                contributors_total_info = contributors_without_dash

            # Contributors count 집계
            if contributors_count < 5:
                total_contributors_count[str(contributors_count)] = total_contributors_count.get(str(contributors_count), 0) + 1
            else:
                total_contributors_count['5+'] = total_contributors_count.get('5+', 0) + 1

            # Repository 언어 비율
            repo_language_percentages = r.language_percentage or {}
            sorted_repo_language_percentages = sorted(repo_language_percentages.items(), key=itemgetter(1), reverse=True)
            top_5_language_percentages = dict(sorted_repo_language_percentages[:5])
            other_languages_percentage = sum(value for key, value in sorted_repo_language_percentages[5:])
            top_5_language_percentages['others'] = round(other_languages_percentage, 1)

            repo_monthly_commit_data = sorted(repo_monthly_commits.get(r.id, {}).items())
            latest_snapshot = latest_snapshots_by_repo.get(r.id)
            file_metrics = file_metrics_by_repo.get(r.id, {})
            review_metrics = review_metrics_by_repo.get(r.id, {})
            dependabot_metrics = dependabot_metrics_by_repo.get(r.id, {})
            repo_github_2026_metrics = {
                'branch_count': latest_snapshot.branch_count if latest_snapshot else None,
                'snapshot_collected_at': latest_snapshot.collected_at if latest_snapshot else None,
                'workflow_yaml_count': latest_snapshot.workflow_yaml_count if latest_snapshot else 0,
                'workflow_yaml_total_size': latest_snapshot.workflow_yaml_total_size if latest_snapshot else 0,
                'workflow_yaml_paths': latest_snapshot.workflow_yaml_paths if latest_snapshot else [],
                'readme_dependency_mentioned': latest_snapshot.readme_dependency_mentioned if latest_snapshot else None,
                'dependency_evidence': latest_snapshot.dependency_evidence if latest_snapshot else {},
                'dependabot_config_present': latest_snapshot.dependabot_config_present if latest_snapshot else None,
                'workflow_yaml_commit_count': file_metrics.get('workflow_yaml_commit_count', 0),
                'test_file_commit_count': file_metrics.get('test_file_commit_count', 0),
                'dependency_manifest_commit_count': file_metrics.get('dependency_manifest_commit_count', 0),
                'repeated_file_modification_count': repeated_file_modifications_by_repo.get(r.id, 0),
                'review_count': review_metrics.get('review_count', 0),
                'review_diff_comment_count': review_metrics.get('review_diff_comment_count', 0),
                'review_comment_count': review_metrics.get('review_comment_count', 0),
                'dependabot_alert_count': dependabot_metrics.get('dependabot_alert_count', 0),
                'open_dependabot_alert_count': dependabot_metrics.get('open_dependabot_alert_count', 0),
            }

            repo_info = {
                'is_owner': r.id in owner_repo_ids,
                'is_contributor': r.id in contributor_repo_ids,
                'id': r.id,
                'name': r.name,
                'is_course': r.is_course,
                'category': r.category,
                'url': r.url,
                'student_id': student.id,
                'owner_github_id': r.owner_github_id,
                'default_branch': r.default_branch,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
                'fork_count': r.fork_count,
                'star_count': r.star_count,
                'total_commit_count': r.commit_count,
                'user_commit_count': repo_user_commit_count,
                'total_issue_count': repo_total_open_issue_count + repo_total_closed_issue_count,
                'owner_issue_count': repo_owner_open_issue_count + repo_owner_closed_issue_count,
                'total_pr_count': repo_total_open_pr_count + repo_total_closed_pr_count,
                'owner_pr_count': repo_owner_open_pr_count + repo_owner_closed_pr_count,
                'language': r.language,
                'language_percentages': top_5_language_percentages,
                'contributors_count': contributors_count,
                'contributors_list': contributors_total_info,
                'license': r.license,
                'has_readme': r.has_readme,
                'description': r.description,
                'project_introduction': r.repo_introduction or "",
                'release_version': r.release_version,
                'summary': r.summary,
                'monthly_commits': repo_monthly_commit_data,
                'github_2026_metrics': repo_github_2026_metrics
            }
            
            data.append(repo_info)

        total_stats.update({
            'total_open_issue_count': total_open_issue_count,
            'total_closed_issue_count': total_closed_issue_count,
            'owner_open_issue_count': owner_open_issue_count,
            'owner_closed_issue_count': owner_closed_issue_count,
            'total_open_pr_count': total_open_pr_count,
            'total_closed_pr_count': total_closed_pr_count,
            'owner_open_pr_count': owner_open_pr_count,
            'owner_closed_pr_count': owner_closed_pr_count,
            'total_star_count': total_star_count,
            'total_fork_count': total_fork_count,
            'workflow_yaml_commit_count': sum(row.get('workflow_yaml_commit_count', 0) for row in file_metrics_by_repo.values()),
            'test_file_commit_count': sum(row.get('test_file_commit_count', 0) for row in file_metrics_by_repo.values()),
            'dependency_manifest_commit_count': sum(row.get('dependency_manifest_commit_count', 0) for row in file_metrics_by_repo.values()),
            'repeated_file_modification_count': sum(repeated_file_modifications_by_repo.values()),
            'review_count': sum(row.get('review_count', 0) for row in review_metrics_by_repo.values()),
            'review_diff_comment_count': sum(row.get('review_diff_comment_count', 0) for row in review_metrics_by_repo.values()),
            'review_comment_count': sum(row.get('review_comment_count', 0) for row in review_metrics_by_repo.values()),
            'dependabot_alert_count': sum(row.get('dependabot_alert_count', 0) for row in dependabot_metrics_by_repo.values()),
            'open_dependabot_alert_count': sum(row.get('open_dependabot_alert_count', 0) for row in dependabot_metrics_by_repo.values()),
        })

        response_data = {
            'student_id': student_id,
            'github_id': github_id,
            'student_name': student_name,
            'student_primary_email': student_primary_email,
            'student_department': student_department,
            'repositories': data,
            'total_language_percentage': top_5_total_language_percentages,
            'total_contributors_count': total_contributors_count,
            'total_stats': total_stats,
            'monthly_commits': {
                'total_count': sorted_commit_counts,
                'added_lines': sorted_added_lines,
                'deleted_lines': sorted_deleted_lines,
                'changed_lines': sorted_changed_lines
            },
            'heatmap': heatmap_data,
            'student_introduction': student.account_introduction or "",
            'student_technology_stack': student.technology_stack or [],
        }

        return JsonResponse(response_data, safe=False)
     
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

# ========================================
# LLM Summary
# ========================================
class RepoSummaryAnalyzer:
    """GitHub API와 OpenAI로 레포지토리를 분석합니다."""

    def __init__(self, openai_key: str = None, github_token: str = None):
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.openai_key:
            raise ValueError("OpenAI API 키가 필요합니다")
        
        if not self.github_token:
            raise ValueError("GitHub Token이 필요합니다")

        self.openai_client = OpenAI(api_key=self.openai_key)
        self.github_headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def analyze_repository(
        self, repo_data: dict, include_frontend_data: bool = False
    ) -> dict:
        """GitHub API와 OpenAI를 활용한 실제 레포지토리 분석"""
        try:
            owner = repo_data.get('owner_github_id')
            repo_name = repo_data.get('name')
            
            repo_structure = self._fetch_repository_structure(owner, repo_name)
            readme_content = self._fetch_readme_content(owner, repo_name)
            key_files_content = self._fetch_key_files(owner, repo_name, repo_structure)
            
            llm_analysis = self._analyze_with_llm(
                repo_data, repo_structure, readme_content, key_files_content
            )
            
            result = {
                "success": True,
                "repository": f"{owner}/{repo_name}",
                "structured_summary": llm_analysis,
                "analyzed_at": datetime.now().isoformat(),
            }

            if include_frontend_data:
                frontend_summary = self._generate_frontend_summary(llm_analysis)
                result.update({
                    "description": llm_analysis.get("user_content", {}).get("description", ""),
                    "frontend_summary": frontend_summary,
                })

            return result

        except Exception as e:
            logging.exception(f"[{owner}/{repo_name}] 전체 분석 과정에서 오류 발생: {e}")
            # 전체 분석 실패 시에도 폴백 데이터 생성
            fallback_summary = self._create_fallback_analysis(repo_data, {}, "")
            return {
                "success": False,
                "repository": f"{owner}/{repo_name}",
                "error": str(e),
                "analyzed_at": datetime.now().isoformat(),
                "structured_summary": fallback_summary
            }

    def _fetch_repository_structure(self, owner: str, repo_name: str) -> dict:
        """GitHub API로 레포지토리 파일 구조 가져오기"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"
            response = requests.get(url, headers=self.github_headers)
            if response.status_code != 200:
                return {"error": f"GitHub API 요청 실패: {response.status_code}"}
            
            tree_data = response.json()
            files, directories = [], set()
            
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':
                    files.append({'path': item['path'], 'size': item.get('size', 0)})
                elif item['type'] == 'tree':
                    directories.add(item['path'])
            
            file_analysis = self._analyze_file_structure(files)
            
            return {
                "total_files": len(files),
                "directories": list(directories),
                "file_analysis": file_analysis,
                "project_structure": self._infer_project_structure(files, directories)
            }
        except Exception as e:
            return {"error": f"구조 분석 실패: {str(e)}"}

    def _fetch_readme_content(self, owner: str, repo_name: str) -> str:
        """README 파일 내용 가져오기"""
        try:
            readme_names = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md']
            for readme_name in readme_names:
                url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{readme_name}"
                response = requests.get(url, headers=self.github_headers)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data.get('encoding') == 'base64' and content_data.get('content'):
                        return base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')[:3000]
            return ""
        except Exception:
            return ""

    def _fetch_key_files(self, owner: str, repo_name: str, repo_structure: dict) -> dict:
        """주요 설정 파일들의 내용 분석"""
        key_files = {'package.json': None, 'requirements.txt': None, '.github/workflows': []}
        try:
            file_analysis = repo_structure.get('file_analysis', {})
            if 'package.json' in file_analysis.get('config_files', []):
                content = self._fetch_file_content(owner, repo_name, 'package.json')
                if content:
                    try:
                        package_data = json.loads(content)
                        key_files['package.json'] = {
                            'dependencies': list(package_data.get('dependencies', {}).keys())[:10],
                            'devDependencies': list(package_data.get('devDependencies', {}).keys())[:10],
                        }
                    except json.JSONDecodeError: pass
            for req_file in ['requirements.txt', 'requirements/base.txt', 'requirements/production.txt']:
                if any(req_file in f for f in file_analysis.get('config_files', [])):
                    content = self._fetch_file_content(owner, repo_name, req_file)
                    if content:
                        key_files['requirements.txt'] = [line.split('==')[0].strip() for line in content.split('\n') if line.strip() and not line.startswith('#')][:15]
                        break
            key_files['.github/workflows'] = self._fetch_github_workflows(owner, repo_name)
            return key_files
        except Exception:
            return key_files

    def _fetch_file_content(self, owner: str, repo_name: str, file_path: str) -> str:
        """특정 파일의 내용 가져오기"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
            response = requests.get(url, headers=self.github_headers)
            if response.status_code == 200:
                content_data = response.json()
                if content_data.get('encoding') == 'base64':
                    return base64.b64decode(content_data['content']).decode('utf-8')
            return ""
        except Exception:
            return ""

    def _fetch_github_workflows(self, owner: str, repo_name: str) -> list:
        """GitHub Actions 워크플로우 정보 가져오기"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/workflows"
            response = requests.get(url, headers=self.github_headers)
            if response.status_code == 200:
                return [{'name': w['name'], 'state': w['state']} for w in response.json().get('workflows', [])]
            return []
        except Exception:
            return []

    def _analyze_file_structure(self, files: list) -> dict:
        """파일 구조 분석"""
        analysis = {'languages': {}, 'config_files': [], 'test_files': [], 'doc_files': []}
        lang_ext = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java', '.html': 'HTML', '.css': 'CSS'}
        for file_info in files:
            path = file_info['path']
            ext = os.path.splitext(path)[1]
            if ext in lang_ext:
                lang = lang_ext[ext]
                analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
            if any(p in path.lower() for p in ['config', 'requirements.txt', 'package.json', 'dockerfile']):
                analysis['config_files'].append(path)
            if 'test' in path.lower():
                analysis['test_files'].append(path)
            if 'doc' in path.lower() or '.md' in path.lower():
                analysis['doc_files'].append(path)
        return analysis

    def _infer_project_structure(self, files: list, directories: list) -> dict:
        """프로젝트 구조 추론"""
        structure = {'project_type': 'unknown', 'framework_indicators': []}
        all_content = ' '.join([f['path'] for f in files] + list(directories)).lower()
        if 'react' in all_content: structure['framework_indicators'].append('React')
        if 'vue' in all_content: structure['framework_indicators'].append('Vue')
        if 'django' in all_content: structure['framework_indicators'].append('Django')
        if 'flask' in all_content: structure['framework_indicators'].append('Flask')
        if structure['framework_indicators']:
            structure['project_type'] = 'backend' if any(f in ['Django', 'Flask'] for f in structure['framework_indicators']) else 'frontend'
        elif '.py' in all_content: structure['project_type'] = 'python'
        elif '.js' in all_content: structure['project_type'] = 'javascript'
        return structure

    def _analyze_with_llm(self, repo_data: dict, repo_structure: dict, readme_content: str, key_files_content: dict) -> dict:
        """OpenAI를 사용한 종합 분석"""
        # owner = repo_data.get('owner_github_id', 'unknown')
        # repo_name = repo_data.get('name', 'unknown')
        # try:
        #     analysis_prompt = self._create_analysis_prompt(repo_data, repo_structure, readme_content, key_files_content)
        #     logging.info(f"[LLM CALL] model=gpt-5-nano repo={owner}/{repo_name}")
        #     response = self.openai_client.responses.create(
        #         model="gpt-5-nano",
        #         input=analysis_prompt,
        #         reasoning={"effort": "low"},
        #         text={"verbosity": "low"},
        #     )
        #     # GPT-5 Responses API는 output_text 필드에 결과를 담아 반환합니다.
        #     output = getattr(response, 'output_text', None)
        #     if not output:
        #         logging.warning(f"[LLM EMPTY OUTPUT] repo={owner}/{repo_name}")
        #         return self._create_fallback_analysis(repo_data, repo_structure, readme_content)
        #     try:
        #         return json.loads(output)
        #     except Exception:
        #         logging.warning(f"[LLM NON-JSON OUTPUT] repo={owner}/{repo_name} output_head={output[:120]}")
        #         return self._create_fallback_analysis(repo_data, repo_structure, readme_content)
        # except Exception as e:
        #     logging.exception(f"[{owner}/{repo_name}] LLM 분석 실패: {e}")
        #     return self._create_fallback_analysis(repo_data, repo_structure, readme_content)
        return 0

    def _create_analysis_prompt(self, repo_data: dict, repo_structure: dict, readme_content: str, key_files_content: dict) -> str:
        """LLM 분석용 프롬프트 생성"""
        prompt = f"""
                다음 레포지토리를 분석하고 결과를 한국어 JSON 형식으로 제공해주세요.

                **레포지토리 정보:**
                - 이름: {repo_data.get('owner_github_id')}/{repo_data.get('name')}
                - 설명: {repo_data.get('description', '설명 없음')}
                - 언어 분포: {repo_structure.get('file_analysis', {}).get('languages', {})}

                **README 내용:**
                {readme_content[:1200] if readme_content else 'README 파일이 없거나 비어있습니다.'}

                **요구사항:**
                분석 결과를 반드시 다음 JSON 형식에 맞춰 한국어로 작성해주세요.

                {{
                    "project_summary": {{
                        "primary_language": "가장 많이 사용된 프로그래밍 언어",
                        "purpose": "이 프로젝트가 해결하려는 문제나 제공하는 기능에 대한 구체적인 설명",
                        "tech_stack": ["주요 기술 3-4개 목록"],
                        "key_functionalities": ["구현된 주요 기능 2-4개 목록"],
                        "scale": "small/medium/large 중 하나"
                    }},
                    "user_content": {{
                        "description": "일반인도 이해할 수 있도록 프로젝트에 대해 한 문단으로 포괄적으로 설명해주세요."
                    }}
                }}
                """
        return prompt

    def _create_fallback_analysis(self, repo_data: dict, repo_structure: dict, readme_content: str = "") -> dict:
        """LLM 분석 실패 시 폴백 분석"""
        languages = repo_data.get('language_bytes', {})
        primary_language = max(languages, key=languages.get) if languages else "Unknown"
        purpose = repo_data.get('description', f"{primary_language} project")
        
        description = f"{purpose}. "
        if readme_content:
            description += readme_content[:200] + "..."

        return {
            "project_summary": {
                "primary_language": primary_language,
                "purpose": purpose,
                "tech_stack": [primary_language],
                "key_functionalities": ["Feature extraction failed"],
                "scale": "medium"
            },
            "user_content": {
                "description": description.strip()
            }
        }

    def _generate_frontend_summary(self, llm_analysis: dict) -> dict:
        """분석 결과를 프론트엔드 전달용으로 가공"""
        summary = llm_analysis.get("project_summary", {})
        user_content = llm_analysis.get("user_content", {})
        
        return {
            "description": user_content.get("description", summary.get("purpose", "No description available.")),
            "key_functionalities": summary.get("key_functionalities", []),
            "tech_stack": summary.get("tech_stack", []),
        }

class GenerateRepoSummaryAPIView(APIView):
    """
    레포지토리 분석을 실행하고 결과를 DB에 저장합니다.
    요청 본문에 필터 조건이 없으면 모든 레포지토리를 대상으로 분석을 실행합니다.
    """
    def post(self, request, *args, **kwargs):
        # analyzer = RepoSummaryAnalyzer()
        queryset = Repository.objects.all()

        # 요청 본문에서 필터 조건 가져오기
        student_ids = request.data.get("student_ids")
        repo_ids = request.data.get("repo_ids")
        filter_type = request.data.get("filter")

        # 1. 학생 ID로 필터링
        if student_ids:
            try:
                # Student 모델에서 github_id 조회
                github_ids = Student.objects.filter(id__in=student_ids).values_list('github_id', flat=True)
                queryset = queryset.filter(owner_github_id__in=list(github_ids))
            except Exception as e:
                return Response({"error": f"학생 ID 필터링 오류: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 레포지토리 ID로 필터링
        if repo_ids:
            queryset = queryset.filter(id__in=repo_ids)

        # 3. 상태(filter_type)로 필터링
        if filter_type == "missing_summary":
            queryset = queryset.filter(summary__isnull=True)
        elif filter_type == "outdated":
            # 예: 30일 이상된 분석 결과 필터링
            thirty_days_ago = make_aware(datetime.now() - timedelta(days=30))
            # 이 부분은 summary 필드가 JSON 객체일 때를 가정하므로, 실제 필드 구조에 맞게 조정 필요
            # queryset = queryset.filter(summary__analyzed_at__lte=thirty_days_ago.isoformat())

        repositories = queryset.all()
        total_requested = len(repositories)
        
        success_count, failure_count = 0, 0
        failed_repositories = []
        
        for repo in repositories:
            repo_data = {
                'id': repo.id, 'name': repo.name, 'owner_github_id': repo.owner_github_id,
                'description': repo.description, 'language_bytes': repo.language_bytes,
            }
            
            analysis_result = analyzer.analyze_repository(repo_data)
            
            # 실제 분석 내용인 structured_summary를 추출
            llm_summary = analysis_result.get("structured_summary")
            
            # llm_summary가 존재하면 성공/실패 여부와 무관하게 저장
            if llm_summary:
                # 성공 시, TextField에 유효한 JSON 문자열로 저장 (DB가 JSONB여도 캐스팅 가능)
                repo.summary = json.dumps(llm_summary, ensure_ascii=False)
                repo.save(update_fields=['summary'])
                print(f"[SUMMARY SAVED] repo={repo.owner_github_id}/{repo.name} id={repo.id} len={len(repo.summary)}")
                success_count += 1
            else:
                # 실패 시, 실패 카운트를 올리고 실패 목록에 추가
                failure_count += 1
                failed_repositories.append({
                    "repository": f"{repo.owner_github_id}/{repo.name}",
                    "error": analysis_result.get("error", "Unknown error")
                })
                print(f"[SUMMARY NOT SAVED] repo={repo.owner_github_id}/{repo.name} id={repo.id} reason=no_summary")
                # (선택) 실패 시 폴백 데이터를 저장하고 싶다면 아래 주석 해제
                # if llm_summary:
                #     repo.summary = json.dumps(llm_summary, ensure_ascii=False)
                #     repo.save(update_fields=['summary'])
                
        return Response({
            "message": "Repository analysis completed.",
            "total_requested": total_requested,
            "processed": success_count,
            "failed": failure_count,
            "failed_repositories": failed_repositories
        }, status=status.HTTP_200_OK)

class GetRepoSummaryAPIView(APIView):
    """
    특정 레포지토리의 분석 결과를 프론트엔드 형식으로 반환합니다.
    """
    def get(self, request, *args, **kwargs):
        repo_id = request.query_params.get('repo_id')
        if not repo_id:
            return Response({"error": "repo_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"error": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)
            
        summary_text = repo.summary
        if not summary_text:
            return Response({"error": "Analysis not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            llm_analysis = json.loads(summary_text)
        except Exception:
            return Response({"error": "Analysis data is invalid."}, status=status.HTTP_404_NOT_FOUND)

        analyzer = RepoSummaryAnalyzer()
        frontend_data = analyzer._generate_frontend_summary(llm_analysis)

        return Response({
            "description": frontend_data.get("description"),
            "bullet_description": frontend_data.get("key_functionalities"),
            "tech_stack": frontend_data.get("tech_stack"),
        }, status=status.HTTP_200_OK)

# ---------------------------------------------
# Save repo introduction per Repository
# ---------------------------------------------
@csrf_exempt
def update_repo_introduction(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)

        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        uuid = body.get('uuid')
        repo_id = body.get('repo_id')
        project_introduction = body.get('project_introduction', '')

        if not uuid:
            return JsonResponse({"status": "Error", "message": "uuid is required"}, status=400)
        if not repo_id:
            return JsonResponse({"status": "Error", "message": "repo_id is required"}, status=400)

        # uuid → login_student → account_student 검증 (소유자 확인용)
        try:
            login_student = LoginStudent.objects.get(member_id=uuid)
            account_student = Student.objects.get(id=login_student.id)
        except LoginStudent.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "login_student not found for given uuid"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "account_student not found for given student id"}, status=404)

        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "repository not found"}, status=404)

        # 선택: 요청자가 해당 repo의 owner인지 확인 (owner_github_id 매칭)
        # owner_mismatch = account_student.github_id and repo.owner_github_id and (account_student.github_id != repo.owner_github_id)
        # if owner_mismatch:
        #     return JsonResponse({"status": "Error", "message": "permission denied: not the repo owner"}, status=403)

        repo.repo_introduction = project_introduction or ''
        repo.save()

        return JsonResponse({
            "status": "OK",
            "message": "project_introduction saved",
            "repo_id": repo.id,
            "project_introduction": repo.repo_introduction,
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
