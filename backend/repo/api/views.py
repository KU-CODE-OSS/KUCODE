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
import requests

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

# ========================================
# Backend Function
# ========================================
# ------------Repo--------------#
def sync_repo_db(request):
    try:
        students = Student.objects.all()
        students_list = [{'id': student.id, 'github_id': student.github_id} for student in students]

        total_student_count = len(students_list)
        student_count = 0

        success_student_count = 0
        failure_student_count = 0
        failure_student_details = []

        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        for student in students_list:
            student_count += 1
            print(f'\n{"="*10} [{student_count}/{total_student_count}] Processing GitHub user: {student["github_id"]} {"="*10}')
            id = student['id']
            github_id = student['github_id']
            
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos", params={'github_id': github_id})
            if response.status_code != 200:
                message = f"Failed to fetch repositories for GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue
            
            data = response.json()
            if not isinstance(data, list):
                message = f"Invalid response format for repositories of GitHub user {github_id}"
                print(f"[ERROR] {message}")
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue

            total_repo_count = len(data)
            repo_list = [{'id': repo['id'], 'name': repo['name']} for repo in data]

            
            # Compare with the list of repositories stored in the current DB
            repos_in_db = Repository.objects.filter(owner_github_id=github_id).values_list('id', flat=True)
            repos_in_db_sorted = sorted(repos_in_db)  # Sort the DB repository IDs in ascending order
            print("-"*5 + f"\nDB: {repos_in_db_sorted}")

            repo_ids_in_list = sorted([str(repo['id']) for repo in repo_list])  # Sort the list of IDs in ascending order
            print("-"*5 + f"\nFASTAPI: {repo_ids_in_list}")

            missing_in_fastapi = set(repos_in_db) - set(repo_ids_in_list)

            if missing_in_fastapi:  # Check if the set is not empty
                print("-"*5 + f"\n Need to Remove: {missing_in_fastapi}\n"+"-"*5)
            else:
                print("-"*5 + f"\n No repositories need to be removed.\n"+"-"*5)

            for repo_id in repos_in_db:
                if repo_id not in repo_ids_in_list:
                    remove_repository(github_id, Repository(id=repo_id))
                    print(f" Repository {repo_id} removed for GitHub ID: {github_id}\n"+"-"*5)

            repo_count = 0
            for repo in repo_list:
                repo_name = repo['name']
                repo_id = repo['id']
                repo_count += 1
                print(f"  [{repo_count}/{total_repo_count}] Processing repository: {repo_name} (ID: {repo_id})")
                
                repo_response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos", params={'github_id': github_id, 'repo_id': repo_id})
                if repo_response.status_code != 200:
                    message = f"Failed to fetch data for repo {repo_id} of GitHub user {github_id}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_id": repo_id, "message": message})
                    continue

                repo_data = repo_response.json()
                try:
                    print(f"  {github_id}/{repo_name}: {repo_data}")
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
                    print(f"  {action} repository: {repo_name} (ID: {repo_id})")
                    success_repo_count += 1

                except Exception as e:
                    message = f"Error processing repository {repo_name} (ID: {repo_id}) for GitHub user {github_id}: {str(e)}"
                    print(f"[ERROR] {message}")
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})

            # account_student -> star_count 
            total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count'] or 0
            student_record = Student.objects.get(id=id)
            student_record.starred_count = total_star_count
            student_record.save()

            print(f"  Total star count ({total_star_count}) for GitHub user {github_id} saved.")
            success_student_count += 1
            print(f'{"-"*5} Processed GitHub user: {github_id} {"-"*5}')

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
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------DELETE--------------#
def remove_repository(github_id, repository):
    try:
        # Related Course_project deletion
        try:
            course_project = Course_project.objects.get(repo=repository.id)
            course_project.delete()
            print(f"  Deleted associated course project for repo ID: {repository.id}")
        except Course_project.DoesNotExist:
            print(f"  Already been deleted or does not exist: {repository.id}")

        # Related repositories contributor, issue, PR, and commit deletion
        # Contributor deletion
        try:
            contributors = Repo_contributor.objects.filter(repo=repository.id)
            if contributors.exists():
                contributors.delete()
                print(f"  Deleted all contributors for repo ID: {repository.id}")
            else:
                print(f"  Already been deleted or does not exist: {repository.id}")
        except Exception as e:
            print(f"  Error deleting contributors for repo ID: {repository.id}: {str(e)}")

        # Issue deletion
        try:
            issues = Repo_issue.objects.filter(repo=repository.id)
            if issues.exists():
                issues.delete()
                print(f"  Deleted all issues for repo ID: {repository.id}")
            else:
                print(f"  Already been deleted or does not exist: {repository.id}")
        except Exception as e:
            print(f"  Error deleting issues for repo ID: {repository.id}: {str(e)}")

        # PR deletion
        try:
            prs = Repo_pr.objects.filter(repo=repository.id)
            if prs.exists():
                prs.delete()
                print(f"  Deleted all pull requests for repo ID: {repository.id}")
            else:
                print(f"  Already been deleted or does not exist: {repository.id}")
        except Exception as e:
            print(f"  Error deleting pull requests for repo ID: {repository.id}: {str(e)}")

        # Commit deletion
        try:
            commits = Repo_commit.objects.filter(repo=repository.id)
            if commits.exists():
                commits.delete()
                print(f"  Deleted all commits for repo ID: {repository.id}")
            else:
                print(f"  Already been deleted or does not exist: {repository.id}")
        except Exception as e:
            print(f"  Error deleting commits for repo ID: {repository.id}: {str(e)}")

        # Repository deletion
        try:
            repository_obj = Repository.objects.get(owner_github_id=github_id, id=repository.id)
            repo_name = repository_obj.name  # Access the name attribute safely
            repository_obj.delete()
            print(f"  The repo {repo_name} has been deleted successfully for GitHub user {github_id}")
            return {"status": "OK", "message": "The repo has been deleted successfully"}
        except Repository.DoesNotExist:
            print(f"  Repo with ID '{repository.id}' does not exist for GitHub user {github_id}")
            return {"status": "Error", "message": f"Repo with ID '{repository.id}' does not exist"}

    except Exception as e:
        print(f"  Error deleting repo with ID '{repository.id}' for GitHub user {github_id}: {str(e)}")
        return {"status": "Error", "message": str(e)}

