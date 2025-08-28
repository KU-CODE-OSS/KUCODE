from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
  path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # repo_repository CRUD
  path("sync_repo_db", views.sync_repo_db, name="sync_repo_db"),
  path("repo_read_db", views.repo_read_db, name="repo_read_db"),
  path("repo_course_read_db", views.repo_course_read_db, name="repo_course_read_db"),
  path("sync_repo_category", views.sync_repo_category, name="sync_repo_category"),

# repo_contributor CRUD
  path("sync_repo_contributor_db", views.sync_repo_contributor_db, name="sync_repo_contributor_db"),
  path("repo_contributor_read_db", views.repo_contributor_read_db, name="repo_contributor_read_db"),

# repo_repo_issue CRUD
  path("sync_repo_issue_db",views.sync_repo_issue_db, name="sync_repo_issue_db"),
  path("repo_issue_read_db", views.repo_issue_read_db, name="repo_issue_read_db"),

 # repo_repo_pr CRUD    
  path("sync_repo_pr_db",views.sync_repo_pr_db, name="sync_repo_pr_db"),
  path("repo_pr_read_db", views.repo_pr_read_db, name="repo_pr_read_db"),

 # repo_repo_commit CRUD
  path("sync_repo_commit_db",views.sync_repo_commit_db, name="sync_repo_commit_db"),
  path("repo_commit_read_db", views.repo_commit_read_db, name="repo_commit_read_db"),

  # test
  path('sync_repo_db_test/<int:student_id>/', views.sync_repo_db_test, name='sync_repo_db_test'),
  path('sync_repo_contributor_db_test/<int:student_id>/', views.sync_repo_contributor_db_test, name='sync_repo_contributor_db_test'),
  path('sync_repo_issue_db_test/<int:student_id>/', views.sync_repo_issue_db_test, name='sync_repo_issue_db_test'),
  path('sync_repo_pr_db_test/<int:student_id>/', views.sync_repo_pr_db_test, name='sync_repo_pr_db_test'),
  path('sync_repo_commit_db_test/<int:student_id>/', views.sync_repo_commit_db_test, name='sync_repo_commit_db_test'),
  
# read_db_per_request
  path('repo_account_read_db', views.repo_account_read_db, name='repo_account_read_db')
  ]
