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
from course.models import Course, Course_project, Course_registration
from operator import itemgetter
import requests
import json

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
            github_id = body_data.get('github_id')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"status": "Error", "message": "Invalid JSON format or character encoding"}, status=400)
        
        if not github_id:
            return JsonResponse({"status": "Error", "message": "github_id is required in the request body"}, status=400)

        # github_id로 Repository, Student 객체 조회
        repo_list = Repository.objects.filter(owner_github_id=github_id)
        student = Student.objects.get(github_id=github_id)
        
        sorted_total_language_percentages = sorted(student.total_language_percentage.items(), key=itemgetter(1), reverse=True)
        top_5_total_language_percentages = dict(sorted_total_language_percentages[:5])
        other_total_languages_percentage = sum(value for key, value in sorted_total_language_percentages[5:])
        top_5_total_language_percentages['others'] = round(other_total_languages_percentage, 1)
        
        if not repo_list:
            return JsonResponse({"status": "Error", "message": f"No repositories found for github_id: {github_id}"}, status=404)

        repo_ids = [r.id for r in repo_list]
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        # 지난 1년간의 커밋 기록을 한 번만 조회
        all_commits = Repo_commit.objects.filter(
            repo_id__in=repo_ids,
            last_update__gte=one_year_ago
        )
        
        monthly_commit_counts = {}
        monthly_added_lines = {}
        monthly_deleted_lines = {}
        monthly_total_changed_lines = {}
        
        # 히트맵 데이터 초기화
        days_of_week = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        heatmap_data = {day: {str(hour): 0 for hour in range(24)} for day in days_of_week.values()}
        
        # 조회된 커밋 데이터셋을 한 번만 순회하며 모든 통계 데이터를 동시에 집계
        for commit in all_commits:
            try:
                commit_datetime = datetime.strptime(commit.last_update, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, TypeError):
                continue
            
            # 월별 데이터 집계
            month_key = commit_datetime.strftime('%Y-%m')
            added = commit.added_lines if commit.added_lines is not None else 0
            deleted = commit.deleted_lines if commit.deleted_lines is not None else 0

            monthly_commit_counts[month_key] = monthly_commit_counts.get(month_key, 0) + 1
            monthly_added_lines[month_key] = monthly_added_lines.get(month_key, 0) + added
            monthly_deleted_lines[month_key] = monthly_deleted_lines.get(month_key, 0) + deleted
            monthly_total_changed_lines[month_key] = monthly_total_changed_lines.get(month_key, 0) + added + deleted
            
            # 히트맵 데이터 집계
            weekday_index = commit_datetime.weekday() # 0 = 월요일
            hour = commit_datetime.hour
            day_name = days_of_week[weekday_index]
            
            heatmap_data[day_name][str(hour)] += 1

        # 데이터 정렬
        sorted_commit_counts = sorted(monthly_commit_counts.items())
        sorted_added_lines = sorted(monthly_added_lines.items())
        sorted_deleted_lines = sorted(monthly_deleted_lines.items())
        sorted_total_changed_lines = sorted(monthly_total_changed_lines.items())

        data =[]
        for r in repo_list:
            
            try:
                course = Course.objects.get(course_repo_name=r.name)
                category = course.name 
            except ObjectDoesNotExist:
                category = "-"
            
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
            
            repo_language_percentages = r.language_percentage or {}
            sorted_repo_language_percentages = sorted(repo_language_percentages.items(), key=itemgetter(1), reverse=True)
            top_5_language_percentages = dict(sorted_repo_language_percentages[:5])
            other_languages_percentage = sum(value for key, value in sorted_repo_language_percentages[5:])
            top_5_language_percentages['others'] = round(other_languages_percentage, 1)

            repo_info = {
            'id': r.id,
            'name': r.name,
            'category' : category,
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
            'contributors': contributors_count,
            'contributors_list': contributors_total_info,
            'license': r.license,
            'has_readme': r.has_readme,
            'description': r.description,
            'release_version': r.release_version
            }
            
            data.append(repo_info)
    
        response_data = {
            'repositories': data,
            'total_language_percentage': top_5_total_language_percentages,
            'monthly_commits': {
                'total_count': sorted_commit_counts,
                'added_lines': sorted_added_lines,
                'deleted_lines': sorted_deleted_lines,
                'total_changed_lines': sorted_total_changed_lines
            },
            'heatmap': heatmap_data,
        }

        return JsonResponse(response_data, safe=False)
     
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)