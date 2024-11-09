from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from account.models import User,Student,Administration
from course.models import Course, Course_registration, Course_project
from repo.models import Repo_commit, Repo_pr ,Repo_issue, Repository,Repo_contributor
import requests
from account.api.views import get_kuopenapi_access_token,query_student_openapi

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def course_create_db (request):
    try:
        course_id=request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')
        name = request.GET.get('name')
        prof = request.GET.get('prof')
        ta = request.GET.get('ta')
        student_count = request.GET.get('student_count')

        if not course_id or not year or not semester:
            raise ValueError("course_id and year and semester cannot be empty")
        
        if Course.objects.filter(course_id=course_id, year=year,semester=semester).exists():
            raise ValueError("course already exists.")
        
        course = Course.objects.create(
            course_id=course_id,
            year=year,
            semester=semester,
            name=name,
            prof=prof,
            ta=ta,
            student_count=student_count
        )

        return JsonResponse({"status": "OK", "message": "course record created successfully"})
    
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)     

def course_read_db(request):
    try:
        data = []
        courses = Course.objects.all()

        for course in courses:
            
            total_commits = 0
            total_prs = 0
            total_issues = 0
            total_stars =0 
            # Calculate the total commits
            total_course_repos = Repository.objects.filter(url__contains=course.course_repo_name)
            
            for course_repo in total_course_repos :
                if course_repo.forked is True :
                    continue            
                else :
                    total_commits += course_repo.commit_count or 0 
                    total_issues += (course_repo.open_issue_count or 0) + (course_repo.closed_issue_count or 0)
                    total_prs += (course_repo.open_pr_count or 0) + (course_repo.closed_pr_count or 0)
                    total_stars += course_repo.star_count or 0 


            # Calculate the average commits 

            student_count = Course_registration.objects.filter(
                course=course,
                course_year=course.year,
                course_semester=course.semester
            ).count()
            
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
            ).values('repo_id')

            contributor_count = Repo_contributor.objects.filter(
            repo_id__in=repo_ids
            ).values('contributor_id').count()

        
            # Gather all the data 
            data.append( {
                "course_id":course.course_id,
                "year": course.year,
                "semester": course.semester,
                "name": course.name,
                "prof": course.prof,
                "ta": course.ta,
                "student_count": course.student_count,
                "total_commits": total_commits ,
                "total_issues": total_issues,
                "total_prs": total_prs,
                "total_stars": total_stars,
                "avg_commits": avg_commits,
                "repository_count": repository_count,
                "contributor_count": contributor_count
            })
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



