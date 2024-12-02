from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from account.models import User,Student
from course.models import Course, Course_registration, Course_project
from repo.models import Repo_commit, Repo_pr ,Repo_issue, Repository,Repo_contributor
from django.db.models import Sum,Count
from openpyxl import load_workbook
from django.db.models import Q
from datetime import datetime

from django.db.models.functions import ExtractYear

import requests
import pandas as pd
import subprocess

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

# ========================================
# Backend Function
# ========================================
# ------------Main--------------#
def sync_student_db(request):
    try:
        # Fetch all students
        students = Student.objects.all()
        student_list = [{'id': student.id, 'github_id': student.github_id} for student in students]
        
        total_student_count = len(student_list)
        student_count = 0
        
        success_count = 0
        failure_count = 0
        failure_details = []

        # Process each student
        for student in student_list:
            student_count += 1
            print(f'\n{"="*10} [{student_count}/{total_student_count}] Processing student ID: {student["id"]} (GitHub ID: {student["github_id"]}) {"="*10}')
            
            id = student['id']
            github_id = student['github_id']
            
            # Fetch GitHub user data
            response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user", params={'github_id': github_id})
            if response.status_code == 404:
                message = f"[ERROR] GitHub user {github_id} not found"
                print(message)
                failure_count += 1
                failure_details.append({"id": id, "github_id": github_id, "message": message})
                continue

            data = response.json()
            
            try:
                print(f"Received data for GitHub ID {github_id}: {data}")
                # Update or create student record
                student_record, created = Student.objects.update_or_create(
                    github_id__iexact=github_id,
                    defaults={
                        'follower_count': data.get('Follower_CNT'),
                        'following_count': data.get('Following_CNT'),
                        'public_repo_count': data.get('Public_repos_CNT'),
                        'github_profile_create_at': data.get('Github_profile_Create_Date'),
                        'github_profile_update_at': data.get('Github_profile_Update_Date')
                    }
                )

                action = "Created" if created else "Updated"
                message = f"Student record {action}: ID {id}, GitHub ID {github_id}"
                print(f"[SUCCESS] {message}")
                success_count += 1

            except Exception as e:
                message = f"[ERROR] Error processing student: ID {id}, GitHub ID {github_id} - {str(e)}"
                print(message)
                failure_count += 1
                failure_details.append({"id": id, "github_id": github_id, "message": message})

            print(f'-'*5)

        return JsonResponse({
            "status": "OK", 
            "message": "Student records processed successfully", 
            "success_count": success_count,
            "failure_count": failure_count,
            "failure_details": failure_details
        })
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Delete--------------#
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
    
# ---------------------------------------------

