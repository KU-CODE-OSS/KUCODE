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
from django.utils.timezone import make_aware
from django.db.models import Sum

from repo.models import Repository, Repo_contributor, Repo_issue,Repo_pr, Repo_commit
from account.models import Student
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
        students = Student.objects.all()
        students_list = [{'id': student.id, 'github_id': student.github_id} for student in students]

        # 2. Initialize counters and lists to track synchronization results.
        total_student_count = len(students_list)
        student_count = 0

        success_student_count = 0
        failure_student_count = 0
        failure_student_details = []

        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        # 3. Start the synchronization process for each student.
        for student in students_list:
            student_count += 1
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
            repo_list = [{'id': repo['id'], 'name': repo['name']} for repo in data]

            
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
        # 1. Fetch all Repository objects and initialize the data list.
        repo_list = Repository.objects.all()
        data = []

        # 2. Iterate through each repository to compile its detailed information.
        for r in repo_list:
            
            # 2a. Fetch related data: owner, PR count, and contributors.
            student = Student.objects.get(github_id=r.owner_github_id)
            pr_count = Repo_pr.objects.filter(repo=r).count()
            contributors_list = r.contributors.split(",")
            contributors_count = len(contributors_list)

            # 2b. Process the list of contributors.
            if all(value.strip() == '' for value in contributors_list):
                # Handle cases where the contributors string is empty.
                contributors_count = 0
                contributors_total_info = []
            else:
                # If contributors exist, look up details for each one.
                contributors_total_info = []
                for specific_contributor in contributors_list:
                    contributor_student_info = []
                    specific_contributor_trim = str(specific_contributor).strip()
                    try:
                        # Find the contributor in the Student table.
                        contributor_student = Student.objects.get(github_id=specific_contributor_trim)
                        contributor_student_info.extend([
                            contributor_student.name,
                            contributor_student.department,
                            contributor_student.id,
                            contributor_student.github_id
                        ])
                    except ObjectDoesNotExist:
                        # If the contributor is not found, use placeholders.
                        contributor_student_info.extend(['-', '-', '-', specific_contributor_trim])
                    
                    contributors_total_info.append(contributor_student_info)
                
                # 2c. Sort the processed contributors list.
                # Separate registered users (found in DB) from unregistered ones.
                contributors_without_dash = [info for info in contributors_total_info if '-' not in info[0]]
                contributors_with_dash = [info for info in contributors_total_info if '-' in info[0]]

                # Sort the registered contributors by name (ascending).
                contributors_without_dash.sort(key=lambda x: x[0])

                # NOTE: This line overwrites the list, effectively discarding unregistered contributors
                # (contributors_with_dash) from the final output for this repository.
                contributors_total_info = contributors_without_dash
            
            # 2d. Assemble the final dictionary for the repository.
            repo_info = {
                'id': r.id,
                'name': r.name,
                'url': r.url,
                'student_id': student.id,
                'owner_github_id': r.owner_github_id,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
                'fork_count': r.fork_count,
                'star_count': r.star_count,
                'commit_count': r.commit_count,
                'total_issue_count': int(r.open_issue_count) + int(r.closed_issue_count),
                "pr_count": pr_count,
                'language': r.language,
                'contributors': contributors_count,
                'contributors_list': contributors_total_info,
                'license': r.license,
                'has_readme': r.has_readme,
                'description': r.description,
                'release_version': r.release_version
            }
            
            data.append(repo_info)
    
        # 3. Return the complete list as a JSON response.
        return JsonResponse(data, safe=False)
    
    # Global exception handler for the entire process.
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
        repositories = Repository.objects.all()
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
        repositories = Repository.objects.all()
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
                            'repo_url': issue_data.get('repo_url'),
                            'owner_github_id': issue_data.get('contributed_github_id'),
                            'state': issue_data.get('state'),
                            'title': issue_data.get('title'),
                            'publisher_github_id': issue_data.get('publisher_github_id'),
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
            'repo_url',
            'owner_github_id',
            'state',
            'title',
            'publisher_github_id',
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
        repositories = Repository.objects.all()
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
                            'repo_url': pr_data.get('repo_url'),
                            'owner_github_id': pr_data.get('contributed_github_id'),
                            'title': pr_data.get('title'),
                            'requester_id': pr_data.get('requester_id'),
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
            'repo_url',
            'owner_github_id',
            'title',
            'requester_id',
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
        repositories = Repository.objects.all()
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
                    params={'github_id': github_id, 'repo_name': repo_name, 'since': since}
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
                            'last_update': commit_data.get('last_update')
                        }
                    )

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
            'last_update'
        ))
        
        # 2. Return the list of commits as a JSON response.
        return JsonResponse(commit_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors during the database query.
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------Course_reated REPO READ--------------#
from django.db.models import Count

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
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"status": "Error", "message": "Invalid JSON format or character encoding"}, status=400)
        
        if not uuid:
            return JsonResponse({"status": "Error", "message": "uuid is required in the request body"}, status=400)

        try:
            # uuid로 login.Student에서 학번(id) 조회 후 account.Student에서 github_id 조회
            login_student = LoginStudent.objects.get(member_id=uuid)
            student_id = login_student.id  # 학번
            student = Student.objects.get(id=student_id)
            github_id = student.github_id
            # github_id로 Repository 조회
            owner_repo_list = Repository.objects.filter(owner_github_id=github_id)
            contributor_repo_list = Repository.objects.filter(contributors__icontains=github_id)
            owner_contributor_repo_list = owner_repo_list | contributor_repo_list
            
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
        
        if not owner_repo_list:
            return JsonResponse({"status": "Error", "message": f"No user repositories found for github_id: {github_id}"}, status=404)
        elif not contributor_repo_list:
            return JsonResponse({"status": "Error", "message": f"No contributed repositories found for github_id: {github_id}"}, status=404)

        owner_repo_ids = [r.id for r in owner_repo_list]
        contributor_repo_ids = [r.id for r in contributor_repo_list]
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        # 지난 1년간의 커밋 기록을 한 번만 조회
        all_commits = Repo_commit.objects.filter(repo_id__in=owner_repo_ids + contributor_repo_ids)
        owner_all_commits = Repo_commit.objects.filter(repo_id__in=owner_repo_ids, author_github_id=github_id)
        contributor_all_commits = Repo_commit.objects.filter(repo_id__in=contributor_repo_ids, author_github_id=github_id)
        owner_contributor_all_commits = Repo_commit.objects.filter(repo_id__in=owner_repo_ids + contributor_repo_ids, author_github_id=github_id)
        # 모든 기간 커밋 통계 계산
        all_commit_total_data = all_commits.aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        owner_commit_total_data = owner_all_commits.aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        contributor_commit_total_data = contributor_all_commits.aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        total_stats = {
            'all_total_commits': all_commit_total_data.get('total_commits', 0) or 0,
            'all_added_lines': all_commit_total_data.get('added_lines', 0) or 0,
            'all_deleted_lines': all_commit_total_data.get('deleted_lines', 0) or 0,
            'all_total_changed_lines': (all_commit_total_data.get('added_lines', 0) or 0) + (all_commit_total_data.get('deleted_lines', 0) or 0),
            'owner_total_commits': owner_commit_total_data.get('total_commits', 0) or 0,
            'owner_added_lines': owner_commit_total_data.get('added_lines', 0) or 0,
            'owner_deleted_lines': owner_commit_total_data.get('deleted_lines', 0) or 0,
            'owner_total_changed_lines': (owner_commit_total_data.get('added_lines', 0) or 0) + (owner_commit_total_data.get('deleted_lines', 0) or 0),
            'contributor_total_commits': contributor_commit_total_data.get('total_commits', 0) or 0,
            'contributor_added_lines': contributor_commit_total_data.get('added_lines', 0) or 0,
            'contributor_deleted_lines': contributor_commit_total_data.get('deleted_lines', 0) or 0,
            'contributor_total_changed_lines': (contributor_commit_total_data.get('added_lines', 0) or 0) + (contributor_commit_total_data.get('deleted_lines', 0) or 0),
        }

        # 이슈, PR 등 리포지토리 관련 통계는 기존과 동일하게 repo_list를 순회하며 계산
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

        monthly_commit_counts = {}
        monthly_added_lines = {}
        monthly_deleted_lines = {}
        monthly_changed_lines = {}
        repo_monthly_commits = {repo.id: {} for repo in owner_contributor_repo_list}

        # 히트맵 데이터 초기화
        days_of_week = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        heatmap_data = {day: {str(hour): 0 for hour in range(24)} for day in days_of_week.values()}
        
        # 조회된 커밋 데이터셋을 한 번만 순회하며 모든 통계 데이터를 동시에 집계
        for commit in owner_contributor_all_commits:
            try:
                commit_datetime = datetime.strptime(commit.last_update, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, TypeError):
                continue
            
            # 1년치 데이터만 월별/히트맵 집계에 사용
            if commit_datetime >= one_year_ago:
                # 월별 데이터 집계
                month_key = commit_datetime.strftime('%Y-%m')
                added = commit.added_lines if commit.added_lines is not None else 0
                deleted = commit.deleted_lines if commit.deleted_lines is not None else 0

                monthly_commit_counts[month_key] = monthly_commit_counts.get(month_key, 0) + 1
                monthly_added_lines[month_key] = monthly_added_lines.get(month_key, 0) + added
                monthly_deleted_lines[month_key] = monthly_deleted_lines.get(month_key, 0) + deleted
                monthly_changed_lines[month_key] = monthly_changed_lines.get(month_key, 0) + added + deleted

                # 히트맵 데이터 집계
                weekday_index = commit_datetime.weekday() # 0 = 월요일
                hour = commit_datetime.hour
                day_name = days_of_week[weekday_index]
                
                heatmap_data[day_name][str(hour)] += 1

        # repo_monthly_commits 별도 처리: 각 레포지토리별 마지막 커밋 날짜 기준으로 1년 전까지 계산
        for repo in owner_contributor_repo_list:
            # 해당 레포지토리의 커밋들만 필터링
            repo_commits = [commit for commit in all_commits if commit.repo.id == repo.id and commit.author_github_id == github_id]
            
            if not repo_commits:
                continue
                
            # 해당 레포지토리의 가장 마지막 커밋 날짜 찾기
            latest_commit_date = None
            for commit in repo_commits:
                try:
                    commit_datetime = datetime.strptime(commit.last_update, '%Y-%m-%dT%H:%M:%SZ')
                    if latest_commit_date is None or commit_datetime > latest_commit_date:
                        latest_commit_date = commit_datetime
                except (ValueError, TypeError):
                    continue
            
            # 마지막 커밋 날짜가 없으면 현재 날짜 사용
            if latest_commit_date is None:
                latest_commit_date = datetime.now()
            
            # 해당 레포지토리의 마지막 커밋 날짜 기준으로 1년 전 계산
            repo_one_year_ago = latest_commit_date - timedelta(days=365)
            
            # 해당 레포지토리의 마지막 커밋 날짜 기준 1년 내 커밋들을 월별로 집계
            for commit in repo_commits:
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

        total_contributors_count = {'1':0, '2':0, '3':0, '4':0, '5+':0}

        data =[]
        for r in owner_contributor_repo_list:
            
            repo_user_commit_count = Repo_commit.objects.filter(repo=r, author_github_id=github_id).count()
            repo_total_open_pr_count = Repo_pr.objects.filter(repo=r, state='open').count()
            repo_total_closed_pr_count = Repo_pr.objects.filter(repo=r, state='closed').count()
            repo_owner_open_pr_count = Repo_pr.objects.filter(repo=r, requester_id=github_id, state='open').count()
            repo_owner_closed_pr_count = Repo_pr.objects.filter(repo=r, requester_id=github_id, state='closed').count()
            repo_total_open_issue_count = Repo_issue.objects.filter(repo=r, state='open').count()
            repo_total_closed_issue_count = Repo_issue.objects.filter(repo=r, state='closed').count()
            repo_owner_open_issue_count = Repo_issue.objects.filter(repo=r, publisher_github_id=github_id, state='open').count()
            repo_owner_closed_issue_count = Repo_issue.objects.filter(repo=r, publisher_github_id=github_id, state='closed').count()
            contributors_list = r.contributors.split(",")
            contributors_count = len(contributors_list)

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

            if all(value.strip() == '' for value in contributors_list): # contributors 없을 시
                contributors_count = 0  
                contributors_total_info = []

            else :
                contributors_total_info = []
                
                for specific_contributor in contributors_list :
                    contributor_student_info = []
                    specific_contributor_trim = str(specific_contributor).strip()
                    try:
                        contributor_student = Student.objects.get(github_id = specific_contributor_trim)
                        contributor_student_info.append(contributor_student.name) 
                        contributor_student_info.append(contributor_student.department)
                        contributor_student_info.append(contributor_student.id)   
                        contributor_student_info.append(contributor_student.github_id)                
                    except ObjectDoesNotExist:
                        contributor_student_info.append('-')   
                        contributor_student_info.append('-') 
                        contributor_student_info.append('-')
                        contributor_student_info.append(specific_contributor_trim)  

                    contributors_total_info.append(contributor_student_info)
                
                # Separate contributors with '-' from those without
                contributors_without_dash = [info for info in contributors_total_info if '-' not in info[0]]  # Sort by name (index 0)
                contributors_with_dash = [info for info in contributors_total_info if '-' in info[0]]

                # Sort the registered contributors by name (ascending).
                contributors_without_dash.sort(key=lambda x: x[0])

                # Concatenate sorted lists, placing contributors with '-' at the end
                contributors_total_info = contributors_without_dash 

            total_contributors_count.update({str(contributors_count): total_contributors_count.get(str(contributors_count), 0) + 1}) if contributors_count < 5 else total_contributors_count.update({'5+': total_contributors_count.get('5+', 0) + 1})

            # Repository별 언어 비율 처리
            repo_language_percentages = r.language_percentage or {}
            sorted_repo_language_percentages = sorted(repo_language_percentages.items(), key=itemgetter(1), reverse=True)
            top_5_language_percentages = dict(sorted_repo_language_percentages[:5])
            other_languages_percentage = sum(value for key, value in sorted_repo_language_percentages[5:])
            top_5_language_percentages['others'] = round(other_languages_percentage, 1)

            repo_monthly_commit_data = sorted(repo_monthly_commits.get(r.id, {}).items())

            # Send raw summary as stored (full JSON string/dict)

            repo_info = {
            'is_owner': r in owner_repo_list,
            'is_contributor': r in contributor_repo_list,
            'id': r.id,
            'name': r.name,
            'is_course': r.is_course,
            'category' : r.category,
            'url': r.url,
            'student_id': student.id if student else None,
            'owner_github_id': r.owner_github_id,
            'created_at': r.created_at,
            'updated_at': r.updated_at,
            'fork_count': r.fork_count,
            'star_count': r.star_count,
            'total_commit_count': r.commit_count,
            'user_commit_count': repo_user_commit_count,
            'total_issue_count': int(total_open_issue_count) + int(total_closed_issue_count),
            'owner_issue_count': int(owner_open_issue_count) + int(owner_closed_issue_count),
            'total_pr_count': int(repo_total_open_pr_count) + int(repo_total_closed_pr_count),
            'owner_pr_count': int(repo_owner_open_pr_count) + int(repo_owner_closed_pr_count),
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
            'monthly_commits': repo_monthly_commit_data
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
        })

        response_data = {
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
            'student_introduction': student.introduction or "",
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
        owner = repo_data.get('owner_github_id', 'unknown')
        repo_name = repo_data.get('name', 'unknown')
        try:
            analysis_prompt = self._create_analysis_prompt(repo_data, repo_structure, readme_content, key_files_content)
            logging.info(f"[LLM CALL] model=gpt-5-nano repo={owner}/{repo_name}")
            response = self.openai_client.responses.create(
                model="gpt-5-nano",
                input=analysis_prompt,
                reasoning={"effort": "low"},
                text={"verbosity": "low"},
            )
            # GPT-5 Responses API는 output_text 필드에 결과를 담아 반환합니다.
            output = getattr(response, 'output_text', None)
            if not output:
                logging.warning(f"[LLM EMPTY OUTPUT] repo={owner}/{repo_name}")
                return self._create_fallback_analysis(repo_data, repo_structure, readme_content)
            try:
                return json.loads(output)
            except Exception:
                logging.warning(f"[LLM NON-JSON OUTPUT] repo={owner}/{repo_name} output_head={output[:120]}")
                return self._create_fallback_analysis(repo_data, repo_structure, readme_content)
        except Exception as e:
            logging.exception(f"[{owner}/{repo_name}] LLM 분석 실패: {e}")
            return self._create_fallback_analysis(repo_data, repo_structure, readme_content)

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
        analyzer = RepoSummaryAnalyzer()
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
def save_repo_introduction(request):
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
        owner_mismatch = account_student.github_id and repo.owner_github_id and (account_student.github_id != repo.owner_github_id)
        if owner_mismatch:
            return JsonResponse({"status": "Error", "message": "permission denied: not the repo owner"}, status=403)

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