def course_registration_create_db(request):
    
    try:
        course_id = request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')  
        student_ids = Student.objects.values_list('id', flat=True)
        course = Course.objects.get(course_id=course_id, year=year, semester=semester)
        
        count =0 

        for student_id in student_ids:
            student = Student.objects.get(id=student_id)    
            count+=1
            # 이미 해당 수업에 등록된 학생이 있는지 확인
            if Course_registration.objects.filter(course=course, student=student).exists():
                print(f"{student} already registered for {course.name}")
                continue
            
            course_reg = Course_registration.objects.create(
                course=course,  
                course_year=course.year,
                course_semester=course.semester,
                student=student
            )
            print(f"OK! {student} has been registered for {course.name}")
            
        print(f"The num of students:{count}")
        course.student_count = count
        course.save()
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
    
    
def course_read_db_specific(request):
    try:
        course_id=request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')    
        course = Course.objects.get(course_id=course_id, year=year, semester=semester)

        # Calculate the total commits
        total_commits = Repo_commit.objects.filter(repo_url__contains=course.course_repo_name).count()
        


        # Calculate the average commits 

        student_count = Course_registration.objects.filter(
            course=course,
            course_year=year,
            course_semester=semester
        ).count()
        
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
        ).values('repo_id')

        contributor_count = Repo_contributor.objects.filter(
        repo_id__in=repo_ids
        ).values('contributor_id').count()

        


        # Gather all the data 
        data = {
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
        return JsonResponse(data)
           
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    



def course_year_search(request):
    try:
        data = []
        year = request.GET.get('year')
        students = Student.objects.all()
        
        for student in students:
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
    

def course_department_count(request):
    try:
        data = []
        # 해당 년도의 모든 과목 코드들 가져옴
        
        # 간단하게 생각스.. 
        distinct_course_ids = Course.objects.all()
        print(distinct_course_ids)
        # Initialize the dictionary to store department counts

        for specific_course_id in distinct_course_ids:
            
            department_count = {}
            
            specific_course_reg = Course_registration.objects.filter(course = specific_course_id)

            for specific_course_per_reg in specific_course_reg : 
                student = Student.objects.get(id = specific_course_per_reg.student.id)
                
                # Get the department of the student
                department_name = student.department
                
                # Check if the department already exists in the dictionary
                if department_name in department_count:
                    # If it exists, increment the count
                    department_count[department_name] += 1
                else:
                    # If it doesn't exist, add it with a count of 1
                    department_count[department_name] = 1
            
            # You can now return this dictionary as part of the response, or process it further
            data.append({'year': specific_course_id.year,'semester': specific_course_id.semester ,'course_id': specific_course_id.course_id,'course_name': specific_course_id.name, 'department_count': department_count , "total_count": specific_course_id.student_count})
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

                

def course_validation(request):
    try:
        access_token = get_kuopenapi_access_token()
        courses = Course.objects.all()
        data = []
        for specific_course in courses:
            course_id, course_class = specific_course.course_id.split('-')
            
            #API 요청
            api_url = "https://kuapi.korea.ac.kr/svc/lecture/class/class-information"  # 실제 API 엔드포인트로 변경
            headers = {
                'AUTH_KEY': access_token
            }
            
            # 요청 파라미터 설정
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                "year":str(specific_course.year),
                'term':str(specific_course.semester)+'R',
                'course_code': course_id,
                'course_class': course_class
            }
            
            # API 호출
            response = requests.get(api_url, headers=headers, params=params)
            # JSON 응답을 파싱
            
            response_data = response.json()
            
            result_items = response_data.get("result", [])
            result_item = result_items[0]
            course_name = result_item.get("COURSE_NAME")

            specific_course.name = course_name 
            specific_course.save()

            # 과목 학생 수 count validation 
            specific_course_count = Course_registration.objects.filter(course = specific_course).count()
            specific_course.student_count = specific_course_count
            specific_course.save()

            data.append(response_data)
        
        return JsonResponse(data , safe=False) 

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def course_reg_validation(request):
    try:
        access_token = get_kuopenapi_access_token()
        courses = Course.objects.all()
        data = []
        for specific_course in courses:
            course_id, course_class = specific_course.course_id.split('-')
            
            #API 요청
            api_url = "https://kuapi.korea.ac.kr/svc/course/course-registration/by-class"  # 실제 API 엔드포인트로 변경
            headers = {
                'AUTH_KEY': access_token
            }
            
            # 요청 파라미터 설정
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                "year":str(specific_course.year),
                'term':str(specific_course.semester)+'R',
                'course_code': course_id,
                'course_class': course_class
            }
            
            # API 호출
            response = requests.get(api_url, headers=headers, params=params)
            # JSON 응답을 파싱
            
            response_data = response.json()
            
            result_items = response_data.get("result", [])
            
            new_ids = []

            for result_item in result_items:

                student_reg_id = result_item.get("student_id")
                
                try:
                    # Student 객체를 조회
                    reg_student = Student.objects.get(id=student_reg_id)
                    
                    try:
                        # Course_registration 객체가 존재하는지 확인
                        Course_registration.objects.get(student=reg_student, course = specific_course)
                        # 존재하면 pass
                        pass
                    
                    except Course_registration.DoesNotExist:
                        # Course_registration 객체가 존재하지 않으면 student_reg_id를 추가
                        Course_registration.objects.create(course = specific_course, course_year = specific_course.year , course_semester = specific_course.semester , student = reg_student)
                
                except Student.DoesNotExist:
                    # Student 객체가 존재하지 않으면 student_reg_id를 추가
                    new_ids.append(student_reg_id)

            
            #새로운 (미등록)학생들에 대해서 학생DB에 추가
            new_student_data,empty_ids = query_student_openapi(new_ids,access_token)
            print([specific_course.name,new_student_data,"empty",empty_ids])
            new_count = 0 

            for item in new_student_data :
                try :
                    id = item.get("STD_ID")
                    enrollment = item.get("REC_STS_NM")
                    name = item.get("KOR_NM")
                    college = item.get("COL_NM")
                    department = item.get("DEPT_NM")
                    double_major = item.get("SMAJOR_NM")
                    email_addr = item.get("email_addr")

                    new_reg_student, created = Student.objects.get_or_create(
                        id=id,                   
                        enrollment =enrollment,
                        name = name,
                        college = college,
                        department = department,
                        double_major = double_major,
                        primary_email = email_addr
                        
                    )
                    if not created:
                        print(f'Student with ID {id} already exists!')                    
                    
                    # Course_registration 객체 생성 또는 가져오기
                    new_course_reg, created = Course_registration.objects.get_or_create(
                        course=specific_course,
                        course_year=specific_course.year,
                        course_semester=specific_course.semester,
                        student=new_reg_student )
                    
                    if created:
                                print(f'Student {id}, {name} registered for {specific_course.name}')
                                new_count += 1
                    else:
                        print(f'Student {id}, {name} already registered for {specific_course.name}')

                except Exception as e:
                    print(f'Error processing student with ID {id}: {e}')
                    continue

            data.append(f'{specific_course.name}: new student created: {new_count} , empty student: {empty_ids}')

        return JsonResponse(data , safe=False) 

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



def course_reg_look(request):
    try:
        access_token = get_kuopenapi_access_token()
        courses = Course.objects.all()
        data = []
        for specific_course in courses:
            course_id, course_class = specific_course.course_id.split('-')
            
            #API 요청
            api_url = "https://kuapi.korea.ac.kr/svc/course/course-registration/by-class"  # 실제 API 엔드포인트로 변경
            headers = {
                'AUTH_KEY': access_token
            }
            
            # 요청 파라미터 설정
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                "year":str(specific_course.year),
                'term':str(specific_course.semester)+'R',
                'course_code': course_id,
                'course_class': course_class
            }
            
            # API 호출
            response = requests.get(api_url, headers=headers, params=params)
            # JSON 응답을 파싱
            
            response_data = response.json()

            data.append(response_data)

        return JsonResponse(data , safe=False) 

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    