# ========================================
# Frontend Function
# ========================================
# ------------Excel import --------------#
@csrf_exempt
def student_excel_import(request):
    try:
        # Get the file from the request
        file = request.FILES['file']
        print("file received!")
        # Check if the file is of type .xlsx
        if not file.name.endswith('.xlsx'):
            return JsonResponse({"status": "Error", "message": "File type is not supported"}, status=400)
        
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file, header=None)  # Treat the first row as data, automatically assign column names
        print(df)
        course_id = str(df.iloc[0, 0])
        year = int(df.iloc[0, 1])
        semester = int(df.iloc[0,2])

        if not course_id  or not year  or not semester :
            return JsonResponse({"status": "Error", "message": "Course information has to be included"}, status=400)

        if Course.objects.filter(course_id=course_id,year=year,semester=semester).exists():
            print("The course already exists.!!!")
        else:
            course = Course.objects.create(
            course_id = df.iloc[0, 0],
            year = int(df.iloc[0, 1]),
            semester = int(df.iloc[0,2]),
            name=df.iloc[0,3],
            prof=df.iloc[0,4],
            ta=df.iloc[0,5],
            student_count = len(df) -1, 
            course_repo_name = str(year)+str(semester)+course_id
            )

        course = Course.objects.get(course_id=course_id,year=year,semester=semester)
        missing_list =[]        

        for index, row in df.iloc[1:].iterrows():
            # 필수 매개변수에 누락된 값이 있는지 확인
            
            if pd.isnull(row[0]) or pd.isnull(row[1]) or pd.isnull(row[2]):
                print(f"Student with id {row[0]} has missing values")   
                missing_list.append(str(row[0]))
                continue
            
            row[0] = str(row[0])  # 첫 번째 열을 문자열 형식으로 변환

            
            # 학생이 이미 존재하는지 확인
            if Student.objects.filter(id=row[0]).exists():
                print(f"Student with id {row[0]} already exists")
            
            else:
                # 디버깅을 위해 학생 세부 정보 출력
                print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

                # 새 Student 객체 생성
                Student.objects.create(
                    id=row[0],
                    name=row[1],
                    github_id=row[2],
                    department=row[3],
                    double_major=row[4],
                    college=row[5],
                    primary_email=row[6],
                    secondary_email=row[7],
                    enrollment=row[8],
                )
                print(f"{row[0]} Student has been created! ")

            student = Student.objects.get(id=row[0])
            
            if Course_registration.objects.filter(course=course,student=student,course_year=course.year,course_semester=course.semester).exists():
                print(f"{course.name}-{student.name} has been already registered")

            else:   # Course_registration 채우기
                Course_registration.objects.create(
                    course=course,
                    course_year=year,
                    course_semester=semester,
                    student=student
                  )
                print(f"{course.name}-{student.name} has been registered!")


        if len(missing_list) >= 1:
            return JsonResponse({"status": "Error", "message": "Missing values for some students", "missing_students": missing_list}, status=400)        
        else :
            return JsonResponse({"status": "OK", "message": "Student record has been imported successfully"})
    
    except Exception as e:
        print(str(e))
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Student's course_reated info --------------#
def student_read_course_info(request):
    try:
        data = []
        students = Student.objects.all()
        for student in students:
            try:
                # 특정 하나의 학생에 대해 진행             
                total_commit = 0 
                total_pr = 0
                total_issue = 0
                total_repo = 0
                total_star = 0

                etc_total_commit = 0 
                etc_total_pr = 0
                etc_total_issue = 0
                etc_total_repo = 0
                etc_total_star = 0

                # 특정 학생의 모든 레포지토리 가져옴
                student_repos = Repository.objects.filter(owner_github_id=student.github_id)
                
                # 특정 학생의 수강 목록들 가져옴
                course_reg_list = Course_registration.objects.filter(student=student)

                # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
                courses_repos = Course_project.objects.filter(repo__in=student_repos)
                
                # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
                course_ids = []
                for course_reg in course_reg_list:
                    course_ids.append(course_reg.course.course_id)

                # 딕셔너리 초기화
                course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0, 'star': 0} for course_id in course_ids}

                courses_project_repos = []

                for c in courses_repos:
                    courses_project_repos.append(c.repo)

                # 각 repo에 대한 정보 추가
                for repo in student_repos:
                    if repo in courses_project_repos:  # 특정 학생의 현재 가리키는 repo가 과목과 관련이 있는 경우
                        specific_course = Course_project.objects.get(repo=repo)
                        course_id = specific_course.course.course_id

                        # Commit 수 합산
                        total_commit_count = Repository.objects.filter(
                            id = specific_course.repo.id,
                            owner_github_id=student.github_id
                        ).aggregate(total_commits=Sum('contributed_commit_count'))['total_commits'] or 0
                        
                        # 합산한 값을 course_dict에 추가
                        course_dict[course_id]['commit'] += total_commit_count
                        
                        # PR 수 합산
                        course_dict[course_id]['pr'] += ( repo.contributed_open_pr_count or 0) +  (repo.contributed_closed_pr_count or 0)
                        
                        # Issue 수 합산
                        course_dict[course_id]['issue'] += (repo.contributed_open_issue_count or 0) + (repo.contributed_closed_issue_count or 0)
                        
                        # Repo 수 합산
                        course_dict[course_id]['repo'] += 1
                        
                        # Star 수 합산
                        course_dict[course_id]['star'] += Repository.objects.get(id=repo.id).star_count or 0

                    else:  # 특정 학생의 repo가 과목과 관련 없는 경우
                        etc_total_commit += repo.contributed_commit_count or 0 
                        etc_total_pr +=  ( repo.contributed_open_pr_count or 0) +  (repo.contributed_closed_pr_count or 0)
                        etc_total_issue += (repo.contributed_open_issue_count or 0) + (repo.contributed_closed_issue_count or 0)
                        etc_total_repo += 1
                        etc_total_star += Repository.objects.get(id=repo.id).star_count or 0

                # 학생별 total_contributes와 is_contributor 계산
                total_contributions_data = Repo_contributor.objects.filter(
                    contributor_id=student.github_id
                ).exclude(
                    owner_github_id=student.github_id
                ).aggregate(
                    total_contributes=Sum('contribution_count')
                )
                total_contributes = total_contributions_data.get('total_contributes') or 0
                is_contributor = 1 if total_contributes >= 1 else 0

                # 각 과목에 대한 정보 추가
                for course_id, course_count in course_dict.items():
                    course = Course.objects.get(course_id=course_id)

                    course_info = {
                        "id": student.id,
                        "github_id": student.github_id,
                        "name": student.name,
                        "department": student.department,
                        "enrollment": student.enrollment,
                        "year": course.year,
                        "semester": course.semester,
                        "course_name": course.name,
                        "commit": course_count['commit'],
                        "pr": course_count['pr'],
                        "issue": course_count['issue'],
                        "num_repos": course_count['repo'],
                        "star_count": course_count['star'],
                        "prof": course.prof,
                        "course_id": course.course_id,
                        "total_contributes": total_contributes,
                        "is_contributor": is_contributor
                    }
                    total_commit += course_count['commit']
                    total_pr += course_count['pr']
                    total_issue += course_count['issue']
                    total_repo += course_count['repo']
                    total_star += course_count['star']

                    data.append(course_info)

                # 기타 정보 추가
                etc_info = {
                    "id": student.id,
                    "github_id": student.github_id,
                    "name": student.name,
                    "department": student.department,
                    "enrollment": student.enrollment,
                    "year": "",
                    "semester": "",
                    "course_name": "기타",
                    "commit": etc_total_commit,
                    "pr": etc_total_pr,
                    "issue": etc_total_issue,
                    "num_repos": etc_total_repo,
                    "star_count": etc_total_star,
                    "prof": "",
                    "course_id": "",
                    "total_contributes": total_contributes,
                    "is_contributor": is_contributor
                }

                total_commit += etc_total_commit
                total_pr += etc_total_pr
                total_issue += etc_total_issue
                total_repo += etc_total_repo
                total_star += etc_total_star

                data.append(etc_info)               

            except Exception as e:
                print(f'Error processing student {student.name}: {e}')
                continue       

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Student's info --------------#
def student_read_total(request):
    try:
        data = []
        students = Student.objects.all()
        for student in students:
            try:
                print(f'student is:{student.name}')
                # 특정 하나의 학생에 대해 진행             
                total_commit = 0 
                total_pr = 0
                total_issue = 0
                total_repo = 0

                etc_total_commit = 0 
                etc_total_pr = 0
                etc_total_issue = 0
                etc_total_repo = 0

                # 특정 학생의 모든 레포지토리 가져옴
                student_repos = Repository.objects.filter(owner_github_id=student.github_id)

                # 특정 학생의 수강 목록들 가져옴
                course_reg_list = Course_registration.objects.filter(student=student)

                # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
                courses_repos = Course_project.objects.filter(repo__in=student_repos)
                
                # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
                course_ids = []
                for course_reg in course_reg_list:
                    course_ids.append(course_reg.course.course_id)

                # 딕셔너리 초기화
                course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}
                courses_project_repos = []

                for c in courses_repos:
                    courses_project_repos.append(c.repo)

                # 각 repo에 대한 정보 추가
                for repo in student_repos:
                    if repo in courses_project_repos:  # 특정 학생의 현재 가리키는 repo가 과목과 관련이 있는 경우
                        specific_course = Course_project.objects.get(repo=repo)
                        course_id = specific_course.course.course_id
                        
                        # Commit 수 합산
                        total_commit_count = Repository.objects.filter(
                            id = specific_course.repo.id,
                            owner_github_id=student.github_id
                        ).aggregate(total_commits=Sum('contributed_commit_count'))['total_commits'] or 0

                        # 합산한 값을 course_dict에 추가
                        course_dict[course_id]['commit'] += total_commit_count
                        # PR 수 합산
                        course_dict[course_id]['pr'] += ( repo.contributed_open_pr_count or 0) +  (repo.contributed_closed_pr_count or 0)
                        
                        # Issue 수 합산
                        course_dict[course_id]['issue'] += (repo.contributed_open_issue_count or 0) + (repo.contributed_closed_issue_count or 0)
                        # Repo 수 합산
                        course_dict[course_id]['repo'] += 1

                    else:  # 특정 학생의 repo가 과목과 관련 없는 경우
                        etc_total_commit += repo.contributed_commit_count or 0 
                        etc_total_pr +=  ( repo.contributed_open_pr_count or 0) +  (repo.contributed_closed_pr_count or 0)
                        etc_total_issue += (repo.contributed_open_issue_count or 0) + (repo.contributed_closed_issue_count or 0)
                        etc_total_repo += 1
                


                # 각 과목에 대한 정보 추가
                for course_id, course_count in course_dict.items():
                    total_commit += course_count['commit']
                    total_pr += course_count['pr']
                    total_issue += course_count['issue']
                    total_repo += course_count['repo']            
                    
                total_commit += etc_total_commit
                total_pr += etc_total_pr
                total_issue += etc_total_issue
                total_repo += etc_total_repo
                        
                total_info = {
                    "id": student.id,
                    "github_id": student.github_id,
                    "name": student.name,
                    "department": student.department,
                    "enrollment": student.enrollment,
                    "year": "",
                    "semester": "",
                    "course_name": "",
                    "total_commit": total_commit,
                    "total_pr": total_pr,
                    "total_issue": total_issue,
                    "total_repos": total_repo
                }
                data.append(total_info)

            except Exception as e:
                if student.name == '홍종현':
                    print(f'Error processing student {student.name}: {e}')
                continue
            
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ETC --------------#
def student_course_year_search(request):
    try:
        data = []
        student_id = request.GET.get('student_id')
        year = request.GET.get('year')
        student = Student.objects.get(id=student_id)

        
        # 특정 학생의 모든 레포지토리 가져옴
        student_repos = Repository.objects.filter(owner_github_id=student.github_id)
        
        # 특정 학생의 과목 관련된 레포지토리들을 가져옴
        courses_repos = Course_project.objects.filter(repo__in=student_repos)
        
        # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
        course_ids = []
        for course_project in courses_repos:
            course_id = course_project.course.course_id
            if course_id not in course_ids:
                course_ids.append(course_id)

        # 딕셔너리 초기화
        course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}
        etc_dict = {year: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0}}

        courses_project_repos = [c.repo for c in courses_repos]
        
        print(courses_project_repos)

        # 각 repo에 대한 정보 추가
        for repo in student_repos:
            repo_created_year = str(datetime.strptime(repo.created_at, '%Y-%m-%dT%H:%M:%SZ').year)  # 연도 추출
            if repo_created_year == year:
                
                if repo in courses_project_repos:  # 특정 학생의 repo가 과목과 관련이 있는 경우
                    specific_course = Course_project.objects.get(repo=repo)
                    course_id = specific_course.course.course_id
                
                    # Commit 수 합산
                    course_dict[course_id]['commit'] += repo.commit_count
                    
                    # PR 수 합산
                    course_dict[course_id]['pr'] += Repo_pr.objects.filter(repo_id=repo.id).count()
                    
                    # Issue 수 합산
                    course_dict[course_id]['issue'] += Repo_issue.objects.filter(repo_id=repo.id).count()
                    
                    # Repo 수 합산
                    course_dict[course_id]['repo'] += 1
                else:  # 특정 학생의 repo가 과목과 관련 없는 경우
                    etc_dict[repo_created_year]['commit'] += repo.commit_count
                    etc_dict[repo_created_year]['pr'] += Repo_pr.objects.filter(repo_id=repo.id).count()
                    etc_dict[repo_created_year]['issue'] += Repo_issue.objects.filter(repo_id=repo.id).count()
                    etc_dict[repo_created_year]['repo'] += 1

            else: 
                continue 
        # 각 과목에 대한 정보 추가
        
        for course_id, course_count in course_dict.items():
                course = Course.objects.get(course_id=course_id)
                if str(course.year) == year :
 
                    course_info = {
                        "id": student.id,
                        "github_id": student.github_id,
                        "name": student.name,
                        "department": student.department,
                        "enrollment": student.enrollment,
                        "year": course.year,
                        "semester": course.semester,
                        "course_name": course.name,
                        "commit": course_count['commit'],
                        "pr": course_count['pr'],
                        "issue": course_count['issue'],
                        "num_repos": course_count['repo']
                    }

                    data.append(course_info)
        
        for the_year, the_year_count in etc_dict.items():
            etc_info = {
                "id": student.id,
                "github_id": student.github_id,
                "name": student.name,
                "department": student.department,
                "enrollment": student.enrollment,
                "year": the_year,
                "semester": "",
                "course_name": the_year + " 기타",
                "commit": the_year_count['commit'],
                "pr": the_year_count['pr'],
                "issue": the_year_count['issue'],
                "num_repos": the_year_count['repo']
            }

            data.append(etc_info)               
                    
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ETC --------------#
def student_num_read_course_info(request):
    try:
        student_num = int(request.GET.get('num'))  # Fetch the 'num' parameter and convert it to an integer
        data = []
        students = Student.objects.all()[:student_num]
        for student in students:
     
            # 특정 하나의 학생에 대해 진행             
            total_commit =0 
            total_pr =0
            total_issue =0
            total_repo =0

            etc_total_commit =0 
            etc_total_pr =0
            etc_total_issue =0
            etc_total_repo =0

            # 특정 학생의 모든 레포지토리 가져옴
            student_repos= Repository.objects.filter(owner_github_id=student.github_id)
            
            # 특정 학생의 수강 목록들 가져옴
            course_reg_list = Course_registration.objects.filter(student=student)

            # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
            courses_repos = Course_project.objects.filter(repo__in=student_repos)
            
            # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
            course_ids=[]
            for course_reg in course_reg_list :
                course_ids.append(course_reg.course.course_id)

            # 딕셔너리 초기화
            course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}


            courses_project_repos = []

            for c in courses_repos:
                courses_project_repos.append(c.repo)

            # 각 repo에 대한 정보 추가
            for repo in student_repos:

                if repo in courses_project_repos: # 특정 학생의 현재 가리키는 repo가 과목과 관련이 있는 경우
                    specific_course = Course_project.objects.get(repo=repo)
                    course_id = specific_course.course.course_id
                    
                    # Commit 수 합산
                    course_dict[course_id]['commit'] += repo.commit_count
                    
                    # PR 수 합산
                    course_dict[course_id]['pr'] += Repo_pr.objects.filter(repo_id=repo.id).count()
                    
                    # Issue 수 합산
                    course_dict[course_id]['issue'] += Repo_issue.objects.filter(repo_id=repo.id).count()
                    
                    # Repo 수 합산
                    course_dict[course_id]['repo'] += 1


                else: # 특정 학생의 repo가 과목과 관련 없는 경우
                    etc_total_commit += repo.commit_count
                    etc_total_pr += Repo_pr.objects.filter(repo_id=repo.id).count()
                    etc_total_issue += Repo_issue.objects.filter(repo_id=repo.id).count()
                    etc_total_repo += 1


            # 각 과목에 대한 정보 추가

            for course_id, course_count in course_dict.items():
                
                course = Course.objects.get(course_id=course_id)

                course_info = {
                    "id": student.id,
                    "github_id": student.github_id,
                    "name":student.name,
                    "department": student.department,
                    "enrollment": student.enrollment,
                    "year": course.year,
                    "semester": course.semester,
                    "course_name": course.name,
                    "commit": course_count['commit'],
                    "pr": course_count['pr'],
                    "issue": course_count['issue'],
                    "num_repos": course_count['repo']
                }
                total_commit += course_count['commit']
                total_pr += course_count['pr']
                total_issue += course_count['issue']
                total_repo += course_count['repo']

                data.append(course_info)
            
                    

            etc_info = {
                "id": student.id,
                "github_id": student.github_id,
                "name": student.name,
                "department": student.department,
                "enrollment": student.enrollment,
                "year": "",
                "semester": "",
                "course_name": "기타",
                "commit": etc_total_commit,
                "pr": etc_total_pr,
                "issue": etc_total_issue,
                "num_repos": etc_total_repo
                }
                
            total_commit += etc_total_commit
            total_pr += etc_total_pr
            total_issue += etc_total_issue
            total_repo += etc_total_repo
            
            data.append(etc_info)               
                        
        return JsonResponse(data , safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------ETC --------------#
def student_num_read_total(request):
    try:
        student_num = int(request.GET.get('num'))  # Fetch the 'num' parameter and convert it to an integer
        data = []
        students = Student.objects.all()[:student_num]
        for student in students:
     
            # 특정 하나의 학생에 대해 진행             
            total_commit =0 
            total_pr =0
            total_issue =0
            total_repo =0

            etc_total_commit =0 
            etc_total_pr =0
            etc_total_issue =0
            etc_total_repo =0

            # 특정 학생의 모든 레포지토리 가져옴
            student_repos= Repository.objects.filter(owner_github_id=student.github_id)
            
            # 특정 학생의 수강 목록들 가져옴
            course_reg_list = Course_registration.objects.filter(student=student)

            # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
            courses_repos = Course_project.objects.filter(repo__in=student_repos)
            
            # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
            course_ids=[]
            for course_reg in course_reg_list :
                course_ids.append(course_reg.course.course_id)

            # 딕셔너리 초기화
            course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}

            courses_project_repos = []

            for c in courses_repos:
                courses_project_repos.append(c.repo)

            # 각 repo에 대한 정보 추가
            for repo in student_repos:

                if repo in courses_project_repos: # 특정 학생의 현재 가리키는 repo가 과목과 관련이 있는 경우
                    specific_course = Course_project.objects.get(repo=repo)
                    course_id = specific_course.course.course_id
                    
                    # Commit 수 합산
                    course_dict[course_id]['commit'] += repo.commit_count
                    
                    # PR 수 합산
                    course_dict[course_id]['pr'] += Repo_pr.objects.filter(repo_id=repo.id).count()
                    
                    # Issue 수 합산
                    course_dict[course_id]['issue'] += Repo_issue.objects.filter(repo_id=repo.id).count()
                    
                    # Repo 수 합산
                    course_dict[course_id]['repo'] += 1


                else: # 특정 학생의 repo가 과목과 관련 없는 경우
                    etc_total_commit += repo.commit_count
                    etc_total_pr += Repo_pr.objects.filter(repo_id=repo.id).count()
                    etc_total_issue += Repo_issue.objects.filter(repo_id=repo.id).count()
                    etc_total_repo += 1


            # 각 과목에 대한 정보 추가

            for course_id, course_count in course_dict.items():
                
                total_commit += course_count['commit']
                total_pr += course_count['pr']
                total_issue += course_count['issue']
                total_repo += course_count['repo']            
                    
                
            total_commit += etc_total_commit
            total_pr += etc_total_pr
            total_issue += etc_total_issue
            total_repo += etc_total_repo
                        
            
            total_info = {
                "id": student.id,
                "github_id": student.github_id,
                "name": student.name,
                "department": student.department,
                "enrollment": student.enrollment,
                "year": "",
                "semester": "",
                "course_name": "",
                "total_commit": total_commit,
                "total_pr": total_pr,
                "total_issue": total_issue,
                "total_repos": total_repo
            }
            data.append(total_info)
            
        return JsonResponse(data , safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Korea UNI OPEN-API TOEKN --------------#
def get_kuopenapi_access_token():
    
    token_url = "https://kuapi.korea.ac.kr/svc/modules/token"
    client_id = settings.KOREAUNIV_OPENAPI_CLIENT_ID  # 여기에 실제 client_id 입력
    client_secret = settings.KOREAUNIV_OPENAPI_CLIENT_SECRET  # 여기에 실제 client_secret 입력

    token_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    # 토큰 요청
    token_response = requests.get(token_url, params=token_params)
    token_data = token_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return JsonResponse({'error': 'Token registration failed', 'details': token_data}, status=400)

    print(f'your access token is {access_token}')
    return access_token    
# ---------------------------------------------

# ------------Student validation--------------#
def student_validation(request):
    try:
        access_token = get_kuopenapi_access_token()
        
        student_count = 0 
        data =[]
        student_ids = Student.objects.all().values_list('id', flat=True)
        student_total_count = Student.objects.all().count()
        for student_id in student_ids:
            #API 요청
            api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate"  # 실제 API 엔드포인트로 변경
            headers = {
                'AUTH_KEY': access_token
            }
            
            # 요청 파라미터 설정
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                'std_id' : student_id
            }
            
            # API 호출
            response = requests.get(api_url, headers=headers, params=params)

            # JSON 응답을 파싱
            response_data = response.json()
            
            # Check if the "result" key is an empty list
            if response_data.get("result") == []:
                
                #졸업생 쿼리 api 호출
                
                grad_api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate-gra"  # 실제 API 엔드포인트로 변경

                headers = {
                'AUTH_KEY': access_token
            }
                params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                'std_id' : student_id
            }
                            # API 호출
                response = requests.get(grad_api_url, headers=headers, params=params)
                
                 # JSON 응답을 파싱
                response_data = response.json()
                
                if response_data.get("result") == []:
                    print(f'Empty result for student ID: {student_id}')
                
                else :    
                    result_items = response_data.get("result", [])
                    result_item = result_items[0]
                    # result_list가 빈 리스트가 아닐 경우
                    std_id = result_item.get("STD_ID")
                    rec_sts_nm = result_item.get("REC_STS_NM")
                    kor_nm = result_item.get("KOR_NM")
                    col_nm = result_item.get("COL_NM")
                    dept_nm = result_item.get("DEPT_NM")
                    smajor_nm = result_item.get("SMAJOR_NM")          
                    email_addr = result_item.get("EMAIL_ADDR")     

                    # data 리스트에 새로운 딕셔너리 추가
                    data.append({
                        "STD_ID": std_id,
                        "REC_STS_NM": rec_sts_nm,
                        "KOR_NM": kor_nm,
                        "COL_NM": col_nm,
                        "DEPT_NM": dept_nm,
                        "SMAJOR_NM":smajor_nm,
                        "email_addr": email_addr
                    })
                    student_count += 1

                    specific_student =  Student.objects.get(id= student_id)
                    specific_student.enrollment = rec_sts_nm 
                    specific_student.name = kor_nm
                    specific_student.college = col_nm
                    specific_student.department = dept_nm 
                    specific_student.double_major = smajor_nm
                    specific_student.primary_email = email_addr
                    specific_student.save()
            
            else:
                # response_data에서 "result" 키의 값을 가져옴
                result_items = response_data.get("result", [])
                result_item = result_items[0]
                # result_list가 빈 리스트가 아닐 경우
                std_id = result_item.get("STD_ID")
                rec_sts_nm = result_item.get("REC_STS_NM")
                kor_nm = result_item.get("KOR_NM")
                col_nm = result_item.get("COL_NM")
                dept_nm = result_item.get("DEPT_NM")
                smajor_nm = result_item.get("SMAJOR_NM")          
                email_addr = result_item.get("EMAIL_ADDR")     

                # data 리스트에 새로운 딕셔너리 추가
                data.append({
                    "STD_ID": std_id,
                    "REC_STS_NM": rec_sts_nm,
                    "KOR_NM": kor_nm,
                    "COL_NM": col_nm,
                    "DEPT_NM": dept_nm,
                    "SMAJOR_NM":smajor_nm,
                    "email_addr": email_addr
                })

                student_count += 1 

                specific_student =  Student.objects.get(id= student_id)
                specific_student.enrollment = rec_sts_nm 
                specific_student.name = kor_nm
                specific_student.college = col_nm
                specific_student.department = dept_nm 
                specific_student.double_major = smajor_nm
                specific_student.primary_email = email_addr
                specific_student.save()

        data.append(f'{student_count} students')
        not_valid_student_count = student_total_count - student_count
        data.append(f'{not_valid_student_count} students are not valid.')
        

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Student validation--------------#
def query_student_openapi(ids,access_token):
    try:
        student_ids = ids  # Fetch the 'num' parameter and convert it to an integer
        data =[]
        empty_list = [] 
        for student_id in student_ids:

            #API 요청
            api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate"  # 실제 API 엔드포인트로 변경
            headers = {
                'AUTH_KEY': access_token
            }
            
            # 요청 파라미터 설정
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                'std_id' : student_id
            }
            
            # API 호출
            response = requests.get(api_url, headers=headers, params=params)

            # JSON 응답을 파싱
            response_data = response.json()
            
            # Check if the "result" key is an empty list
            if response_data.get("result") == []:
                #졸업생 쿼리 api 호출
                
                grad_api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate-gra"  # 실제 API 엔드포인트로 변경

                headers = {
                'AUTH_KEY': access_token
            }
                params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                'std_id' : student_id
            }
                            # API 호출
                response = requests.get(grad_api_url, headers=headers, params=params)
                
                 # JSON 응답을 파싱
                response_data = response.json()
                
                if response_data.get("result") == []:
                    empty_list.append(student_id)

                else :    
                    result_items = response_data.get("result", [])
                    result_item = result_items[0]
                    # result_list가 빈 리스트가 아닐 경우
                    std_id = result_item.get("STD_ID")
                    rec_sts_nm = result_item.get("REC_STS_NM")
                    kor_nm = result_item.get("KOR_NM")
                    col_nm = result_item.get("COL_NM")
                    dept_nm = result_item.get("DEPT_NM")
                    smajor_nm = result_item.get("SMAJOR_NM")          
                    email_addr = result_item.get("EMAIL_ADDR")     

                    # data 리스트에 새로운 딕셔너리 추가
                    data.append({
                        "STD_ID": std_id,
                        "REC_STS_NM": rec_sts_nm,
                        "KOR_NM": kor_nm,
                        "COL_NM": col_nm,
                        "DEPT_NM": dept_nm,
                        "SMAJOR_NM":smajor_nm,
                        "email_addr": email_addr
                    })
                
            else:
                # response_data에서 "result" 키의 값을 가져옴
                result_items = response_data.get("result", [])
                result_item = result_items[0]
                # result_list가 빈 리스트가 아닐 경우
                std_id = result_item.get("STD_ID")
                rec_sts_nm = result_item.get("REC_STS_NM")
                kor_nm = result_item.get("KOR_NM")
                col_nm = result_item.get("COL_NM")
                dept_nm = result_item.get("DEPT_NM")
                smajor_nm = result_item.get("SMAJOR_NM")          
                email_addr = result_item.get("EMAIL_ADDR")     

                # data 리스트에 새로운 딕셔너리 추가
                data.append({
                    "STD_ID": std_id,
                    "REC_STS_NM": rec_sts_nm,
                    "KOR_NM": kor_nm,
                    "COL_NM": col_nm,
                    "DEPT_NM": dept_nm,
                    "SMAJOR_NM":smajor_nm,
                    "email_addr": email_addr
                })
            
        return data, empty_list

    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Student validation--------------#
