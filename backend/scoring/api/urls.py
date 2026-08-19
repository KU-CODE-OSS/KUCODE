from django.urls import path

from scoring.api import views


urlpatterns = [
    path("course-ranking", views.course_ranking, name="scoring-course-ranking"),
]
