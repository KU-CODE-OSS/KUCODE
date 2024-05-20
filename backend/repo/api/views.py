from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from repo.models import Repository
import requests

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def repo_create_db (request):
    try:
        github_id = request.GET.get('github_id')
        repo = request.GET.get('repo')

        if not repo or not github_id:
            raise ValueError("repo and GitHub ID cannot be empty")
         
        if Repository.objects.filter(owner_github_id=github_id, name=repo).exists():
            raise ValueError("repo already exists.")
         
        response= requests.get("http://119.28.232.108:5000/api/repos",params={'github_id':github_id,'repo_name':repo})
        if response.status_code == 404:
            return JsonResponse({"status": "Error", "message": "Repo has not been found"}, status=404)        
        data = response.json()

        id = data.get('id')
        name = data.get('name')
        url = data.get('url')
        owner_github_id = data.get('owner_github_id')
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        forks_count = data.get('forks_count')
        stars_count = data.get('stars_count')
        commit_count = data.get('commit_count')
        open_issue_count = data.get('open_issue_count')
        closed_issue_count = data.get('closed_issue_count')
        language = ', '.join(data.get('language', []))
        contributors = ', '.join(data.get('contributors', []))
        license = str(data.get('license'))
        has_readme = data.get('has_readme')
        description = data.get('description')
        release_version = data.get('release_version')

        repository = Repository.objects.create(
            id=id,
            name=name,
            url=url,
            owner_github_id=owner_github_id,
            created_at=created_at,
            updated_at=updated_at,
            fork_count=forks_count,
            star_count=stars_count,
            commit_count=commit_count,
            open_issue_count=open_issue_count,
            closed_issue_count=closed_issue_count,
            languate=language,
            contributor=contributors,
            license=license,
            has_readme=has_readme,
            description=description,
            release_version=release_version,
        )
        return JsonResponse({"status": "OK", "message": "The repo has been created successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)     

def repo_read_db(request):
    try:
        github_id = request.GET.get('github_id')
        repo = request.GET.get('repo')

        repository = Repository.objects.get(owner_github_id=github_id, name=repo)

       
        data = {
            "id":repository.id,
            "name": repository.name,
            "url": repository.url,
            "owner_github_id": repository.owner_github_id,
            "created_at": repository.created_at,
            "updated_at": repository.updated_at,
            "forks_count": repository.fork_count,
            "stars_count": repository.star_count,
            "commit_count": repository.commit_count,
            "open_issue_count": repository.open_issue_count,
            "closed_issue_count": repository.closed_issue_count,
            "language": repository.languate,
            "contributors": repository.contributor,
            "license": repository.license,
            "has_readme": repository.has_readme,
            "description": repository.description,
            "release_version": repository.release_version,
            "etc": repository.etc,
            "crawled_date": repository.crawled_date,
        }
        return JsonResponse(data)
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Repo '{repo}' does not exist"}, status=404)    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def repo_update_db(request):
    try:
        github_id = request.GET.get('github_id')
        repo = request.GET.get('repo')

        response= requests.get("http://119.28.232.108:5000/api/repos",params={'github_id':github_id,'repo_name':repo})
        data = response.json()

        # 데이터에서 필요한 정보 추출
        id = data.get('id')
        name = data.get('name')
        url = data.get('url')
        owner_github_id = data.get('owner_github_id')
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        forks_count = data.get('forks_count')
        stars_count = data.get('stars_count')
        commit_count = data.get('commit_count')
        open_issue_count = data.get('open_issue_count')
        closed_issue_count = data.get('closed_issue_count')
        language = ', '.join(data.get('language', []))
        contributors = ', '.join(data.get('contributors', []))
        license = str(data.get('license'))
        has_readme = data.get('has_readme')
        description = data.get('description')
        release_version = data.get('release_version')


        # Repo 업데이트
        repository = Repository.objects.get(id=id)
        repository.name = name
        repository.url = url   
        repository.owner_github_id = owner_github_id   
        repository.created_at = created_at
        repository.updated_at = updated_at
        repository.fork_count = forks_count
        repository.star_count = stars_count
        repository.commit_count = commit_count
        repository.open_issue_count = open_issue_count
        repository.closed_issue_count = closed_issue_count
        repository.languate = language
        repository.contributor = contributors
        repository.license = license
        repository.has_readme = has_readme
        repository.description = description
        repository.release_version = release_version
        repository.save()
        return JsonResponse({"status": "OK", "message": "Student record update successfully"})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Repo '{repo}' does not exist"}, status=404)    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def repo_delete_db(request):
    try:
        github_id = request.GET.get('github_id')
        repo = request.GET.get('repo')        
        repository = Repository.objects.get(owner_github_id=github_id, name=repo)
        repository.delete()  # 사용자 객체를 삭제합니다.
        return JsonResponse({"status": "OK", "message": "The repo has been deleted successfully"})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Repo '{repo}' does not exist"}, status=404)    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