def query_per_get_student_openapi(request):
    try:
        student_id = request.GET.get('id')
        access_token = get_kuopenapi_access_token()
        
        data =[]
        #API 요청
        api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate-gra"  # 실제 API 엔드포인트로 변경
        headers = {
            'AUTH_KEY': access_token
        }
        
        # 요청 파라미터 설정
        params = {
            'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
            'std_id' : student_id
        }
        
        # API 호출
        response = requests.get(api_url, headers=headers, params=params)

        # JSON 응답을 파싱
        response_data = response.json()
        
        # Check if the "result" key is an empty list
        if response_data.get("result") == []:
            print(f'Empty result for student ID: {student_id}')
        
        else:
            # response_data에서 "result" 키의 값을 가져옴
            result_items = response_data.get("result", [])
            result_item = result_items[0]
            # result_list가 빈 리스트가 아닐 경우
            std_id = result_item.get("STD_ID")
            rec_sts_nm = result_item.get("REC_STS_NM")
            kor_nm = result_item.get("KOR_NM")
            col_nm = result_item.get("COL_NM")
            dept_nm = result_item.get("DEPT_NM")
            smajor_nm = result_item.get("SMAJOR_NM")          
            email_addr = result_item.get("EMAIL_ADDR")     

            # data 리스트에 새로운 딕셔너리 추가
            data.append({
                "STD_ID": std_id,
                "REC_STS_NM": rec_sts_nm,
                "KOR_NM": kor_nm,
                "COL_NM": col_nm,
                "DEPT_NM": dept_nm,
                "SMAJOR_NM":smajor_nm,
                "email_addr": email_addr
            })

            
        return JsonResponse(data , safe = False)

    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------Invalid github_id--------------# 
