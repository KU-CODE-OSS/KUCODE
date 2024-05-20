from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import User,Student
import requests

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def student_create_db (request):
    try:
        id = request.GET.get('id')
        github_id = request.GET.get('github_id')

        # 빈 값인 경우 에러 처리
        if not id or not github_id:
            raise ValueError("ID and GitHub ID cannot be empty")
        
        # 이미 존재하는 학생인 경우 에러 처리
        if Student.objects.filter(id=id).exists():
            raise ValueError("Student with this ID already exists")

        student = Student.objects.create(
            id=id,
            github_id=github_id,
        )

        return JsonResponse({"status": "OK", "message": "Student record created successfully"})
    except ValueError as ve:
        return JsonResponse({"status": "Error", "message": str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def student_read_db(request):
    try:
        github_id = request.GET.get('github_id')
        student = Student.objects.get(github_id=github_id)
        if student is None:
            return JsonResponse({"status": "Error", "message": "User doesn't exist"})
       
        data = {
            "id":student.id,
            "github_id": student.github_id,
            "name": student.name,
            "department": student.department,
            "double_major": student.double_major,
            "college": student.college,
            "primary_email": student.primary_email,
            "secondary_email": student.secondary_email,
            "follower_count": student.follower_count,
            "following_count": student.following_count,
            "public_repo_count": student.public_repo_count,
            "github_profile_create_at": student.github_profile_create_at,
            "github_profile_update_at": student.github_profile_update_at
        }
        return JsonResponse(data)
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def student_update_db(request):
    try:
        github_id = request.GET.get('github_id')
        response= requests.get("http://119.28.232.108:5000/api/user",params={'github_id':github_id})
        if response.status_code == 404:
            return JsonResponse({"status": "Error", "message": "GitHub user not found"}, status=404)
        data = response.json()

        # 데이터에서 필요한 정보 추출
        github_id = data.get('GithubID')
        follower_count = data.get('Follower_CNT')
        following_count = data.get('Following_CNT')
        public_repo_count = data.get('Public_repos_CNT')
        github_profile_create_at = data.get('Github_profile_Create_Date')
        github_profile_update_at = data.get('Github_profile_Update_Date')

        # Student 객체 생성
        student = Student.objects.get(github_id=github_id) 
        student.follower_count=int(follower_count)
        student.following_count=int(following_count)
        student.public_repo_count=int(public_repo_count)
        student.github_profile_create_at=github_profile_create_at
        student.github_profile_update_at=github_profile_update_at

        student.save()
    
        return JsonResponse({"status": "OK", "message": "Student record update successfully"})
   
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)       

def student_delete_db(request):
    try:
        github_id = request.GET.get('github_id')
        student = Student.objects.get(github_id=github_id)

        student.delete()  # 사용자 객체를 삭제합니다.
        return JsonResponse({"status": "OK", "message": "Student record deleted successfully"})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

