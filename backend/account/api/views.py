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
from repo.models import Repo_commit, Repo_pr ,Repo_issue, Repository
from django.db.models import Sum
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

#---------- CU ----------#
def sync_student_db(request):
    try:
        students = Student.objects.all()
        
        student_list = [{'id': student.id, 'github_id': student.github_id} for student in students]
        
        total_student_count = len(student_list)
        student_count = 0
        
        success_count = 0
        failure_count = 0
        failure_details = []

        for student in student_list:
            student_count += 1
            print(f'({student_count}/{total_student_count}) Processing student with id {student["id"]} and github_id {student["github_id"]}')
            id = student['id']
            github_id = student['github_id']
            
            response = requests.get(f"http://{settings.PUBLIC_IP}:5000/api/user", params={'github_id': github_id})
            if response.status_code == 404:
                message = f"GitHub user {github_id} not found"
                print(message)
                failure_count += 1
                failure_details.append({"id": id, "github_id": github_id, "message": message})
                continue
            
            data = response.json()
            
            try:                    
                student_record = Student.objects.get(github_id__iexact=github_id)
                student_record.follower_count = data.get('Follower_CNT')
                student_record.following_count = data.get('Following_CNT')
                student_record.public_repo_count = data.get('Public_repos_CNT')
                student_record.starred_count = 0
                student_record.github_profile_create_at = data.get('Github_profile_Create_Date')
                student_record.github_profile_update_at = data.get('Github_profile_Update_Date')
                student_record.save()
                message = f"Student record with id {id} and github_id {github_id} updated successfully"
                print(message)
                success_count += 1

            except ObjectDoesNotExist:
                Student.objects.create(
                    id=id,
                    github_id=github_id,
                    follower_count=data.get('Follower_CNT'),
                    following_count=data.get('Following_CNT'),
                    public_repo_count=data.get('Public_repos_CNT'),
                    starred_count=0,
                    github_profile_create_at=data.get('Github_profile_Create_Date'),
                    github_profile_update_at=data.get('Github_profile_Update_Date')
                )

                message = f"Student record with id {id} and github_id {github_id} created successfully"
                print(message)

            except Exception as e:
                message = f"Error processing student with id {id} and github_id {github_id}: {str(e)}"
                print(message)
                failure_count += 1
                failure_details.append({"id": id, "github_id": github_id, "message": message})


            print(f'({student_count}/{total_student_count}) Successfully processed student with id {id} and github_id {github_id}')

        return JsonResponse({
            "status": "OK", 
            "message": "Student records processed successfully", 
            "success_count": success_count,
            "failure_count": failure_count,
            "failure_details": failure_details
        })
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


#---------- READ ----------#
def student_read_db(request):
    try:
        data = []
        students = Student.objects.all()
        for student in students:
            # 특정 하나의 학생에 대해 진행 
            per_student_data =[]
            
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
            


            # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
            courses_repos = Course_project.objects.filter(repo__in=student_repos)
            
            # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
            course_ids=[]
            for course_project in courses_repos:
                course_id = course_project.course.course_id
                if course_id not in course_ids:
                    course_ids.append(course_id)

            # 딕셔너리 초기화
            course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}

            courses_project_repos = []

            for c in courses_repos:
                courses_project_repos.append(c.repo)

            # 각 repo에 대한 정보 추가
            for repo in student_repos:


                if repo in courses_project_repos: # 특정 학생의 repo가 과목과 관련이 있는 경우
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
                    "github_id": "",
                    "name":"",
                    "department": "",
                    "enrollment": "",
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

                per_student_data.append(course_info)
                
            etc_info = {
                "id": student.id,
                "github_id": "",
                "name": "",
                "department": "",
                "enrollment": "",
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
            
            per_student_data.append(etc_info)               
            
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
            per_student_data.insert(0, total_info)
            
            
            data.append(per_student_data)

        return JsonResponse(data , safe=False)


    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


# ---------- DELETE ----------#
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


# ---------- TEST ----------#
def sync_student_db_test(request):
    try:
        github_id = request.GET.get('github_id')
        if not Student.objects.get(github_id=github_id):
            return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
        else:
            response = requests.get(f"http://{settings.PUBLIC_IP}:5000/api/user", params={'github_id': github_id})
            if response.status_code == 404:
                message = f"GitHub user {github_id} not found"
                print(message)
            
            data = response.json()
            
            try:
                student_record = Student.objects.get(github_id__iexact=github_id)
                student_record.follower_count = data.get('Follower_CNT')
                student_record.following_count = data.get('Following_CNT')
                student_record.public_repo_count = data.get('Public_repos_CNT')
                student_record.starred_count = 0
                student_record.github_profile_create_at = data.get('Github_profile_Create_Date')
                student_record.github_profile_update_at = data.get('Github_profile_Update_Date')
                student_record.save()
                message = f"Student record with github_id {github_id} updated successfully"
                print(message)
            except ObjectDoesNotExist:
                student_record = Student.objects.create(
                    github_id=github_id,
                    follower_count=data.get('Follower_CNT'),
                    following_count=data.get('Following_CNT'),
                    public_repo_count=data.get('Public_repos_CNT'),
                    starred_count=0,
                    github_profile_create_at=data.get('Github_profile_Create_Date'),
                    github_profile_update_at=data.get('Github_profile_Update_Date')
                )
                message = f"Student record with github_id {github_id} created successfully"
                print(message)
            except Exception as e:
                message = f"Error processing student with id {id} and github_id {github_id}: {str(e)}"
                print(message)

            return JsonResponse({"status": "OK", "message": "Student record processed successfully"})
        
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Student with github_id '{github_id}' does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
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

        course = Course.objects.get_or_create(
            course_id = df.iloc[0, 0],
            year = int(df.iloc[0, 1]),
            semester = int(df.iloc[0,2]),
            name=df.iloc[0,3],
            prof=df.iloc[0,4],
            ta=df.iloc[0,5],
            student_count = df.iloc[0,6],
            course_repo_name = df.iloc[0,7]
        )
        course = Course.objects.get(course_id=course_id,year=year,semester=semester)
                
        for index, row in df.iloc[1:].iterrows():
            # 필수 매개변수에 누락된 값이 있는지 확인
            
            if pd.isnull(row[0]) or pd.isnull(row[1]) or pd.isnull(row[2]):
                print(f"Student with id {row[0]} has missing values")
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
                        

        return JsonResponse({"status": "OK", "message": "Student record has been imported successfully"})
    
    except Exception as e:
        print(str(e))
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)





