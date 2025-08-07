from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # account_students CRUD
    path("sync_student_db", views.sync_student_db, name="sync_student_db"),
    # path("student_update_db", views.student_update_db, name="student_update_db"),
    path("student_delete_db", views.student_delete_db, name="student_delete_db"),

    # excel
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
    path("none_githubid_list_only_attending",views.none_githubid_list_only_attending, name ="none_githubid_list_only_attending"),

    # Counting num of contributors and contributions per student
    path("count_contributors_per_student",views.count_contributors_per_student, name ="count_contributors_per_student"),

    #update foreign students
    path("update_foreign_students",views.update_foreign_students, name ="update_foreign_students"),

    # test
    path("sync_student_db_test/<int:student_id>/", views.sync_student_db_test, name="sync_student_db_test"),

    # 학생관점 과목 수강 엑셀 리스트
    path("student_course_read_excel", views.student_course_read_excel, name="student_course_read_excel"),

]   
