from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from course.models import Course,Course_registration, Course_project 
import requests

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
        course_id=request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')    
        course = Course.objects.get(course_id=course_id, year=year, semester=semester)

        if course is None:
            return JsonResponse({"status": "Error", "message": "User doesn't exist"})
       
        data = {
            "course_id":course.course_id,
            "year": course.year,
            "semester": course.semester,
            "name": course.name,
            "prof": course.prof,
            "ta": course.ta,
            "student_count": course.student_count
        }
        return JsonResponse(data)
    
    except course.DoesNotExist:
        return JsonResponse({"status": "Error", "message":"course  doesn't exist"}, status=404)
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
    except course.DoesNotExist:
        return False, f"User with username '{course}' does not exist"
    except Exception as e:
        return False, str(e)



def course_registration_create_db (request):
    try:
        course_id=request.GET.get('course_id')
        year = request.GET.get('year')
        semester = request.GET.get('semester')  
        student_id = request.GET.get('student_id')

        course = Course.objects.get(course_id=course_id, year=year, semester=semester)
        
        course_reg = Course_registration.objects.create(
            course_pk=course,  # course_pk 필드에 Course 모델의 인스턴스를 할당
            course_id=course.course_id,
            course_year=course.year,
            course_semester=course.semester,
            student_id=student_id
        )

        return JsonResponse({"status": "OK", "message": "course_registration record created successfully"})
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)