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
            'author_github_id', # Corrected field name for consistency
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
            repo_list = Repository.objects.filter(owner_github_id=github_id)
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
        
        if not repo_list:
            return JsonResponse({"status": "Error", "message": f"No repositories found for github_id: {github_id}"}, status=404)

        repo_ids = [r.id for r in repo_list]
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        # 지난 1년간의 커밋 기록을 한 번만 조회
        all_commits = Repo_commit.objects.filter(repo_id__in=repo_ids)
        
        # 모든 기간 커밋 통계 계산
        commit_total_data = all_commits.aggregate(
            added_lines=Sum('added_lines'),
            deleted_lines=Sum('deleted_lines'),
            total_commits=Count('id')
        )
        total_stats = {
            'total_commits': commit_total_data.get('total_commits', 0) or 0,
            'added_lines': commit_total_data.get('added_lines', 0) or 0,
            'deleted_lines': commit_total_data.get('deleted_lines', 0) or 0,
            'total_changed_lines': (commit_total_data.get('added_lines', 0) or 0) + (commit_total_data.get('deleted_lines', 0) or 0),
        }


        monthly_commit_counts = {}
        monthly_added_lines = {}
        monthly_deleted_lines = {}
        monthly_changed_lines = {}
        repo_monthly_commits = {repo.id: {} for repo in repo_list}

        # 히트맵 데이터 초기화
        days_of_week = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        heatmap_data = {day: {str(hour): 0 for hour in range(24)} for day in days_of_week.values()}
        
        # 조회된 커밋 데이터셋을 한 번만 순회하며 모든 통계 데이터를 동시에 집계
        for commit in all_commits:
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
            
                repo_id = commit.repo.id
                repo_monthly_commits[repo_id][month_key] = repo_monthly_commits[repo_id].get(month_key, 0) + 1

                # 히트맵 데이터 집계
                weekday_index = commit_datetime.weekday() # 0 = 월요일
                hour = commit_datetime.hour
                day_name = days_of_week[weekday_index]
                
                heatmap_data[day_name][str(hour)] += 1

        # 데이터 정렬
        sorted_commit_counts = sorted(monthly_commit_counts.items())
        sorted_added_lines = sorted(monthly_added_lines.items())
        sorted_deleted_lines = sorted(monthly_deleted_lines.items())
        sorted_changed_lines = sorted(monthly_changed_lines.items())

        # 이슈, PR 등 리포지토리 관련 통계는 기존과 동일하게 repo_list를 순회하며 계산
        total_open_issue_count = sum(repo.open_issue_count for repo in repo_list)
        total_closed_issue_count = sum(repo.closed_issue_count for repo in repo_list)
        total_open_pr_count = sum(repo.open_pr_count for repo in repo_list)
        total_closed_pr_count = sum(repo.closed_pr_count for repo in repo_list)
        total_star_count = sum(repo.star_count for repo in repo_list)
        total_fork_count = sum(repo.fork_count for repo in repo_list)

        total_stats.update({
            'total_open_issues': total_open_issue_count,
            'total_closed_issues': total_closed_issue_count,
            'total_open_prs': total_open_pr_count,
            'total_closed_prs': total_closed_pr_count,
            'total_stars': total_star_count,
            'total_forks': total_fork_count,
        })

        total_contributors_count = {'1':0, '2':0, '3':0, '4':0, '5+':0}

        data =[]
        for r in repo_list:
            
            pr_count = Repo_pr.objects.filter(repo=r).count()
            contributors_list = r.contributors.split(",")
            contributors_count = len(contributors_list)

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

                # Sort contributors_without_dash by name (ascending order)
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

            repo_info = {
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
            'commit_count': r.commit_count,
            'total_issue_count': int(r.open_issue_count) + int(r.closed_issue_count),
            "pr_count":pr_count,
            'language': r.language,
            'language_percentages': top_5_language_percentages,
            'contributors_count': contributors_count,
            'contributors_list': contributors_total_info,
            'license': r.license,
            'has_readme': r.has_readme,
            'description': r.description,
            'release_version': r.release_version,
            'summary': r.summary,
            'monthly_commits': repo_monthly_commit_data
            }
            
            data.append(repo_info)
    
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
        }

        return JsonResponse(response_data, safe=False)
     
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
# ========================================
# Repository Summary Analyzer
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
        """GitHub API와 OpenAI를 활용한 실제 레포지토리 분석

        Args:
            repo_data: DB의 레포지토리 기본 정보
            include_frontend_data: 프론트엔드용 데이터 포함 여부
        """
        try:
            owner = repo_data.get('owner_github_id')
            repo_name = repo_data.get('name')
            
            # 1. GitHub API로 실제 레포지토리 구조 분석
            repo_structure = self._fetch_repository_structure(owner, repo_name)
            
            # 2. README 내용 가져오기
            readme_content = self._fetch_readme_content(owner, repo_name)
            
            # 3. 주요 파일들 내용 분석
            key_files_content = self._fetch_key_files(owner, repo_name, repo_structure)
            
            # 4. OpenAI로 종합 분석
            llm_analysis = self._analyze_with_llm(
                repo_data, repo_structure, readme_content, key_files_content
            )
            
            # 5. 구조화된 응답 생성
            result = {
                "success": True,
                "repository": f"{owner}/{repo_name}",
                "structured_summary": llm_analysis,
                "analyzed_at": datetime.now().isoformat(),
            }

            # 프론트엔드 데이터가 필요한 경우에만 추가 생성
            if include_frontend_data:
                # description은 문단 형태 요약으로 구성 (간결하게)
                description = self._create_paragraph_description(llm_analysis)
                frontend_summary = self._generate_frontend_summary(llm_analysis, repo_data)

                result.update({
                    "description": description,
                    "frontend_summary": frontend_summary,
                })

            return result

        except Exception as e:
            return {
                "success": False,
                "repository": f"{repo_data.get('owner_github_id', 'unknown')}/{repo_data.get('name', 'unknown')}",
                "error": str(e),
                "analyzed_at": datetime.now().isoformat(),
            }

    def _fetch_repository_structure(self, owner: str, repo_name: str) -> dict:
        """GitHub API로 레포지토리 파일 구조 가져오기"""
        try:
            # Get repository tree
            url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"
            print(f"GitHub API 호출: {url}")
            response = requests.get(url, headers=self.github_headers)
            
            print(f"GitHub API 응답: {response.status_code}")
            if response.status_code != 200:
                print(f"GitHub API 오류: {response.text[:200]}")
                return {"error": f"GitHub API 요청 실패: {response.status_code}"}
            
            tree_data = response.json()
            print(f"트리 항목 수: {len(tree_data.get('tree', []))}")
            
            # 파일 구조 분석
            files = []
            directories = set()
            
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':  # 파일
                    files.append({
                        'path': item['path'],
                        'size': item.get('size', 0)
                    })
                elif item['type'] == 'tree':  # 디렉토리
                    directories.add(item['path'])
            
            print(f"파일 수: {len(files)}, 디렉토리 수: {len(directories)}")
            
            # 파일 분류
            file_analysis = self._analyze_file_structure(files)
            
            result = {
                "total_files": len(files),
                "directories": list(directories),
                "file_analysis": file_analysis,
                "project_structure": self._infer_project_structure(files, directories)
            }
            
            print(f"구조 분석 완료: {result['total_files']}개 파일")
            return result
            
        except Exception as e:
            print(f"구조 분석 실패: {str(e)}")
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
                    # base64 인코딩된 README 처리
                    if content_data.get('encoding') == 'base64' and content_data.get('content'):
                        readme_content = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                        return readme_content[:3000] if len(readme_content) > 3000 else readme_content
                    # 혹시 평문 content가 오는 경우
                    if isinstance(content_data.get('content'), str) and not content_data.get('encoding'):
                        readme_content = content_data['content']
                        return readme_content[:3000] if len(readme_content) > 3000 else readme_content
            return ""
        except Exception:
            return ""

    def _fetch_key_files(self, owner: str, repo_name: str, repo_structure: dict) -> dict:
        """주요 설정 파일들의 내용 분석"""
        key_files = {
            'package.json': None,
            'requirements.txt': None,
            'pom.xml': None,
            'Cargo.toml': None,
            'go.mod': None,
            'composer.json': None,
            'Pipfile': None,
            'setup.py': None,
            'pyproject.toml': None,
            'Dockerfile': None,
            'docker-compose.yml': None,
            '.github/workflows': []
        }

        try:
            file_analysis = repo_structure.get('file_analysis', {})

            # package.json 분석
            if 'package.json' in file_analysis.get('config_files', []):
                content = self._fetch_file_content(owner, repo_name, 'package.json')
                if content:
                    try:
                        package_data = json.loads(content)
                        key_files['package.json'] = {
                            'dependencies': list(package_data.get('dependencies', {}).keys())[:10],
                            'devDependencies': list(package_data.get('devDependencies', {}).keys())[:10],
                            'scripts': list(package_data.get('scripts', {}).keys())
                        }
                    except json.JSONDecodeError:
                        pass

            # requirements.txt 분석
            for req_file in ['requirements.txt', 'requirements/base.txt', 'requirements/production.txt']:
                if any(req_file in f for f in file_analysis.get('config_files', [])):
                    content = self._fetch_file_content(owner, repo_name, req_file)
                    if content:
                        packages = [
                            line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                            for line in content.split('\n')
                            if line.strip() and not line.startswith('#')
                        ]
                        key_files['requirements.txt'] = packages[:15]
                        break

            # GitHub Actions 워크플로우
            workflows = self._fetch_github_workflows(owner, repo_name)
            key_files['.github/workflows'] = workflows

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
                    import base64
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
                workflows_data = response.json()
                return [
                    {
                        'name': workflow['name'],
                        'path': workflow['path'],
                        'state': workflow['state']
                    }
                    for workflow in workflows_data.get('workflows', [])
                ]
            return []
        except Exception:
            return []

    def _analyze_file_structure(self, files: list) -> dict:
        """파일 구조 분석"""
        analysis = {
            'languages': {},
            'config_files': [],
            'test_files': [],
            'doc_files': [],
            'build_files': [],
            'frontend_files': [],
            'backend_files': [],
            'mobile_files': [],
            'data_files': []
        }
        
        language_extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React',
            '.tsx': 'React', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
            '.kt': 'Kotlin', '.dart': 'Dart', '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
            '.vue': 'Vue', '.svelte': 'Svelte', '.sql': 'SQL', '.r': 'R', '.m': 'MATLAB',
            '.sh': 'Shell', '.ps1': 'PowerShell', '.yaml': 'YAML', '.yml': 'YAML'
        }
        
        for file_info in files:
            path = file_info['path']
            filename = path.split('/')[-1].lower()
            
            # 언어별 파일 수 계산
            for ext, lang in language_extensions.items():
                if path.lower().endswith(ext):
                    analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
                    break
            
            # 설정 파일
            config_patterns = [
                'package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 
                'cargo.toml', 'go.mod', 'composer.json', 'pipfile', 'setup.py',
                'pyproject.toml', 'dockerfile', 'docker-compose', '.env', 'config'
            ]
            if any(pattern in filename for pattern in config_patterns):
                analysis['config_files'].append(path)
            
            # 테스트 파일
            if any(pattern in path.lower() for pattern in ['test', 'spec', '__tests__', '.test.', '.spec.']):
                analysis['test_files'].append(path)
            
            # 문서 파일
            if any(pattern in filename for pattern in ['readme', 'docs', 'documentation', '.md', '.rst']):
                analysis['doc_files'].append(path)
            
            # 빌드/배포 파일
            if any(pattern in filename for pattern in ['makefile', 'webpack', 'gulpfile', 'gruntfile', 'rollup']):
                analysis['build_files'].append(path)
        
        return analysis

    def _infer_project_structure(self, files: list, directories: list) -> dict:
        """프로젝트 구조 추론"""
        structure = {
            'project_type': 'unknown',
            'framework_indicators': [],
            'architecture_patterns': [],
            'has_tests': False,
            'has_ci_cd': False,
            'has_docker': False,
            'has_docs': False
        }
        
        file_paths = [f['path'] for f in files]
        all_content = ' '.join(file_paths + list(directories)).lower()
        
        # 프로젝트 타입 추론
        if any(f in all_content for f in ['package.json', 'node_modules', '.js', '.ts']):
            if any(f in all_content for f in ['react', 'angular', 'vue', 'svelte']):
                structure['project_type'] = 'frontend'
            elif any(f in all_content for f in ['express', 'koa', 'nest', 'api']):
                structure['project_type'] = 'backend'
            else:
                structure['project_type'] = 'javascript'
        
        elif any(f in all_content for f in ['requirements.txt', '.py', 'setup.py']):
            if any(f in all_content for f in ['django', 'flask', 'fastapi', 'api']):
                structure['project_type'] = 'backend'
            elif any(f in all_content for f in ['jupyter', '.ipynb', 'data', 'analysis']):
                structure['project_type'] = 'data_science'
            else:
                structure['project_type'] = 'python'
        
        elif any(f in all_content for f in ['pom.xml', '.java', 'build.gradle']):
            structure['project_type'] = 'java'
        
        # 프레임워크 지표
        framework_indicators = {
            'React': ['package.json', 'jsx', 'tsx', 'react'],
            'Angular': ['angular.json', 'typescript', '@angular'],
            'Vue': ['vue.config.js', '.vue', 'vuejs'],
            'Django': ['manage.py', 'settings.py', 'django'],
            'Flask': ['app.py', 'flask', '__init__.py'],
            'Spring': ['pom.xml', 'spring', 'java'],
            'Express': ['express', 'node', 'javascript'],
            'Flutter': ['pubspec.yaml', '.dart', 'flutter'],
            'iOS': ['.swift', '.m', 'xcode'],
            'Android': ['.kt', '.java', 'android', 'gradle']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in all_content for indicator in indicators):
                structure['framework_indicators'].append(framework)
        
        # 아키텍처 패턴
        if any(d in directories for d in ['src', 'lib', 'app']):
            structure['architecture_patterns'].append('modular')
        if any(d in directories for d in ['components', 'services', 'models']):
            structure['architecture_patterns'].append('mvc')
        if any(d in directories for d in ['api', 'controllers', 'routes']):
            structure['architecture_patterns'].append('api')
        
        # 기능 체크
        structure['has_tests'] = any('test' in path for path in file_paths)
        structure['has_ci_cd'] = any('.github/workflows' in path or '.gitlab-ci' in path for path in file_paths)
        structure['has_docker'] = any('dockerfile' in path.lower() for path in file_paths)
        structure['has_docs'] = any('readme' in path.lower() or 'docs' in path.lower() for path in file_paths)
        
        return structure

    def _analyze_with_llm(self, repo_data: dict, repo_structure: dict, readme_content: str, key_files_content: dict) -> dict:
        """OpenAI를 사용한 종합 분석"""
        try:
            # 분석 데이터 준비
            analysis_prompt = self._create_analysis_prompt(repo_data, repo_structure, readme_content, key_files_content)
            
            print(f"LLM 분석 시작: {repo_data.get('owner_github_id')}/{repo_data.get('name')}")
            print(f"프롬프트 길이: {len(analysis_prompt)} 문자")
            print(f"README 길이: {len(readme_content)} 문자")
            print(f"파일 구조: {repo_structure.get('total_files', 0)}개 파일")
            
            # GPT-5 새로운 API 호출
            response = self.openai_client.responses.create(
                model="gpt-5-nano",
                input=f"""당신은 GitHub 레포지토리 분석 전문가입니다. 
                        제공된 정보를 바탕으로 프로젝트를 분석하고 한국어로 정확하고 간결한 요약을 제공해주세요.
                        응답은 반드시 유효한 JSON 형식이어야 합니다.

                        {analysis_prompt}""",
                reasoning={"effort": "low"},  # 빠른 응답을 위해
                text={"verbosity": "low"},     # 간결한 응답을 위해
                response_format={"type": "json_object"},
                max_output_tokens=1200,
            )
            
            # 응답 파싱
            llm_response = response.output_text
            print(f"LLM 응답 길이: {len(llm_response)} 문자")
            print(f"LLM 응답 미리보기: {llm_response[:200]}...")
            
            try:
                # JSON 파싱 시도
                analysis_result = json.loads(llm_response)
                print("LLM JSON 파싱 성공")
                return analysis_result
            except json.JSONDecodeError as je:
                # JSON 파싱 실패 시 기본 구조 반환
                print(f"LLM JSON 파싱 실패: {str(je)}")
                print(f"원본 응답: {llm_response}")
                return self._create_fallback_analysis(repo_data, repo_structure)
                
        except Exception as e:
            print(f"LLM 분석 실패: {str(e)}")
            return self._create_fallback_analysis(repo_data, repo_structure)

    def _create_analysis_prompt(self, repo_data: dict, repo_structure: dict, readme_content: str, key_files_content: dict) -> str:
        """LLM 분석용 프롬프트 생성"""
        
        prompt = f"""
다음 GitHub 레포지토리를 분석해주세요:

**기본 정보:**
- 레포지토리: {repo_data.get('owner_github_id')}/{repo_data.get('name')}
- 설명: {repo_data.get('description', '없음')}
- 주요 언어: {repo_data.get('language_bytes', {})}
- 스타/포크: {repo_data.get('star_count', 0)}/{repo_data.get('fork_count', 0)}
- 커밋 수: {repo_data.get('commit_count', 0)}

**파일 구조 분석:**
- 총 파일 수: {repo_structure.get('total_files', 0)}
- 프로젝트 타입: {repo_structure.get('project_structure', {}).get('project_type', 'unknown')}
- 프레임워크: {repo_structure.get('project_structure', {}).get('framework_indicators', [])}
- 언어별 파일: {repo_structure.get('file_analysis', {}).get('languages', {})}

**주요 디렉토리:**
{', '.join(repo_structure.get('directories', [])[:10])}

**README 내용 (일부):**
{readme_content[:500] if readme_content else '없음'}

**주요 설정 파일:**
- package.json: {'있음' if key_files_content.get('package.json') else '없음'}
- requirements.txt: {'있음' if key_files_content.get('requirements.txt') else '없음'}
- GitHub Actions: {len(key_files_content.get('.github/workflows', []))}개

다음 JSON 형식으로 분석 결과를 제공해주세요:

{{
    "project_summary": {{
        "primary_language": "주요 언어",
        "purpose": "프로젝트의 목적과 용도",
        "tech_stack": ["기술1", "기술2", "기술3"],
        "features": ["특징1", "특징2", "특징3"],
        "scale": "소규모/중규모/대규모",
        "activity": "활발함/보통/비활성",
        "key_highlights": ["주요 하이라이트 1", "주요 하이라이트 2"]
    }},
    "technical_details": {{
        "architecture": "아키텍처 패턴",
        "frameworks": ["프레임워크1", "프레임워크2"],
        "development_tools": ["도구1", "도구2"],
        "deployment": "배포 방식",
        "testing": "테스트 현황"
    }},
    "quality_indicators": {{
        "documentation_quality": "좋음/보통/부족",
        "code_organization": "잘 정리됨/보통/개선 필요",
        "best_practices": "잘 지켜짐/부분적/부족",
        "maintainability": "높음/보통/낮음"
    }}
}}
"""
        return prompt

    def _create_fallback_analysis(self, repo_data: dict, repo_structure: dict) -> dict:
        """LLM 분석 실패 시 폴백 분석"""
        
        languages = repo_data.get('language_bytes', {})
        primary_language = max(languages.keys(), key=lambda k: languages[k]) if languages else "Unknown"
        
        project_structure = repo_structure.get('project_structure', {})
        framework_indicators = project_structure.get('framework_indicators', [])
        
        # 기본 분석
        purpose = self._infer_basic_purpose(primary_language, framework_indicators, repo_data)
        tech_stack = [primary_language] + framework_indicators[:3]
        
        return {
            "project_summary": {
                "primary_language": primary_language,
                "purpose": purpose,
                "tech_stack": tech_stack,
                "features": ["코드 저장소", "버전 관리"],
                "scale": "중규모" if repo_structure.get('total_files', 0) > 50 else "소규모",
                "activity": "보통",
                "key_highlights": [f"{primary_language} 기반 프로젝트"]
            },
            "technical_details": {
                "architecture": "표준 구조",
                "frameworks": framework_indicators,
                "development_tools": [],
                "deployment": "미확인",
                "testing": "테스트 파일 있음" if project_structure.get('has_tests') else "테스트 없음"
            },
            "quality_indicators": {
                "documentation_quality": "보통" if project_structure.get('has_docs') else "부족",
                "code_organization": "보통",
                "best_practices": "부분적",
                "maintainability": "보통"
            }
        }

    def _infer_basic_purpose(self, primary_language: str, frameworks: list, repo_data: dict) -> str:
        """기본 목적 추론"""
        description = (repo_data.get('description') or '').lower()
        
        if 'api' in description or 'server' in description:
            return f"{primary_language} API 서버"
        elif 'web' in description or 'website' in description:
            return f"{primary_language} 웹 애플리케이션"
        elif 'mobile' in description or 'app' in description:
            return f"{primary_language} 모바일 애플리케이션"
        elif frameworks:
            return f"{frameworks[0]} 기반 프로젝트"
        else:
            return f"{primary_language} 프로젝트"

    def _generate_bullet_description(self, llm_analysis: dict) -> str:
        """LLM 분석 결과로부터 개조식 불릿포인트 설명 생성"""
        try:
            project_summary = llm_analysis.get("project_summary", {})
            technical_details = llm_analysis.get("technical_details", {})
            quality_indicators = llm_analysis.get("quality_indicators", {})

            description_parts = []

            # 기본 정보
            primary_language = project_summary.get("primary_language", "Unknown")
            if primary_language != "Unknown":
                description_parts.append(f"• 주요 언어: {primary_language}")

            # 프로젝트 목적
            purpose = project_summary.get("purpose", "")
            if purpose:
                description_parts.append(f"• 프로젝트 유형: {purpose}")

            # 기술 스택
            tech_stack = project_summary.get("tech_stack", [])
            if tech_stack:
                tech_str = ", ".join(tech_stack[:4])
                description_parts.append(f"• 기술 스택: {tech_str}")

            # 주요 특징
            features = project_summary.get("features", [])
            if features:
                features_str = ", ".join(features[:3])
                description_parts.append(f"• 주요 특징: {features_str}")

            # 핵심 하이라이트
            highlights = project_summary.get("key_highlights", [])
            if highlights:
                highlights_str = ", ".join(highlights[:2])
                description_parts.append(f"• 핵심 특징: {highlights_str}")

            # 아키텍처 정보
            architecture = technical_details.get("architecture", "")
            if architecture and architecture != "표준 구조":
                description_parts.append(f"• 아키텍처: {architecture}")

            # 배포 방식
            deployment = technical_details.get("deployment", "")
            if deployment and deployment != "미확인":
                description_parts.append(f"• 배포: {deployment}")

            # 테스트 현황
            testing = technical_details.get("testing", "")
            if testing:
                description_parts.append(f"• 테스트: {testing}")

            # 품질 지표
            quality_items = []
            doc_quality = quality_indicators.get("documentation_quality", "")
            if doc_quality == "좋음":
                quality_items.append("문서화 우수")
            elif doc_quality == "보통":
                quality_items.append("기본 문서화")

            code_org = quality_indicators.get("code_organization", "")
            if code_org == "잘 정리됨":
                quality_items.append("코드 구조 양호")

            maintainability = quality_indicators.get("maintainability", "")
            if maintainability == "높음":
                quality_items.append("유지보수성 높음")

            if quality_items:
                description_parts.append(f"• 코드 품질: {', '.join(quality_items)}")

            # 프로젝트 규모 및 활성도
            scale = project_summary.get("scale", "중규모")
            activity = project_summary.get("activity", "보통")
            description_parts.append(f"• 규모 및 활성도: {scale}, {activity}")

            return "\n".join(description_parts)

        except Exception as e:
            return f"• 요약 생성 중 오류 발생: {str(e)}"

    def _create_paragraph_description(self, llm_analysis: dict) -> str:
        """LLM 분석 결과를 한 문단 요약으로 생성"""
        try:
            ps = llm_analysis.get("project_summary", {})
            td = llm_analysis.get("technical_details", {})

            lang = ps.get("primary_language") or "Unknown"
            purpose = ps.get("purpose") or "프로젝트"
            techs = ", ".join((ps.get("tech_stack") or [])[:4])
            features = ", ".join((ps.get("features") or [])[:2])
            arch = td.get("architecture")
            testing = td.get("testing")
            scale = ps.get("scale") or "중규모"
            activity = ps.get("activity") or "보통"

            parts = [f"{lang} 기반 {purpose}입니다."]
            if techs:
                parts.append(f"주요 기술로 {techs}를 사용합니다.")
            if features:
                parts.append(f"주요 기능은 {features} 등이 있습니다.")
            if arch and arch != "표준 구조":
                parts.append(f"아키텍처는 {arch}를 따릅니다.")
            if testing and testing != "미확인":
                parts.append(f"테스트 현황은 '{testing}'입니다.")
            parts.append(f"프로젝트 규모는 {scale}이며 활성도는 {activity}입니다.")

            return " ".join(parts)
        except Exception:
            return "요약 생성에 실패했습니다."

    def _generate_frontend_summary(self, llm_analysis: dict, repo_data: dict = None) -> dict:
        """LLM 분석 결과로부터 프론트엔드용 프로젝트 요약 정보 생성"""
        try:
            project_summary = llm_analysis.get("project_summary", {})
            technical_details = llm_analysis.get("technical_details", {})
            quality_indicators = llm_analysis.get("quality_indicators", {})

            # 핵심 요약 정보
            primary_language = project_summary.get("primary_language", "Unknown")
            purpose = project_summary.get("purpose", "프로젝트")
            scale = project_summary.get("scale", "중규모")
            activity = project_summary.get("activity", "보통")

            core_info = {
                "title": f"{primary_language} {purpose}",
                "primary_language": primary_language,
                "project_type": purpose,
                "scale_and_activity": f"{scale}, {activity}",
            }

            # 기술 스택 (최대 4개)
            tech_stack = project_summary.get("tech_stack", [])[:4]

            # 주요 특징 (특징 + 하이라이트 결합)
            features = project_summary.get("features", [])[:2]
            highlights = project_summary.get("key_highlights", [])[:1]
            key_features = features + highlights

            # 개발 메트릭 - 원본 repo_data에서 가져오기
            if repo_data:
                metrics = {
                    "commits": repo_data.get("commit_count", 0),
                    "stars": repo_data.get("star_count", 0),
                    "forks": repo_data.get("fork_count", 0),
                }
            else:
                # repo_data가 없는 경우 (기존 저장된 summary 조회시)
                metrics = {
                    "commits": 0,
                    "stars": 0,
                    "forks": 0,
                }

            # 품질 지표
            quality_items = []
            
            doc_quality = quality_indicators.get("documentation_quality", "")
            if doc_quality in ["좋음", "보통"]:
                quality_items.append("문서화")

            code_org = quality_indicators.get("code_organization", "")
            if code_org == "잘 정리됨":
                quality_items.append("코드 구조")

            best_practices = quality_indicators.get("best_practices", "")
            if best_practices in ["잘 지켜짐", "부분적"]:
                quality_items.append("베스트 프랙티스")

            maintainability = quality_indicators.get("maintainability", "")
            if maintainability in ["높음", "보통"]:
                quality_items.append("유지보수성")

            return {
                "core_info": core_info,
                "tech_stack": tech_stack,
                "key_features": key_features,
                "metrics": metrics,
                "quality_indicators": quality_items,
                "bullet_description": self._generate_bullet_description(llm_analysis),
            }

        except Exception as e:
            # 에러 발생 시 기본 응답
            return {
                "core_info": {
                    "title": "분석 실패",
                    "primary_language": "Unknown",
                    "project_type": "알 수 없음",
                    "scale_and_activity": "미확인",
                },
                "tech_stack": [],
                "key_features": ["분석 실패"],
                "metrics": {"commits": 0, "stars": 0, "forks": 0},
                "quality_indicators": [],
                "bullet_description": "• 분석 실패",
            }

