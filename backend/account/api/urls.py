from django.urls import path
<<<<<<< HEAD
=======
from .import views
>>>>>>> e80889aa93fa1e2571004a53d18083cb267d2514

from account.api.views import HealthCheckAPIView

urlpatterns = [
<<<<<<< HEAD
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck")
]
=======
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # account_students CRUD
    path("sync_student_db", views.sync_student_db, name="sync_student_db"),
    # path("student_update_db", views.student_update_db, name="student_update_db"),
    path("student_delete_db", views.student_delete_db, name="student_delete_db"),

    # test
    path("sync_student_db_test", views.sync_student_db_test, name="sync_student_db_test"),
    path("student_excel_import", views.student_excel_import, name="student_excel_import"),

    # read for ALL students 
    path("student_read_course_info", views.student_read_course_info, name="student_read_course_info"),
    path("student_read_total", views.student_read_total, name="student_read_total"),

    # read for ONE SPECIFIC student
    path("student_course_year_search",views.student_course_year_search,name="student_course_year_search"),

    # read for num Students
    path("student_num_read_course_info", views.student_num_read_course_info, name="student_num_read_course_info"),
    path("student_num_read_total", views.student_num_read_total, name="student_num_read_total"),

    # get ku openapi's access token 
    path("get_kuopenapi_access_token", views.get_kuopenapi_access_token, name="get_kuopenapi_access_token"),

    # Student validation 
    path("student_validation", views.student_validation, name="student_validation"),

    # Per Student lookup
    path("query_per_get_student_openapi",views.query_per_get_student_openapi, name ="query_per_get_student_openapi"),

    # Students without githubids.
    path("none_githubid_list",views.none_githubid_list, name ="none_githubid_list"),

    # Students without githubids but only for attending students
    path("none_githubid_list_only_attending",views.none_githubid_list_only_attending, name ="none_githubid_list_only_attending")


]   
>>>>>>> e80889aa93fa1e2571004a53d18083cb267d2514