def none_githubid_list(request):
    # github_id가 빈 문자열이거나 None인 학생의 id와 enrollment 가져오기
    empty_github_ids = Student.objects.filter(
        Q(github_id__isnull=True) | Q(github_id__exact='')
    ).values('id', 'enrollment')  # id와 enrollment 필드 가져오기

    # 데이터를 리스트로 변환
    data = list(empty_github_ids)

    # JsonResponse 반환
    return JsonResponse(data, safe=False)
# ---------------------------------------------

# ------------Invalid github_id for attending students--------------# 
def none_githubid_list_only_attending(request):
    # github_id가 빈 문자열이거나 None이고 enrollment가 '재학'인 학생의 객체 가져오기
    students_empty_github_ids = Student.objects.filter(
        (Q(github_id__isnull=True) | Q(github_id__exact='')) & Q(enrollment='재학')
    )

    data = []

    for empty_student in students_empty_github_ids:
        temp_data = []
        # 해당 학생이 수강한 과목 정보 가져오기
        courses_taken = Course_registration.objects.filter(student=empty_student)
        
        # courses_taken을 리스트로 변환하여 추가
        for per_course_taken in courses_taken:
            course_id = per_course_taken.course.course_id
            course_name = per_course_taken.course.name
            temp_data.append([course_id,course_name])

        # 학생 정보 추가
        temp_data.append(empty_student.id)
        temp_data.append(empty_student.name)
        temp_data.append(empty_student.department)
        temp_data.append(empty_student.enrollment)

        data.append(list(temp_data))

    # JsonResponse 반환
    return JsonResponse(data, safe=False)
