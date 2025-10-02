from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import User,Student,Administration
from course.models import Course, Course_registration, Course_project
from repo.models import Repo_commit, Repo_pr ,Repo_issue, Repository
from login.models import Member, Student as LoginStudent
from django.db.models import Sum
from openpyxl import load_workbook
from django.db.models import Q
from datetime import datetime

from django.db.models.functions import ExtractYear
from django.shortcuts import redirect, reverse
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission

import requests



temp_student_id = ''

def github_login(request):
    try: 
        # OpenAPI 고려대 로그인 정보 받음
        global temp_student_id
        temp_student_id = ''        
        name = ''

        specific_student, created = Student.objects.get_or_create(id=temp_student_id,name = name)

        if specific_student.github_id is None:
            client_id = settings.OAUTH_CLIENT_ID 

            scope = "read:user"
            return redirect(
                f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
        )
        else :
            return  JsonResponse('The github_id for 2023021688 already exists! You will be logined directly!',safe= False)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def callback(request):
    try:
        global temp_student_id
        code = request.GET.get("code", None)
        if code is None:
            print('Code is empty!!')
            return 
       
        client_id = settings.OAUTH_CLIENT_ID 
        client_secret = settings.OAUTH_CLIENT_SECRET
        token_request = requests.post(
            f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
            headers={"Accept": "application/json"},
        )
        token_json = token_request.json()
        
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_request.json()
        username = profile_json.get("login", None)
        name = profile_json.get("name", None)
        email = profile_json.get("email", None)
        url = profile_json.get("url", None)
        
        specific_student = Student.objects.get(id=temp_student_id)
        specific_student.github_id = username 
        specific_student.save()
        temp_student_id = ''
        
        return JsonResponse({   
            "username": username,
            "url": url,
            "name": name,
            "email": email
        })
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def admin_login(request):
    try: 
        example_id ='2023021688'
        specific_admin = Administration.objects.get(id=example_id)
        return JsonResponse({
            "id":specific_admin.id,
            "name":specific_admin.name,
            "department":specific_admin.department,
            "double_major":specific_admin.double_major,
            "college":specific_admin.college
        })
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


@api_view(['POST'])
@csrf_exempt
def signup(request):
    """
    회원가입 API
    프론트엔드로부터 UUID와 학번을 받아서 login_member와 login_student 테이블에 저장
    """
    try:
        # 요청 데이터 추출
        data = request.data
        uuid = data.get('uuid')
        student_id = data.get('student_id')
        name = data.get('name', '')  # 이름은 선택사항
        email = data.get('email', '')  # 이메일은 선택사항
        
        # 필수 필드 검증
        if not uuid:
            return JsonResponse({
                "status": "Error", 
                "message": "UUID는 필수입니다."
            }, status=400)
            
        if not student_id:
            return JsonResponse({
                "status": "Error", 
                "message": "학번은 필수입니다."
            }, status=400)
        
        # UUID가 이미 존재하는지 확인
        if Member.objects.filter(id=uuid).exists():
            return JsonResponse({
                "status": "Error", 
                "message": "이미 존재하는 UUID입니다."
            }, status=400)
        
        # 학번이 이미 존재하는지 확인
        if LoginStudent.objects.filter(id=student_id).exists():
            return JsonResponse({
                "status": "Error", 
                "message": "이미 존재하는 학번입니다."
            }, status=400)
        
        # 트랜잭션으로 Member와 Student 생성
        from django.db import transaction
        
        with transaction.atomic():
            # Member 생성
            member = Member.objects.create(
                id=uuid,
                role='STUDENT',  # 기본값
                name=name,
                email=email
            )
            
            # Student 생성
            student = LoginStudent.objects.create(
                member=member,
                id=student_id,
                github_auth='LOCKED'  # 기본값
            )
        
        return JsonResponse({
            "status": "Success",
            "message": "회원가입이 완료되었습니다.",
            "data": {
                "uuid": member.id,
                "student_id": student.id,
                "name": member.name,
                "email": member.email,
                "role": member.role,
                "github_auth": student.github_auth
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            "status": "Error", 
            "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"
        }, status=500)