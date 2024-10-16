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

# --- repository CRUD ---r
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
            print(f'({student_count}/{total_student_count}) Processing repositories for GitHub user {student["github_id"]}')
            id = student['id']
            github_id = student['github_id']
            
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos", params={'github_id': github_id})
            if response.status_code != 200:
                message = f"Failed to fetch repositories for GitHub user {github_id}"
                print(message)
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue
            
            total_repo_count = len(response.json())
            repo_count = 0

            data = response.json()
            if not isinstance(data, list):
                message = f"Invalid response format for repositories of GitHub user {github_id}"
                print(message)
                failure_student_count += 1
                failure_student_details.append({"id": id, "github_id": github_id, "message": message})
                continue

            repo_list = [{'id': repo['id'], 'name': repo['name']} for repo in data]
            
            # Check for any repositories that need to be removed
            repos_in_db = Repository.objects.filter(owner_github_id=github_id).values_list('id', flat=True)
            for repo_id in repos_in_db:
                if repo_id not in [str(repo['id']) for repo in repo_list]:
                    remove_repository(github_id, Repository(id=repo_id))

            for repo in repo_list:
                repo_name = repo['name']
                repo_id = repo['id']
                repo_count += 1
                print(f'({repo_count}/{total_repo_count}) Processing repository {repo_id} of GitHub user {github_id}')
                repo_response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos", params={'github_id': github_id, 'repo_id': repo_id})
                if repo_response.status_code != 200:
                    message = f"Failed to fetch data for repo {repo_id} of GitHub user {github_id}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_id": repo_id, "message": message})
                    continue

                repo_data = repo_response.json()

                if isinstance(repo_data, dict):
                    try:
                        repository_record = Repository.objects.get(owner_github_id=github_id, id=repo_id)
                        repository_record.name = repo_name
                        repository_record.url = repo_data.get('url')
                        repository_record.created_at = repo_data.get('created_at')
                        repository_record.updated_at = repo_data.get('updated_at')
                        repository_record.fork_count = repo_data.get('forks_count')
                        repository_record.star_count = repo_data.get('stars_count')
                        repository_record.commit_count = repo_data.get('commit_count')
                        repository_record.open_issue_count = repo_data.get('open_issue_count')
                        repository_record.closed_issue_count = repo_data.get('closed_issue_count')
                        repository_record.open_pr_count = repo_data.get('open_pr_count')
                        repository_record.closed_pr_count = repo_data.get('closed_pr_count')
                        repository_record.language = ', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None'
                        repository_record.contributors = ', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None'
                        repository_record.license = repo_data.get('license')
                        repository_record.has_readme = repo_data.get('has_readme')
                        repository_record.description = repo_data.get('description')
                        repository_record.release_version = repo_data.get('release_version')
                        repository_record.crawled_date = repo_data.get('crawled_date')
                        repository_record.save()
                        print(f"Updated repository {repo_name} for GitHub user {github_id}")

                    except ObjectDoesNotExist:
                        Repository.objects.create(
                            id = repo_data.get('id'),
                            name=repo_name,
                            url=repo_data.get('url'),
                            owner_github_id=github_id,
                            created_at=repo_data.get('created_at'),
                            updated_at=repo_data.get('updated_at'),
                            fork_count=repo_data.get('forks_count'),
                            star_count=repo_data.get('stars_count'),
                            commit_count=repo_data.get('commit_count'),
                            open_issue_count=repo_data.get('open_issue_count'),
                            closed_issue_count=repo_data.get('closed_issue_count'),
                            open_pr_count=repo_data.get('open_pr_count'),
                            closed_pr_count=repo_data.get('closed_pr_count'),
                            language=', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None',
                            contributors=', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None',
                            license=repo_data.get('license'),
                            has_readme=repo_data.get('has_readme'),
                            description=repo_data.get('description'),
                            release_version=repo_data.get('release_version'),
                            crawled_date=repo_data.get('crawled_date'),
                        )
                        print(f"Created repository {repo_name} for GitHub user {github_id}")
                        success_repo_count += 1

                    except Exception as e:
                        message = f"Error processing repository {repo_name} for GitHub user {github_id}: {str(e)}"
                        print(message)
                        failure_repo_count += 1
                        failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                        continue
                else:
                    message = f"Invalid response format for repository {repo_name} of GitHub user {github_id}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

                print(f'({repo_count}/{total_repo_count}) Successfully processed repository {repo_name} of GitHub user {github_id}')

            # Calculate total star count for the student
            total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count']
            if total_star_count is None:
                total_star_count = 0
            
            # Update the student's starred_count
            student_record = Student.objects.get(id=id)
            student_record.starred_count = total_star_count
            student_record.save()
            print(f'total star_count ({total_star_count}) for {id} saved.')

            success_student_count += 1


            print(f'({student_count}/{total_student_count}) Successfully processed repositories for GitHub user {github_id}')
            print(f"-"*50)

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