# ---------------------------------------------

# ------------student's contributions--------------# 
def count_contributors_per_student(request):
    try:
        # 모든 Repo_contributor 데이터를 가져오고 이후 파이썬 코드에서 필터링
        all_contributors = (
            Repo_contributor.objects
            .values('contributor_id', 'owner_github_id')  # 필터링에 필요한 필드만 선택
            .annotate(
                total_contributions=Sum('contribution_count')  # contribution_count 합계 계산
            )
        )

        # owner_github_id와 contributor_id가 다른 데이터만 남기기
        filtered_data = [
            entry for entry in all_contributors
            if entry['owner_github_id'] != entry['contributor_id']
        ]

        # 학생 데이터를 저장할 딕셔너리 초기화
        student_data = {}

        for entry in filtered_data:
            try:
                # contributor_id로 Student 테이블에서 해당하는 학생을 찾기
                student = Student.objects.get(github_id=entry['contributor_id'])
                student_id = student.id

                # 이미 student_id가 존재하면 기존 값에 누적, 없으면 새로 추가
                if student_id in student_data:
                    student_data[student_id]['total_contributions'] += entry['total_contributions']
                else:
                    # 새로운 student_id인 경우 초기 데이터 설정
                    student_data[student_id] = {
                        'student_id': student_id,
                        'student_name': student.name,
                        'total_contributions': entry['total_contributions']
                    }

            except Student.DoesNotExist:
                # 해당 contributor_id에 해당하는 학생이 없으면 무시
                continue

        # commit_exist 필드 추가
        for student_id, info in student_data.items():
            info['commit_exist'] = info['total_contributions'] > 0  # total_contributions가 0보다 크면 True, 아니면 False

        # 결과를 리스트로 변환
        data = list(student_data.values())

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------

