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


 # Course Year별 search
   path("course_year_search", views.course_year_search, name="course_year_search"),

 # Course department별 search (year별로)
   path("course_department_count", views.course_department_count, name = "course_department_count"),

 # Course validation 
   path("course_validation", views.course_validation, name = "course_validation"),
   path("course_reg_validation", views.course_reg_validation, name = "course_reg_validation"),
   path("course_reg_look", views.course_reg_look, name ="course_reg_look"),
 
 # Courses with min,max,avg
   path("course_read_min_max_avg", views.course_read_min_max_avg, name="course_read_min_max_avg"),

]
