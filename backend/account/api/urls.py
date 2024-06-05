from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # account_students CRUD
    path("sync_student_db", views.sync_student_db, name="sync_student_db"),
    path("student_read_db", views.student_read_db, name="student_read_db"),
    # path("student_update_db", views.student_update_db, name="student_update_db"),
    path("student_delete_db", views.student_delete_db, name="student_delete_db"),

    # test
    path("sync_student_db_test", views.sync_student_db_test, name="sync_student_db_test"),
]   