from django.urls import path

from scoring.api import views


urlpatterns = [
    path("course-ranking", views.course_ranking, name="scoring-course-ranking"),
    path("student-aptitude", views.student_aptitude, name="scoring-student-aptitude"),
]
