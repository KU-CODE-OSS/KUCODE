from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from course.models import Course,Course_project,Course_registration
from repo.models import Repository,Repo_contributor,Repo_commit
from account.models import Student
import requests

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def course_create_db(request):
    try:
        if request.method != 'POST':
            raise ValueError("POST 요청만 허용됩니다.")

        course_id = request.POST.get('course_id')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        name = request.POST.get('name')
        prof = request.POST.get('prof')
        ta = request.POST.get('ta')
        student_count = request.POST.get('student_count')

        if not course_id or not year or not semester:
            raise ValueError("course_id, year 및 semester는 비워둘 수 없습니다.")
        
        if Course.objects.filter(course_id=course_id, year=year, semester=semester).exists():
            raise ValueError("해당 강의는 이미 존재합니다.")
        
        course = Course.objects.create(
            course_id=course_id,
            year=year,
            semester=semester,
            name=name,
            prof=prof,
            ta=ta,
            student_count=student_count
        )

        return JsonResponse({"status": "OK", "message": "강의가 성공적으로 생성되었습니다."})
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def course_read_db(request):
    try:
        data =[]
        courses = Course.objects.all()

        for course in courses:

            # Calculate the total commits
            total_commits = Repo_commit.objects.filter(repo_url__contains=course.course_repo_name).count()
            
            # Calculate the average commits 

            student_count = course.student_count
            
            avg_commits = round(total_commits / student_count, 2)
            
            # Calculate the number of repositories 
            
            repository_count = Course_project.objects.filter(
            course=course,
            course_year=course.year,
            course_semester=course.semester
            ).count()
            
            # Calculate the number of contributors 

            repo_ids = Course_project.objects.filter(
                course=course,
                course_year=course.year,
                course_semester=course.semester
            ).values('repo')

            contributor_count = Repo_contributor.objects.filter(
            repo__in=repo_ids
            ).values('contributor_id').count()                       

            
            # Gather all the data 
            course_data = {
                "course_id":course.course_id,
                "year": course.year,
                "semester": course.semester,
                "name": course.name,
                "prof": course.prof,
                "ta": course.ta,
                "student_count": course.student_count,
                "total_commits": total_commits ,
                "avg_commits": avg_commits,
                "repository_count": repository_count,
                "contributor_count": contributor_count
            }
            data.append(course_data)

        return JsonResponse(data,safe=False)
           
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)



def course_update_db(request):
    try:
        return JsonResponse({"status": "OK", "message": "course record update successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)       

def course_delete_db(request):
    try:
        course_id=request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')           
        course = Course.objects.get(course_id=course_id, year=year, semester=semester)
        course.delete()  # 사용자 객체를 삭제합니다.
        return JsonResponse({"status": "OK", "message": "course record deleted successfully"})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "Error", "message": f"Course '{course_id}' does not exist"}, status=404)    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


@csrf_exempt
def course_registration_create_db(request):
    
    try:
        course_id = request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')  
        student_id =request.GET.get('student_id')

        course = Course.objects.get(course_id=course_id, year=year, semester=semester)
        student = Student.objects.get(id=student_id) 

          # 이미 해당 수업에 등록된 학생이 있는지 확인
        if Course_registration.objects.filter(course=course, student=student).exists():
            print(f"{student} already registered for {course.name}")
        
        course_reg = Course_registration.objects.create(
            course=course,  
            course_year=course.year,
            course_semester=course.semester,
            student=student
        )
        print(f"OK! {student} has been registered for {course.name}")
            
        return JsonResponse({"status": "OK", "message": "course_registration record created successfully"})
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


def course_project_update(request):
    try:
        course_id = request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')  

        course = Course.objects.get(course_id=course_id, year=year, semester=semester)

        repos = Repository.objects.filter(name__icontains=course.course_repo_name)

        for repo in repos:
            # 이미 해당 course_id, year, semester, repo_id를 가지는 레코드가 있는지 확인
            if Course_project.objects.filter(course=course, course_year=year, course_semester=semester, repo_id=repo.id).exists():
                print(f"{repo.owner_github_id}'s {repo.name} Course projects already exists!")
                continue
            
            # 존재하지 않는다면 새로운 레코드 생성
            Course_project.objects.create(
                course=course,
                course_year=year,
                course_semester=semester,
                repo_id=repo.id,
                repo_name=repo.name
            )
            print(f"{repo.owner_github_id}'s {repo.name} has been created!")

        
        return JsonResponse({"status": "OK", "message": "course_project record created successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    