def student_read_course_info(request):
    try:
        data = []
        students = Student.objects.all()
        for student in students:
            # 특정 하나의 학생에 대해 진행 
            per_student_data =[]
            
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
            
            # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
            courses_repos = Course_project.objects.filter(repo__in=student_repos)
            
            # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
            course_ids=[]
            for course_project in courses_repos:
                course_id = course_project.course.course_id
                if course_id not in course_ids:
                    course_ids.append(course_id)

            # 딕셔너리 초기화
            course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}

            courses_project_repos = []

            for c in courses_repos:
                courses_project_repos.append(c.repo)

            # 각 repo에 대한 정보 추가
            for repo in student_repos:


                if repo in courses_project_repos: # 특정 학생의 repo가 과목과 관련이 있는 경우
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

def student_read_total(request):
    try:
        data = []
        students = Student.objects.all()
        for student in students:
            # 특정 하나의 학생에 대해 진행 
            per_student_data =[]
            
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
            
            # 특정 학생의 과목 관련된 레포지토리들을 가져옴.
            courses_repos = Course_project.objects.filter(repo__in=student_repos)
            
            # 특정 학생이 듣는 모든 course_id 테이블 및 딕셔너리 생성
            course_ids=[]
            for course_project in courses_repos:
                course_id = course_project.course.course_id
                if course_id not in course_ids:
                    course_ids.append(course_id)

            # 딕셔너리 초기화
            course_dict = {course_id: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for course_id in course_ids}

            courses_project_repos = []

            for c in courses_repos:
                courses_project_repos.append(c.repo)

            # 각 repo에 대한 정보 추가
            for repo in student_repos:


                if repo in courses_project_repos: # 특정 학생의 repo가 과목과 관련이 있는 경우
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
                    "github_id": "",
                    "name":"",
                    "department": "",
                    "enrollment": "",
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

                
            etc_info = {
                "id": student.id,
                "github_id": "",
                "name": "",
                "department": "",
                "enrollment": "",
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




def practice_course_info(request):
    try:
        data = []
        year_table = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
        students = Student.objects.all()
        
        for student in students:
            # 특정 하나의 학생에 대해 진행 
            per_student_data = []
            
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
            etc_dict = {year: {'commit': 0, 'pr': 0, 'issue': 0, 'repo': 0} for year in year_table}

            courses_project_repos = [c.repo for c in courses_repos]

            # 각 repo에 대한 정보 추가
            for repo in student_repos:
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
                    repo_created_year = datetime.strptime(repo.created_at, '%Y-%m-%dT%H:%M:%SZ').year  # 연도 추출
                    repo_created_year = str(repo_created_year)
                    etc_dict[repo_created_year]['commit'] += repo.commit_count
                    etc_dict[repo_created_year]['pr'] += Repo_pr.objects.filter(repo_id=repo.id).count()
                    etc_dict[repo_created_year]['issue'] += Repo_issue.objects.filter(repo_id=repo.id).count()
                    etc_dict[repo_created_year]['repo'] += 1

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
                    "num_repos": course_count['repo']
                }
                total_commit += course_count['commit']
                total_pr += course_count['pr']
                total_issue += course_count['issue']
                total_repo += course_count['repo']

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
                etc_total_commit += the_year_count['commit']
                etc_total_pr += the_year_count['pr']
                etc_total_issue += the_year_count['issue']
                etc_total_repo += the_year_count['repo']

                data.append(etc_info)               
                        
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    


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