# ---------------------------------------------
    
# ------------REPO READ--------------#
def repo_read_db(request):
    try:
        repo_list = Repository.objects.all()
        data =[]
        for r in repo_list:
            
            student = Student.objects.get(github_id = r.owner_github_id)
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
            "pr_count":pr_count,
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

# ------------CONTRIBUTOR--------------#
def sync_repo_contributor_db(request):
    try:
        # Fetch all repository names and associated GitHub IDs
        repositories = Repository.objects.all()
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        repo_ids = [repo['id'] for repo in repo_list]

        total_repo_count = len(repo_list)
        repo_count = 0
        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        # Process each repository
        for repo in repo_list:
            repo_count += 1
            print(f'\n{"="*10} [{repo_count}/{total_repo_count}] Processing repo: {repo["name"]} (GitHub ID: {repo["github_id"]}) {"="*10}')
            
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            processed_repo_ids.add(repo_id)

            # Fetch contributor data for the repository
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/contributor", params={'github_id': github_id, 'repo_name': repo_name})
            contributor_data = response.json()

            if not isinstance(contributor_data, list):
                message = f"[ERROR] Invalid response format or empty repository: {repo_name} (GitHub ID: {github_id})"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            total_contributor_count = len(contributor_data)
            contributor_count = 0

            # Process each contributor
            for contributor in contributor_data:
                contributor_count += 1
                print(f'  [{contributor_count}/{total_contributor_count}] Processing contributor: {contributor.get("login")}')
                
                try:
                    repo_contributor, created = Repo_contributor.objects.update_or_create(
                        owner_github_id=github_id,
                        repo_id=repo_id,
                        contributor_id=contributor.get('login'),
                        defaults={
                            'contributor_id': contributor.get('login'),
                            'contribution_count': contributor.get('contributions'),
                            'repo_url': contributor.get('repo_url')
                        }
                    )
                    
                    action = "Created" if created else "Updated"
                    print(f"  [SUCCESS] {action} repo contributor for repo {repo_name} (GitHub ID: {github_id})")

                except Exception as e:
                    message = f"[ERROR] Error processing contributor for {repo_name} (GitHub ID: {github_id}): {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1
            print(f'\n{"-"*5} Processed contributors for repository: {repo_name} (GitHub ID: {github_id}) {"-"*5}')


        return JsonResponse({
            "status": "OK",
            "message": "Contributor update completed successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------contributor READ--------------#
def repo_contributor_read_db(request):
    try:
        contributors = Repo_contributor.objects.all()
        contributor_list = [{'id': contributor.id, 'repo_id': contributor.repo_id, 'repo_url': contributor.repo_url, 'owner_github_id': contributor.owner_github_id, 'contributor_id': contributor.contributor_id, 'contributor_count': contributor.contributor_count} for contributor in contributors]
        return JsonResponse(contributor_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ISSUE--------------#
def sync_repo_issue_db(request):
    try:
        # Fetch all repositories
        repositories = Repository.objects.all()
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id, 'created': repo.created_at} for repo in repositories]
        repo_ids = [repo['id'] for repo in repo_list]

        total_repo_count = len(repo_list)
        repo_count = 0  
        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        # Track processed repository IDs
        processed_repo_ids = set()
        
        for repo in repo_list:
            repo_count += 1
            print(f'\n{"="*10} [{repo_count}/{total_repo_count}] Processing issues for repo: {repo["name"]} (GitHub ID: {repo["github_id"]}) {"="*10}')
            
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Get the latest update time for open or closed issues
            open_issue = Repo_issue.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_issue = Repo_issue.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_issue:
                since = open_issue.last_update
            elif closed_issue:
                since = closed_issue.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            # Fetch issues from the API
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/issues", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            if not isinstance(data, list):
                message = f"[ERROR] Invalid response format or empty repository: {repo_name} (GitHub ID: {github_id})"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            total_issue_count = len(data)
            issue_count = 0

            # Process each issue
            for issue_data in data:
                issue_count += 1
                print(f'  [{issue_count}/{total_issue_count}] Processing issue: {issue_data.get("title")}')
                
                try:
                    repo_issue, created = Repo_issue.objects.update_or_create(
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
                    
                    action = "Created" if created else "Updated"
                    print(f"  [SUCCESS] {action} issue for repo {repo_name} (GitHub ID: {github_id}): {issue_data.get('id')}")

                except Exception as e:
                    message = f"[ERROR] Error processing issue for {repo_name} (GitHub ID: {github_id}): {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1
            print(f'\n{"-"*5} Processed issues for repository: {repo_name} (GitHub ID: {github_id}) {"-"*5}')


        return JsonResponse({
            "status": "OK",
            "message": "Repo issues updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ISSUE READ--------------#
def repo_issue_read_db(request):
    try:
        issues = Repo_issue.objects.all()
        issue_list = [{'id': issue.id, 'repo_id': issue.repo_id, 'repo_url': issue.repo_url, 'owner_github_id': issue.owner_github_id, 'state': issue.state, 'title': issue.title, 'publisher_github_id': issue.publisher_github_id, 'last_update': issue.last_update} for issue in issues]
        return JsonResponse(issue_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------PR--------------#
def sync_repo_pr_db(request):
    try:
        # Fetch all repositories
        repositories = Repository.objects.all()
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id, 'created': repo.created_at} for repo in repositories]
        repo_ids = [repo['id'] for repo in repo_list]

        total_repo_count = len(repo_list)
        repo_count = 0
        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []
        print("1")
        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        for repo in repo_list:
            repo_count += 1
            print(f'\n{"="*10} [{repo_count}/{total_repo_count}] Processing PRs for repo: {repo["name"]} (GitHub ID: {repo["github_id"]}) {"="*10}')
            
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Get the most recent 'open' or 'closed' PR
            open_pr = Repo_pr.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_pr = Repo_pr.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_pr:
                since = open_pr.last_update
            elif closed_pr:
                since = closed_pr.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            # Fetch PR data from the API
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/pulls", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            if not isinstance(data, list):
                message = f"[ERROR] Invalid response format or empty repository: {repo_name} (GitHub ID: {github_id})"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            total_pr_count = len(data)
            pr_count = 0

            # Process each PR
            for pr_data in data:
                pr_count += 1
                print(f'  [{pr_count}/{total_pr_count}] Processing PR: {pr_data.get("title")}')
                
                try:
                    pr, created = Repo_pr.objects.update_or_create(
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
                    
                    action = "Created" if created else "Updated"
                    print(f"  [SUCCESS] {action} PR for repo {repo_name} (GitHub ID: {github_id}): {pr_data.get('id')}")

                except Exception as e:
                    message = f"[ERROR] Error processing PR for {repo_name} (GitHub ID: {github_id}): {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1
            print(f'\n{"-"*5} Processed PRs for repository: {repo_name} (GitHub ID: {github_id}) {"-"*5}')

        return JsonResponse({
            "status": "OK",
            "message": "Repo PRs updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------PR READ--------------#
def repo_pr_read_db(request):
    try:
        prs = Repo_pr.objects.all()
        pr_list = [{'id': pr.id, 'repo_id': pr.repo_id, 'repo_url': pr.repo_url, 'owner_github_id': pr.owner_github_id, 'title': pr.title, 'requester_id': pr.requester_id, 'published_date': pr.published_date, 'state': pr.state, 'last_update': pr.last_update} for pr in prs]
        return JsonResponse(pr_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------COMMIT--------------#
def sync_repo_commit_db(request):
    try:
        # Fetch all repositories
        repositories = Repository.objects.all()
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id, 'created': repo.created_at} for repo in repositories]
        repo_ids = [repo['id'] for repo in repo_list]

        total_repo_count = len(repo_list)
        repo_count = 0

        success_repo_count = 0
        failure_repo_count = 0
        failure_repo_details = []

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        for repo in repo_list:
            repo_count += 1
            print(f'\n{"="*10} [{repo_count}/{total_repo_count}] Processing commits for repo: {repo["name"]} (GitHub ID: {repo["github_id"]}) {"="*10}')
            
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Get the latest commit
            latest_commit = Repo_commit.objects.filter(repo_id=repo_id).order_by('-last_update').first()
            since = latest_commit.last_update if latest_commit else "2008-02-08T00:00:00Z"

            # Fetch commits from the API
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/commit", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            if not isinstance(data, list):
                message = f"[ERROR] Invalid response format or empty repository: {repo_name} (GitHub ID: {github_id})"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            total_commit_count = len(data)
            commit_count = 0

            # Process each commit
            for commit_data in data:
                commit_count += 1
                print(f'  [{commit_count}/{total_commit_count}] Processing commit: {commit_data.get("sha")}')
                
                try:
                    commit, created = Repo_commit.objects.update_or_create(
                        sha=commit_data.get('sha'),
                        defaults={
                            'repo_id': repo_id,
                            'repo_url': commit_data.get('repo_url'),
                            'owner_github_id': commit_data.get('contributed_github_id'),
                            'author_github_id': commit_data.get(''),
                            'added_lines': commit_data.get('added_lines'),
                            'deleted_lines': commit_data.get('deleted_lines'),
                            'last_update': commit_data.get('last_update')
                        }
                    )

                    action = "Created" if created else "Updated"
                    print(f"  [SUCCESS] {action} commit for repo {repo_name} (GitHub ID: {github_id}): {commit_data.get('sha')}")

                except Exception as e:
                    message = f"[ERROR] Error processing commit for {repo_name} (GitHub ID: {github_id}): {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1
            print(f'\n{"-"*5} Processed commits for repository: {repo_name} (GitHub ID: {github_id}) {"-"*5}')

        return JsonResponse({
            "status": "OK",
            "message": "Repo commits updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ------------COMMIT READ--------------#
def repo_commit_read_db(request):
    try: 
        commits = Repo_commit.objects.all()
        commit_list = [{'sha': commit.sha, 'repo_id': commit.repo_id, 'repo_url': commit.repo_url, 'owner_github_id': commit.owner_github_id, 'committer_github_id': commit.committer_github_id, 'added_lines': commit.added_lines, 'deleted_lines': commit.deleted_lines, 'last_update': commit.last_update} for commit in commits]
        return JsonResponse(commit_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ========================================
# Backend Function
# ========================================
# ------------Course_reated REPO READ--------------#
def repo_course_read_db(request):
    try:
        course_projects = Course_project.objects.all().values_list('repo')
        repo_list = Repository.objects.filter(id__in=course_projects)
        data =[]
        for r in repo_list:
            print(r)
            pr = Repo_pr.objects.filter(repo=r).count()
            contributors_list = r.contributors.split(",")
            contributors_count = len(contributors_list)
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
                "pr_count":pr,
                'language': r.language,
                'contributors': contributors_count,
                'license': r.license,
                'has_readme': r.has_readme,
                'description': r.description,
                'release_version': r.release_version
            }
            data.append(repo_info)
        return JsonResponse(data, safe=False)
    except Exception as e:
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