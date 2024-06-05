from django.urls import path
from . import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # DB CRUD for course
    path("course_create_db", views.course_create_db, name="course_create_db"),
    path("course_read_db", views.course_read_db, name="course_read_db"),
    path("course_update_db", views.course_update_db, name="course_update_db"),
    path("course_delete_db", views.course_delete_db, name="course_delete_db"),

 # DB CRUD for course_registration

    path("course_registration_create_db", views.course_registration_create_db, name="course_registration_create_db"),
    path("course_project_update", views.course_project_update, name="course_project_update"),
]
