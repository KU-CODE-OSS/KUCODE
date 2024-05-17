from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

 # DB CRUD for repo
    path("repo_create_db", views.repo_create_db, name="repo_create_db"),
    path("repo_read_db", views.repo_read_db, name="repo_read_db"),
    path("repo_update_db", views.repo_update_db, name="repo_update_db"),
    path("repo_delete_db", views.repo_delete_db, name="repo_delete_db"),

]