# ------------foreign student validation--------------# 
def update_foreign_students(request):
    try:
       
        students = Student.objects.all()  # 모든 학생을 조회
        
        for student in students:
            # id 필드에서 'KU'가 포함된 경우
            if 'KU' in student.id:
                student.department = '학점교류'
                student.college = '학점교류'
                student.enrollment = '해당없음'
            
            # id의 5번째 자리가 '9'인 경우
            elif len(student.id) == 10 and student.id[4] == '9':
                student.department = '교환학생'
                student.college = '교환학생'
                student.enrollment = '해당없음'

            # 변경 사항을 저장
            student.save()
        return JsonResponse('foreign_students updated!' , safe=False) 
    
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
# ---------------------------------------------

# ========================================
# Test Function
# ========================================
# ------------Test--------------#
def sync_student_db_test(request, student_id):
    try:
        #get student information form DB
        student = Student.objects.get(id=student_id)
        github_id = student.github_id
        print(f"Processing Student: {student_id} - Github ID: {github_id})")

       
            
        # Fetch GitHub user data
        response = requests.get(f"http://{settings.PUBLIC_IP}:{settings.FASTAPI_PORT}/api/user", params={'github_id': github_id})
        if response.status_code == 404:
                message = f"[ERROR] GitHub user {github_id} not found"
                print(message)
                failure_count += 1
                exit()

        data = response.json()
            
        try:
            print(f"Received data for GitHub ID {github_id}: {data}")
            # Update or create student record
            student_record, created = Student.objects.update_or_create(
                github_id__iexact=github_id,
                defaults={
                    'follower_count': data.get('Follower_CNT'),
                    'following_count': data.get('Following_CNT'),
                    'public_repo_count': data.get('Public_repos_CNT'),
                    'github_profile_create_at': data.get('Github_profile_Create_Date'),
                    'github_profile_update_at': data.get('Github_profile_Update_Date')
                }
            )

            action = "Created" if created else "Updated"
            message = f"Student record {action}: ID {student_id}, GitHub ID {github_id}"
            print(f"[SUCCESS] {message}")


        except Exception as e:
            message = f"[ERROR] Error processing student: ID {id}, GitHub ID {github_id} - {str(e)}"
            print(message)
            failure_count += 1
        print(f'-'*5)

        return JsonResponse({
            "status": "OK", 
            "message": "Student records processed successfully", 
        })
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
# ---------------------------------------------