# ========================================
# API Views
# ========================================


class GenerateRepoSummaryAPIView(APIView):
    """단일 레포지토리 요약 생성 API"""

    def post(self, request):
        try:
            repo_id = request.data.get("repo_id")
            if not repo_id:
                return Response(
                    {"error": "repo_id가 필요합니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 레포지토리 조회
            try:
                repository = Repository.objects.get(id=repo_id)
            except Repository.DoesNotExist:
                return Response(
                    {"error": f"레포지토리 {repo_id}를 찾을 수 없습니다"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 분석기 초기화
            try:
                analyzer = RepoSummaryAnalyzer()
            except ValueError as e:
                return Response(
                    {"error": f"분석기 초기화 실패: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 레포지토리 데이터 변환
            repo_data = {
                "owner_github_id": repository.owner_github_id,
                "name": repository.name,
                "description": repository.description,
                "language_bytes": repository.language_bytes or {},
                "star_count": repository.star_count or 0,
                "fork_count": repository.fork_count or 0,
                "commit_count": repository.commit_count or 0,
                "open_issue_count": repository.open_issue_count or 0,
                "has_readme": repository.has_readme or False,
                "license": repository.license,
                "created_at": repository.created_at,
                "updated_at": repository.updated_at,
            }

            # 분석 수행 (프론트엔드 데이터 포함)
            result = analyzer.analyze_repository(repo_data, include_frontend_data=True)

            if not result.get("success"):
                return Response(
                    {"error": f"분석 실패: {result.get('error')}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # summary 필드 업데이트
            repository.summary = json.dumps(
                result["structured_summary"], ensure_ascii=False
            )
            repository.save()

            return Response(
                {
                    "success": True,
                    "repository": result["repository"],
                    "description": result["description"],
                    "project_summary": result["frontend_summary"]["core_info"],
                    "tech_stack": result["frontend_summary"]["tech_stack"],
                    "key_features": result["frontend_summary"]["key_features"],
                    "metrics": result["frontend_summary"]["metrics"],
                    "quality_indicators": result["frontend_summary"][
                        "quality_indicators"
                    ],
                    "bullet_description": result["frontend_summary"][
                        "bullet_description"
                    ],
                    "analyzed_at": result["analyzed_at"],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"예기치 못한 오류: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerateRepoSummaryBatchAPIView(APIView):
    """배치 레포지토리 요약 생성 API"""

    def post(self, request):
        try:
            # 요청 파라미터 파싱
            filter_type = request.data.get("filter", "missing_summary")
            batch_size = min(
                request.data.get("batch_size", 50), 100
            )  # 최대 100개로 제한
            student_ids = request.data.get("student_ids", [])

            # 분석기 초기화
            try:
                analyzer = RepoSummaryAnalyzer()
            except ValueError as e:
                return Response(
                    {"error": f"분석기 초기화 실패: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 필터 조건에 따른 레포지토리 쿼리
            queryset = Repository.objects.all()

            if filter_type == "missing_summary":
                queryset = queryset.filter(summary__isnull=True)
            elif filter_type == "outdated":
                # summary가 있지만 updated_at이 더 최근인 경우
                queryset = queryset.exclude(summary__isnull=True)
                # 실제로는 더 복잡한 비교 로직 필요

            if student_ids:
                queryset = queryset.filter(
                    owner_github_id__in=[
                        Student.objects.get(id=sid).github_id for sid in student_ids
                    ]
                )

            # 배치 크기로 제한
            repositories = queryset[:batch_size]

            if not repositories:
                return Response(
                    {
                        "message": "분석할 레포지토리가 없습니다",
                        "processed": 0,
                        "failed": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # 배치 분석 수행
            print(f"\n배치 분석 시작: {len(repositories)}개 레포지토리")
            print("=" * 60)

            processed_count = 0
            failed_count = 0
            failed_repos = []

            for i, repository in enumerate(repositories):
                try:
                    print(
                        f"[{i+1}/{len(repositories)}] {repository.owner_github_id}/{repository.name} 분석 중..."
                    )

                    # 레포지토리 데이터 변환
                    repo_data = {
                        "owner_github_id": repository.owner_github_id,
                        "name": repository.name,
                        "description": repository.description,
                        "language_bytes": repository.language_bytes or {},
                        "star_count": repository.star_count or 0,
                        "fork_count": repository.fork_count or 0,
                        "commit_count": repository.commit_count or 0,
                        "open_issue_count": repository.open_issue_count or 0,
                        "has_readme": repository.has_readme or False,
                        "license": repository.license,
                        "created_at": repository.created_at,
                        "updated_at": repository.updated_at,
                    }

                    # 분석 수행 (배치용 - 프론트엔드 데이터 불포함)
                    result = analyzer.analyze_repository(
                        repo_data, include_frontend_data=False
                    )

                    if result.get("success"):
                        # summary 필드 업데이트
                        repository.summary = json.dumps(
                            result["structured_summary"], ensure_ascii=False
                        )
                        repository.save()
                        processed_count += 1
                        print("분석 완료")
                    else:
                        failed_count += 1
                        failed_repos.append(
                            {
                                "repository": f"{repository.owner_github_id}/{repository.name}",
                                "error": result.get("error"),
                            }
                        )
                        print(f"분석 실패: {result.get('error')}")

                except Exception as e:
                    failed_count += 1
                    failed_repos.append(
                        {
                            "repository": f"{repository.owner_github_id}/{repository.name}",
                            "error": str(e),
                        }
                    )
                    print(f"예외 발생: {str(e)}")

            print(f"\n배치 분석 완료!")
            print(f"성공: {processed_count}개")
            print(f"실패: {failed_count}개")

            # 실패한 레포지토리 출력 (처음 5개)
            if failed_repos:
                print("\n실패한 레포지토리:")
                for repo in failed_repos[:5]:
                    print(f"  - {repo['repository']}: {repo['error']}")
                if len(failed_repos) > 5:
                    print(f"  ... 및 {len(failed_repos) - 5}개 더")

            return Response(
                {
                    "success": True,
                    "message": "배치 분석 완료",
                    "processed": processed_count,
                    "failed": failed_count,
                    "total_requested": len(repositories),
                    "failed_repositories": failed_repos[:10],  # 최대 10개만 반환
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"배치 분석 중 오류: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetRepoSummaryAPIView(APIView):
    """DB에서 저장된 레포지토리 요약 조회 API (프론트엔드용)"""

    def post(self, request):
        try:
            repo_id = request.data.get("repo_id")
            if not repo_id:
                return Response(
                    {"error": "repo_id가 필요합니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 레포지토리 조회
            try:
                repository = Repository.objects.get(id=repo_id)
            except Repository.DoesNotExist:
                return Response(
                    {"error": f"레포지토리 {repo_id}를 찾을 수 없습니다"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 저장된 요약이 있는지 확인
            if not repository.summary:
                return Response(
                    {
                        "error": "저장된 요약이 없습니다. 먼저 분석을 진행해주세요.",
                        "has_summary": False,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                # 저장된 structured_summary를 파싱
                structured_summary = json.loads(repository.summary)

                # 분석기 초기화 (프론트엔드 변환용)
                analyzer = RepoSummaryAnalyzer()

                # 원본 레포지토리 데이터 준비 (메트릭 정보용)
                repo_data = {
                    "owner_github_id": repository.owner_github_id,
                    "name": repository.name,
                    "description": repository.description,
                    "language_bytes": repository.language_bytes or {},
                    "star_count": repository.star_count or 0,
                    "fork_count": repository.fork_count or 0,
                    "commit_count": repository.commit_count or 0,
                    "open_issue_count": repository.open_issue_count or 0,
                    "has_readme": repository.has_readme or False,
                    "license": repository.license,
                    "created_at": repository.created_at,
                    "updated_at": repository.updated_at,
                }

                # 프론트엔드용 요약 생성
                description = analyzer._create_paragraph_description(structured_summary)
                frontend_summary = analyzer._generate_frontend_summary(
                    structured_summary, repo_data
                )

                return Response(
                    {
                        "success": True,
                        "repository": f"{repository.owner_github_id}/{repository.name}",
                        "has_summary": True,
                        "description": description,
                        "project_summary": frontend_summary["core_info"],
                        "tech_stack": frontend_summary["tech_stack"],
                        "key_features": frontend_summary["key_features"],
                        "metrics": frontend_summary["metrics"],
                        "quality_indicators": frontend_summary["quality_indicators"],
                        "bullet_description": frontend_summary["bullet_description"],
                        "last_analyzed": (
                            repository.updated_at.isoformat()
                            if repository.updated_at and hasattr(repository.updated_at, 'isoformat')
                            else str(repository.updated_at) if repository.updated_at
                            else None
                        ),
                    },
                    status=status.HTTP_200_OK,
                )

            except json.JSONDecodeError:
                return Response(
                    {"error": "저장된 요약 데이터가 손상되었습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response(
                {"error": f"예기치 못한 오류: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )