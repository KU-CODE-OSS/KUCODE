from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # DB CRUD for student
    path("student_create_db", views.student_create_db, name="student_create_db"),
    path("student_read_db", views.student_read_db, name="student_read_db"),
    path("student_update_db", views.student_update_db, name="student_update_db"),
    path("student_delete_db", views.student_delete_db, name="student_delete_db"),

]