def remove_repository(github_id, repository):
    try:
        repository = Repository.objects.get(owner_github_id=github_id, name=repository.name)
        repository.delete()
        print(f"The repo {repository.name} has been deleted successfully for GitHub user {github_id}")
        return JsonResponse({"status": "OK", "message": "The repo has been deleted successfully"})
    
    except ObjectDoesNotExist:
        print(f"Repo '{repository.name}' does not exist for GitHub user {github_id}")
        return JsonResponse({"status": "Error", "message": f"Repo '{repository.name}' does not exist"}, status=404)    
    except Exception as e:
        print(f"Error deleting repo '{repository.name}' for GitHub user {github_id}: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

# --- Repository Read ---
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
                contributors_total_info = contributors_without_dash + contributors_with_dash
            
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
    

# ---repo_Contributor API-------------------------------
def sync_repo_contributor_db(request):
    try:
        # Fetch all repository names for the given GitHub ID
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

        # Iterate through each repository and update/create Repo_contributor records
        for repo in repo_list:
            repo_count += 1
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']}'s contributors of GitHub user {repo['github_id']}")
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            processed_repo_ids.add(repo_id)

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/contributor", params={'github_id': github_id, 'repo_name': repo_name})
            contributor_data = response.json()

            total_contributor_count = len(contributor_data)
            contributor_count = 0

            # Check if the data is a list
            if not isinstance(contributor_data, list):
                message = f"Invalid response format for repository {repo_name} of GitHub user {github_id} or Empty Repository"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            for contributor in contributor_data:
                contributor_count += 1
                print(f'({contributor_count}/{total_contributor_count}) Processing contributor {contributor.get("login")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    repo_contributor = Repo_contributor.objects.get(owner_github_id=github_id, repo_id=repo_id, contributor_id=contributor.get('login'))
                    repo_contributor.contributor_id = contributor.get('login')
                    repo_contributor.contribution_count = contributor.get('contributions')
                    repo_contributor.save()
                    print(f"Updated repo_contributor record for repo {repo_id} of GitHub user {github_id}")

                except ObjectDoesNotExist:
                    Repo_contributor.objects.create(
                        repo_id=repo_id,
                        repo_url=contributor.get('repo_url'),
                        owner_github_id=github_id,
                        contributor_id=contributor.get('login'),
                        contribution_count=contributor.get('contributions')
                    )
                    print(f"Created repo_contributor record for repo {repo_id} of GitHub user {github_id}")

                except Exception as e:
                    message = f"Error processing contributor for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1

            print(f'({repo_count}/{total_repo_count}) Successfully processed contributors for GitHub user {github_id}')
            print(f"-"*50)

        # Check for any repositories that need to be removed
        for repo_id in repo_ids:
            if repo_id not in processed_repo_ids:
                remove_contributor_table(github_id, Repository(id=repo_id))

        return JsonResponse({
            "status": "OK",
            "message": "Contributor updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def remove_contributor_table(github_id, repository):
    try:
        contributor_table = Repo_contributor.objects.filter(owner_github_id=github_id, repo_id=repository.id)
        contributor_table.delete()
        print(f"The repo_contributor record for repo {repository.id} has been deleted successfully for GitHub user {github_id}")
        return JsonResponse({"status": "OK", "message": "The repo_contributor record has been deleted successfully"})

    except ObjectDoesNotExist:
        print(f"Repo_contributor record for repo '{repository.id}' does not exist for GitHub user {github_id}")
        return JsonResponse({"status": "Error", "message": f"Repo_contributor record for repo '{repository.id}' does not exist"}, status=404)
    except Exception as e:
        print(f"Error deleting repo_contributor record for repo '{repository.id}' for GitHub user {github_id}: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def repo_contributor_read_db(request):
    try:
        contributors = Repo_contributor.objects.all()
        contributor_list = [{'id': contributor.id, 'repo_id': contributor.repo_id, 'repo_url': contributor.repo_url, 'owner_github_id': contributor.owner_github_id, 'contributor_id': contributor.contributor_id, 'contributor_count': contributor.contributor_count} for contributor in contributors]
        return JsonResponse(contributor_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
# ---repo_issue API------------------------------------
def sync_repo_issue_db(request):
    try:
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
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']}'s issues of GitHub user {repo['github_id']}")
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the oldest 'open' issue
            open_issue = Repo_issue.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_issue = Repo_issue.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_issue:
                since = open_issue.last_update
            elif closed_issue:
                since = closed_issue.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/issues", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_issue_count = len(data)
            issue_count = 0

            if not isinstance(data, list):
                message = f"Invalid response format for issues of GitHub user {github_id} or Empty Repository"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            for issue_data in data:
                issue_count += 1
                print(f'({issue_count}/{total_issue_count}) Processing issue {issue_data.get("title")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    repo_issue = Repo_issue.objects.get(id=issue_data.get('id'))
                    repo_issue.repo_id = repo_id
                    repo_issue.repo_url = issue_data.get('repo_url')
                    repo_issue.owner_github_id = issue_data.get('owner_github_id')
                    repo_issue.state = issue_data.get('state')
                    repo_issue.title = issue_data.get('title')
                    repo_issue.publisher_github_id = issue_data.get('publisher_github_id')
                    repo_issue.last_update = issue_data.get('last_update')
                    repo_issue.save()
                    print(f"Updated repo_issue record for repo {repo_id} of GitHub user {github_id}: {issue_data.get('id')}")

                except ObjectDoesNotExist:
                    Repo_issue.objects.create(
                        id=issue_data.get('id'),
                        repo_id=repo_id,
                        repo_url=issue_data.get('repo_url'),
                        owner_github_id=issue_data.get('owner_github_id'),
                        state=issue_data.get('state'),
                        title=issue_data.get('title'),
                        publisher_github_id=issue_data.get('publisher_github_id'),
                        last_update=issue_data.get('last_update'),
                    )
                    print(f"Created repo_issue record for repo {repo_id} of GitHub user {github_id}: {issue_data.get('id')}")

                except Exception as e:
                    message = f"Error processing issue for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1

            print(f"Repo {repo_name}'s issue(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed issues for GitHub user {github_id}')
            print(f"-"*50)

        # Check for any repositories that need to be removed
        for repo_id in repo_ids:
            if repo_id not in processed_repo_ids:
                remove_issue_table(github_id, Repository(id=repo_id))

        return JsonResponse({
            "status": "OK",
            "message": "Repo issues updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def remove_issue_table(github_id, repository):
    try:
        issues = Repo_issue.objects.filter(owner_github_id=github_id, repo_id=repository.id)
        issues.delete()
        print(f"The repo_issue records for repo {repository.id} have been deleted successfully for GitHub user {github_id}")
        return JsonResponse({"status": "OK", "message": "The repo_issue records have been deleted successfully"})
    except ObjectDoesNotExist:
        print(f"Repo_issue records for repo '{repository.id}' do not exist for GitHub user {github_id}")
        return JsonResponse({"status": "Error", "message": f"Repo_issue records for repo '{repository.id}' do not exist"}, status=404)
    except Exception as e:
        print(f"Error deleting repo_issue records for repo '{repository.id}' for GitHub user {github_id}: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
def repo_issue_read_db(request):
    try:
        issues = Repo_issue.objects.all()
        issue_list = [{'id': issue.id, 'repo_id': issue.repo_id, 'repo_url': issue.repo_url, 'owner_github_id': issue.owner_github_id, 'state': issue.state, 'title': issue.title, 'publisher_github_id': issue.publisher_github_id, 'last_update': issue.last_update} for issue in issues]
        return JsonResponse(issue_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# ---repo_pr API------------------------------------
def sync_repo_pr_db(request):
    try:
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
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']} of GitHub user {repo['github_id']}")
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the oldest 'open' PR and the most recent 'closed' PR
            open_pr = Repo_pr.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_pr = Repo_pr.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_pr:
                since = open_pr.last_update
            elif closed_pr:
                since = closed_pr.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/pulls", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_pr_count = len(data)
            pr_count = 0
            if not isinstance(data, list):
                message = f"Invalid response format for PRs of GitHub user {github_id} or Empty Repository"
                print(message)
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            for pr_data in data:
                pr_count += 1
                print (f'{pr_count}/{total_pr_count} Processing PR {pr_data.get("title")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    pr = Repo_pr.objects.get(id=pr_data.get('id'))
                    pr.repo_id = repo_id
                    pr.repo_url = pr_data.get('repo_url')
                    pr.owner_github_id = pr_data.get('owner_github_id')
                    pr.title = pr_data.get('title')
                    pr.requester_id = pr_data.get('requester_id')
                    pr.published_date = pr_data.get('published_date')
                    pr.state = pr_data.get('state')
                    pr.last_update = pr_data.get('last_update')
                    pr.save()
                    print(f"Updated repo_pr record for repo {repo_id} of GitHub user {github_id}: {pr_data.get('id')}")

                except ObjectDoesNotExist:
                    Repo_pr.objects.create(
                        id=pr_data.get('id'),
                        repo_id=repo_id,
                        repo_url=pr_data.get('repo_url'),
                        owner_github_id=pr_data.get('owner_github_id'),
                        title=pr_data.get('title'),
                        requester_id=pr_data.get('requester_id'),
                        published_date=pr_data.get('published_date'),
                        state=pr_data.get('state'),
                        last_update=pr_data.get('last_update')
                    )
                    print(f"Created repo_pr record for repo {repo_id} of GitHub user {github_id}: {pr_data.get('id')}")

                except Exception as e:
                    message = f"Error processing PR for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue


            success_repo_count += 1

            print(f"Repo {repo_name}'s PR(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed PRs for GitHub user {github_id}')
            print(f"-"*50)

        # Check for any repositories that need to be removed
        for repo_id in repo_ids:
            if repo_id not in processed_repo_ids:
                remove_pr_table(github_id, Repository(id=repo_id))

        return JsonResponse({
            "status": "OK",
            "message": "Repo PRs updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def remove_pr_table(github_id, repository):
    try:
        prs = Repo_pr.objects.filter(owner_github_id=github_id, repo_id=repository.id)
        prs.delete()
        print(f"The repo_pr records for repo {repository.id} have been deleted successfully for GitHub user {github_id}")
        return JsonResponse({"status": "OK", "message": "The repo_pr records have been deleted successfully"})
    except ObjectDoesNotExist:
        print(f"Repo_pr records for repo '{repository.id}' do not exist for GitHub user {github_id}")
        return JsonResponse({"status": "Error", "message": f"Repo_pr records for repo '{repository.id}' do not exist"}, status=404)
    except Exception as e:
        print(f"Error deleting repo_pr records for repo '{repository.id}' for GitHub user {github_id}: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

    
def repo_pr_read_db(request):
    try:
        prs = Repo_pr.objects.all()
        pr_list = [{'id': pr.id, 'repo_id': pr.repo_id, 'repo_url': pr.repo_url, 'owner_github_id': pr.owner_github_id, 'title': pr.title, 'requester_id': pr.requester_id, 'published_date': pr.published_date, 'state': pr.state, 'last_update': pr.last_update} for pr in prs]
        return JsonResponse(pr_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------
# ---Repo_commit API------------------------------------
def sync_repo_commit_db(request):
    try:
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
            print(f'({repo_count}/{total_repo_count}) Processing repository {repo["name"]} commits of GitHub user {repo["github_id"]}')
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the latest commit
            latest_commit = Repo_commit.objects.filter(repo_id=repo_id).order_by('-last_update').first()
            if latest_commit is None:
                since = "2008-02-08T00:00:00Z"
            else:
                since = latest_commit.last_update

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/commit", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_commit_count = len(data)
            commit_count = 0

            if not isinstance(data, list):
                message = f"Invalid response format for commits of GitHub user {github_id} or Empty Repository"
                print(message)
                repo_count += 1
                failure_repo_count += 1
                failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                continue

            for commit_data in data:
                commit_count += 1
                print(f'{commit_count}/{total_commit_count} Processing commit {commit_data.get("sha")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    commit = Repo_commit.objects.get(sha=commit_data.get('sha'))
                    commit.sha = commit_data.get('sha')
                    commit.repo_id = repo_id
                    commit.repo_url = commit_data.get('repo_url')
                    commit.owner_github_id = commit_data.get('owner_github_id')
                    commit.committer_github_id = commit_data.get('committer_github_id')
                    commit.added_lines = commit_data.get('added_lines')
                    commit.deleted_lines = commit_data.get('deleted_lines')
                    commit.last_update = commit_data.get('last_update')
                    commit.save()
                    print(f"Updated repo_commit record for repo {repo_id} of GitHub user {github_id}: {commit_data.get('sha')}")

                except ObjectDoesNotExist:
                    Repo_commit.objects.create(
                        sha=commit_data.get('sha'),
                        repo_id=repo_id,
                        repo_url=commit_data.get('repo_url'),
                        owner_github_id=commit_data.get('owner_github_id'),
                        committer_github_id=commit_data.get('committer_github_id'),
                        added_lines=commit_data.get('added_lines'),
                        deleted_lines=commit_data.get('deleted_lines'),
                        last_update=commit_data.get('last_update')
                    )
                    print(f"Created repo_commit record for repo {repo_id} of GitHub user {github_id}: {commit_data.get('sha')}")

                except Exception as e:
                    message = f"Error processing commit for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    failure_repo_count += 1
                    failure_repo_details.append({"github_id": github_id, "repo_name": repo_name, "message": message})
                    continue

            success_repo_count += 1
            print(f"Repo {repo_name}'s commit(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed commits for GitHub user {github_id}')
            print(f"-"*50)

        # Check for any repositories that need to be removed
        for repo_id in repo_ids:
            if repo_id not in processed_repo_ids:
                remove_commit_table(github_id, Repository(id=repo_id))

        return JsonResponse({
            "status": "OK",
            "message": "Repo commits updated successfully",
            "success_repo_count": success_repo_count,
            "failure_repo_count": failure_repo_count,
            "failure_repo_details": failure_repo_details
        })
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def remove_commit_table(github_id, repository):
    try:
        commits = Repo_commit.objects.filter(owner_github_id=github_id, repo_id=repository.id)
        commits.delete()
        print(f"The repo_commit records for repo {repository.id} have been deleted successfully for GitHub user {github_id}")
        return JsonResponse({"status": "OK", "message": "The repo_commit records have been deleted successfully"})
    except ObjectDoesNotExist:
        print(f"Repo_commit records for repo '{repository.id}' do not exist for GitHub user {github_id}")
        return JsonResponse({"status": "Error", "message": f"Repo_commit records for repo '{repository.id}' do not exist"}, status=404)
    except Exception as e:
        print(f"Error deleting repo_commit records for repo '{repository.id}' for GitHub user {github_id}: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def repo_commit_read_db(request):
    try: 
        commits = Repo_commit.objects.all()
        commit_list = [{'sha': commit.sha, 'repo_id': commit.repo_id, 'repo_url': commit.repo_url, 'owner_github_id': commit.owner_github_id, 'committer_github_id': commit.committer_github_id, 'added_lines': commit.added_lines, 'deleted_lines': commit.deleted_lines, 'last_update': commit.last_update} for commit in commits]
        return JsonResponse(commit_list, safe=False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# -----------------------------------------------------

# TEST
# --- REPO TEST ---
def sync_repo_db_test(request):
    try:
        github_id = request.GET.get('github_id')

        student = Student.objects.get(github_id=github_id)
        if not student:
            return JsonResponse({"status": "Error", "message": "Student not found"}, status=404)
        
        print(f"Processing repositories for GitHub user {github_id}")
            
        response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user/repos", params={'github_id': github_id})
        if response.status_code != 200:
            message = f"Failed to fetch repositories for GitHub user {github_id}"
            print(message)
            return JsonResponse({"status": "Error", "message": message}, status=500)
        
        total_repo_count = len(response.json())
        repo_count = 0

        data = response.json()
        if not isinstance(data, list):
            message = f"Invalid response format for repositories of GitHub user {github_id}"
            print(message)
            return JsonResponse({"status": "Error", "message": message}, status=500)


        repo_list = [{'id': repo['id'], 'name': repo['name']} for repo in data]
            
        # Check for any repositories that need to be removed
        repos_in_db = Repository.objects.filter(owner_github_id=github_id).values_list('id', flat=True)
        for repo_id in repos_in_db:
            if repo_id not in [str(repo['id']) for repo in repo_list]:
                remove_repository(github_id, Repository(id=repo_id))


        for repo in repo_list:
            repo_name = repo['name']
            repo_id = repo['id']
            repo_count += 1
            print(f'({repo_count}/{total_repo_count}) Processing repository {repo_name} of GitHub user {github_id}')
            repo_response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos", params={'github_id': github_id, 'repo_id': repo_id})
            if repo_response.status_code != 200:
                message = f"Failed to fetch data for repo {repo_name} of GitHub user {github_id}"
                print(message)
                continue

            repo_data = repo_response.json()
            print(repo_data)

            if isinstance(repo_data, dict):
                try:
                    repository_record = Repository.objects.get(owner_github_id=github_id, id=repo_id)
                    #repository_record.name = repo_name
                    repository_record.url = repo_data.get('url')
                    repository_record.created_at = repo_data.get('created_at')
                    repository_record.updated_at = repo_data.get('updated_at')
                    repository_record.fork_count = repo_data.get('forks_count')
                    repository_record.star_count = repo_data.get('stars_count')
                    repository_record.commit_count = repo_data.get('commit_count')
                    repository_record.open_issue_count = repo_data.get('open_issue_count')
                    repository_record.closed_issue_count = repo_data.get('closed_issue_count')
                    repository_record.language = ', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None'
                    repository_record.contributors = ', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None'
                    repository_record.license = repo_data.get('license')
                    repository_record.has_readme = repo_data.get('has_readme')
                    repository_record.description = repo_data.get('description')
                    repository_record.release_version = repo_data.get('release_version')
                    repository_record.crawled_date = repo_data.get('crawled_date'),
                    repository_record.save()
                    print(f"Updated repository {repo_name} for GitHub user {github_id}")

                except ObjectDoesNotExist:
                    Repository.objects.create(
                        id = repo_data.get('id'),
                        #name=repo_name,
                        url=repo_data.get('url'),
                        owner_github_id=github_id,
                        created_at=repo_data.get('created_at'),
                        updated_at=repo_data.get('updated_at'),
                        fork_count=repo_data.get('forks_count'),
                        star_count=repo_data.get('stars_count'),
                        commit_count=repo_data.get('commit_count'),
                        open_issue_count=repo_data.get('open_issue_count'),
                        closed_issue_count=repo_data.get('closed_issue_count'),
                        language=', '.join(repo_data.get('language', [])) if isinstance(repo_data.get('language'), list) else 'None',
                        contributors=', '.join(repo_data.get('contributors', [])) if isinstance(repo_data.get('contributors'), list) else 'None',
                        license=repo_data.get('license'),
                        has_readme=repo_data.get('has_readme'),
                        description=repo_data.get('description'),
                        release_version=repo_data.get('release_version'),
                        crawled_date=repo_data.get('crawled_date'),
                    )
                    print(f"Created repository {repo_name} for GitHub user {github_id}")

                except Exception as e:
                    message = f"Error processing repository {repo_name} for GitHub user {github_id}: {str(e)}"
                    print(message)
                    continue

            else:
                message = f"Invalid response format for repository {repo_name} of GitHub user {github_id}"
                print(message)
                continue
                
            print(f'({repo_count}/{total_repo_count}) Successfully processed repository {repo_name} of GitHub user {github_id}')

        #Calculate total star count for the student
        total_star_count = Repository.objects.filter(owner_github_id=github_id).aggregate(total_star_count=Sum('star_count'))['total_star_count']
        if total_star_count is None:
            total_star_count = 0

        # Update the student's starred_count
        student_record = Student.objects.get(github_id=github_id)
        student_record.starred_count = total_star_count
        student_record.save()

        print(f'Student starred count updated successfully for GitHub user {github_id}')

        print(f'Github_id: {github_id} - Repositories updated successfully')

        return JsonResponse({"status": "OK", "message": "Repositories updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
# --- REPO CONTRIBUTOR TEST ---
def sync_repo_contributor_db_test(request):
    try:

        github_id = request.GET.get('github_id')

        repositories = Repository.objects.filter(owner_github_id=github_id) 
        if not repositories:
            return JsonResponse({"status": "Error", "message": "Repositories not found"}, status=404)
        
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)
        repo_count = 0

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        # Iterate through each repository and update/create Repo_contributor records
        for repo in repo_list:
            repo_count += 1
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']}'s contributors of GitHub user {repo['github_id']}")
            repo_id = repo['id']
            repo_name = repo['name']
            github_id = repo['github_id']
            processed_repo_ids.add(repo_id)

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/contributor", params={'github_id': github_id, 'repo_name': repo_name})
            contributor_data = response.json()

            total_contributor_count = len(contributor_data)
            contributor_count = 0

            # Check if the data is a list
            if not isinstance(contributor_data, list):
                message = f"Invalid response format for repository {repo_name} of GitHub user {github_id} or Empty Repository"
                print(message)
                repo_count += 1
                continue

            for contributor in contributor_data:
                contributor_count += 1
                print(f'({contributor_count}/{total_contributor_count}) Processing contributor {contributor.get("login")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    repo_contributor = Repo_contributor.objects.get(owner_github_id=github_id, repo_id=repo_id, contributor_id=contributor.get('login'))
                    repo_contributor.contributor_id = contributor.get('login')
                    repo_contributor.contribution_count = contributor.get('contributions')
                    repo_contributor.save()
                    print(f"Updated repo_contributor record for repo {repo_id} of GitHub user {github_id}")

                except ObjectDoesNotExist:
                    Repo_contributor.objects.create(
                        repo_id=repo_id,
                        repo_url=contributor.get('repo_url'),
                        owner_github_id=github_id,
                        contributor_id=contributor.get('login'),
                        contribution_count=contributor.get('contributions')
                    )
                    print(f"Created repo_contributor record for repo {repo_id} of GitHub user {github_id}")

                except Exception as e:
                    message = f"Error processing contributor for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    continue

        print(f'({repo_count}/{total_contributor_count}) Successfully processed contributors for GitHub user {github_id}')


        
        return JsonResponse({"status": "OK", "message": "Repositories updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
#-----------------------------------------------------
# --- REPO ISSUE TEST --
def sync_repo_issue_db_test(request):
    try:    
        github_id = request.GET.get('github_id')

        repositories = Repository.objects.filter(owner_github_id=github_id) 
        if not repositories:
            return JsonResponse({"status": "Error", "message": "Repositories not found"}, status=404)
        
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)
        repo_count = 0

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        # Iterate through each repository and update/create Repo_contributor records
        for repo in repo_list:
            repo_count += 1
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']}'s issues of GitHub user {repo['github_id']}")
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the oldest 'open' issue
            open_issue = Repo_issue.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_issue = Repo_issue.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_issue:
                since = open_issue.last_update
            elif closed_issue:
                since = closed_issue.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/issues", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_issue_count = len(data)
            issue_count = 0

            if not isinstance(data, list):
                message = f"Invalid response format for issues of GitHub user {github_id} or Empty Repository"
                print(message)
                continue

            for issue_data in data:
                issue_count += 1
                print(f'{issue_count}/{total_issue_count} Processing issue {issue_data.get("title")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    repo_issue = Repo_issue.objects.get(id=issue_data.get('id'))
                    repo_issue.repo_id = repo_id
                    repo_issue.repo_url = issue_data.get('repo_url')
                    repo_issue.owner_github_id = issue_data.get('owner_github_id')
                    repo_issue.state = issue_data.get('state')
                    repo_issue.title = issue_data.get('title')
                    repo_issue.publisher_github_id = issue_data.get('publisher_github_id')
                    repo_issue.last_update = issue_data.get('last_update')
                    repo_issue.save()
                    print(f"Updated repo_issue record for repo {repo_id} of GitHub user {github_id}: {issue_data.get('id')}")

                except ObjectDoesNotExist:
                    Repo_issue.objects.create(
                        id=issue_data.get('id'),
                        repo_id=repo_id,
                        repo_url=issue_data.get('repo_url'),
                        owner_github_id=issue_data.get('owner_github_id'),
                        state=issue_data.get('state'),
                        title=issue_data.get('title'),
                        publisher_github_id=issue_data.get('publisher_github_id'),
                        last_update=issue_data.get('last_update'),
                    )
                    print(f"Created repo_issue record for repo {repo_id} of GitHub user {github_id}: {issue_data.get('id')}")

                except Exception as e:
                    message = f"Error processing issue for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    continue

            print(f"Repo {repo_name}'s issue(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed issues for GitHub user {github_id}')

        return JsonResponse({"status": "OK", "message": "Repo issues updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
#-----------------------------------------------------
# --- REPO PR TEST --
def sync_repo_pr_db_test(request):
    try:
        github_id = request.GET.get('github_id')

        repositories = Repository.objects.filter(owner_github_id=github_id) 
        if not repositories:
            return JsonResponse({"status": "Error", "message": "Repositories not found"}, status=404)
        
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)
        repo_count = 0

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        for repo in repo_list:
            repo_count += 1
            print(f"({repo_count}/{total_repo_count}) Processing repository {repo['name']} of GitHub user {repo['github_id']}")
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the oldest 'open' PR and the most recent 'closed' PR
            open_pr = Repo_pr.objects.filter(repo_id=repo_id, state='open').order_by('last_update').first()
            closed_pr = Repo_pr.objects.filter(repo_id=repo_id, state='closed').order_by('-last_update').first()

            if open_pr:
                since = open_pr.last_update
            elif closed_pr:
                since = closed_pr.last_update
            else:
                since = "2008-02-08T00:00:00Z"

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/pulls", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_pr_count = len(data)
            pr_count = 0
            if not isinstance(data, list):
                message = f"Invalid response format for PRs of GitHub user {github_id} or Empty Repository"
                print(message)
                continue

            for pr_data in data:
                pr_count += 1
                print (f'({pr_count}/{total_pr_count}) Processing PR {pr_data.get("title")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    pr = Repo_pr.objects.get(id=pr_data.get('id'))
                    pr.repo_id = repo_id
                    pr.repo_url = pr_data.get('repo_url')
                    pr.owner_github_id = pr_data.get('owner_github_id')
                    pr.title = pr_data.get('title')
                    pr.requester_id = pr_data.get('requester_id')
                    pr.published_date = pr_data.get('published_date')
                    pr.state = pr_data.get('state')
                    pr.last_update = pr_data.get('last_update')
                    pr.save()
                    print(f"Updated repo_pr record for repo {repo_id} of GitHub user {github_id}: {pr_data.get('id')}")

                except ObjectDoesNotExist:
                    Repo_pr.objects.create(
                        id=pr_data.get('id'),
                        repo_id=repo_id,
                        repo_url=pr_data.get('repo_url'),
                        owner_github_id=pr_data.get('owner_github_id'),
                        title=pr_data.get('title'),
                        requester_id=pr_data.get('requester_id'),
                        published_date=pr_data.get('published_date'),
                        state=pr_data.get('state'),
                        last_update=pr_data.get('last_update')
                    )
                    print(f"Created repo_pr record for repo {repo_id} of GitHub user {github_id}: {pr_data.get('id')}")

                except Exception as e:
                    message = f"Error processing PR for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    continue


            print(f"Repo {repo_name}'s PR(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed PRs for GitHub user {github_id}')


        return JsonResponse({"status": "OK", "message": "Repo PRs updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
#-----------------------------------------------------
# --- REPO COMMIT TEST --
def sync_repo_commit_db_test(request):
    try:
        github_id = request.GET.get('github_id')

        repositories = Repository.objects.filter(owner_github_id=github_id) 
        if not repositories:
            return JsonResponse({"status": "Error", "message": "Repositories not found"}, status=404)
        
        repo_list = [{'id': repo.id, 'name': repo.name, 'github_id': repo.owner_github_id} for repo in repositories]
        total_repo_count = len(repo_list)
        repo_count = 0

        # Track processed repository IDs to identify deletions later
        processed_repo_ids = set()

        for repo in repo_list:
            repo_count += 1
            print(f'({repo_count}/{total_repo_count}) Processing repository {repo["name"]} commits of GitHub user {repo["github_id"]}')
            processed_repo_ids.add(repo['id'])
            repo_id = repo['id']
            github_id = repo['github_id']
            repo_name = repo['name']

            # Try to get the latest commit
            latest_commit = Repo_commit.objects.filter(repo_id=repo_id).order_by('-last_update').first()
            if latest_commit is None:
                since = "2008-02-08T00:00:00Z"
            else:
                since = latest_commit.last_update

            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/repos/commit", params={'github_id': github_id, 'repo_name': repo_name, 'since': since})
            data = response.json()

            total_commit_count = len(data)
            commit_count = 0

            if not isinstance(data, list):
                message = f"Invalid response format for commits of GitHub user {github_id} or Empty Repository"
                print(message)
                continue

            for commit_data in data:
                commit_count += 1
                print(f'({commit_count}/{total_commit_count}) Processing commit {commit_data.get("sha")} for repo {repo_name} of GitHub user {github_id}')
                try:
                    commit = Repo_commit.objects.get(sha=commit_data.get('sha'))
                    commit.sha = commit_data.get('sha')
                    commit.repo_id = repo_id
                    commit.repo_url = commit_data.get('repo_url')
                    commit.owner_github_id = commit_data.get('owner_github_id')
                    commit.committer_github_id = commit_data.get('committer_github_id')
                    commit.added_lines = commit_data.get('added_lines')
                    commit.deleted_lines = commit_data.get('deleted_lines')
                    commit.last_update = commit_data.get('last_update')
                    commit.save()
                    print(f"Updated repo_commit record for repo {repo_id} of GitHub user {github_id}: {commit_data.get('sha')}")

                except ObjectDoesNotExist:
                    Repo_commit.objects.create(
                        sha=commit_data.get('sha'),
                        repo_id=repo_id,
                        repo_url=commit_data.get('repo_url'),
                        owner_github_id=commit_data.get('owner_github_id'),
                        committer_github_id=commit_data.get('committer_github_id'),
                        added_lines=commit_data.get('added_lines'),
                        deleted_lines=commit_data.get('deleted_lines'),
                        last_update=commit_data.get('last_update')
                    )
                    print(f"Created repo_commit record for repo {repo_id} of GitHub user {github_id}: {commit_data.get('sha')}")

                except Exception as e:
                    message = f"Error processing commit for repo {repo_name} of GitHub user {github_id}: {str(e)}"
                    print(message)
                    continue
 
            print(f"Repo {repo_name}'s commit(s) updated successfully for GitHub user {github_id}")
            print(f'({repo_count}/{total_repo_count}) Successfully processed commits for GitHub user {github_id}')
            
        return JsonResponse({"status": "OK", "message": "Repo commits updated successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
#-----------------------------------------------------