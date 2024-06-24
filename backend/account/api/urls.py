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
    path("student_excel_import", views.student_excel_import, name="student_excel_import"),

    # specific read for students 
    path("student_read_course_info", views.student_read_course_info, name="student_read_course_info"),
    path("student_read_total", views.student_read_total, name="student_read_total"),

    #practice
    path("practice_course_info",views.practice_course_info,name="practice_course_info"),
    path("student_course_year_search",views.student_course_year_search,name="student_course_year_search")
]   