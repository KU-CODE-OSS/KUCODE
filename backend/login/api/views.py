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