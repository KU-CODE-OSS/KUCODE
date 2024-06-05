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

import requests


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
            
            response = requests.get(f"{settings.PUBLIC_IP_FASTAPI}"+"/user", params={'github_id': github_id})
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
        count = 0 
        for student in students:
            per_student_data =[]
            courses_taken = Course_registration.objects.filter(student=student)
            total_commit = 0
            total_pr = 0
            total_issue = 0
            total_repo = 0
            
            for index, specific_course in enumerate(courses_taken):
                year = specific_course.course_year
                semester = specific_course.course_semester
                name = specific_course.course.name
                
                # Find the user's repo for the specific course.
                course_repos = Course_project.objects.filter(course=specific_course.course, course_year=year,
                                                            course_semester=semester).values_list('repo', flat=True)
                specific_course_repos = Repository.objects.filter(id__in=course_repos, owner_github_id=student.github_id)
                
                if not specific_course_repos:
                    break

                # Calculate the user's total_commit for the specific course.
                commit = Repo_commit.objects.filter(repo__in=specific_course_repos).count()
                total_commit += commit

                # Calculate the user's total_pr for the specific course.
                pr = Repo_pr.objects.filter(repo__in=specific_course_repos, owner_github_id=student.github_id).count()
                total_pr += pr

                # Calculate the user's total_issue for the specific course.
                issue = Repo_issue.objects.filter(repo__in=specific_course_repos,
                                                owner_github_id=student.github_id).count()
                total_issue += issue

                # Calculate the user's #num_repos for the specific course.
                num_repos = specific_course_repos.count()
                total_repo += num_repos

                specific_info = {
                    "id": student.id,
                    "github_id": student.github_id,
                    "name": student.name,
                    "department": student.department,
                    "enrollment": student.enrollment,
                    "year": year,
                    "semester": semester,
                    "course_name": name,
                    "commit": commit,
                    "pr": pr,
                    "issue": issue,
                    "num_repos": num_repos
                }
                per_student_data.append(specific_info)
    
                if index == len(courses_taken) - 1:
                    summary_info = {
                        "total_commit": total_commit,
                        "total_pr": total_pr,
                        "total_issue": total_issue,
                        "total_repo": total_repo
                    }
                    per_student_data.insert(0,summary_info) 
            
            if per_student_data == []:
                continue                
            data.append(per_student_data)


             
        
        print(count)
        return JsonResponse(data, safe=False)


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
            response = requests.get(f"{settings.PUBLIC_IP_FASTAPI}/user", params={'github_id': github_id})
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
    
        