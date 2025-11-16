from django.urls import path
from . import views

urlpatterns = [
  path("healthcheck", views.HealthCheckAPIView.as_view(), name="healthcheck"),
  path("ping", views.ping, name="ping"),
  path("read_posts_list", views.read_posts_list, name="read_posts_list"),
  path("read_post", views.read_post, name="read_post"),
  path("read_company_repos_list", views.read_company_repos_list, name="read_company_repos_list"),
  path("read_trending_repos_list", views.read_trending_repos_list, name="read_trending_repos_list"),
  path("update_post", views.update_post, name="update_post"),
  path("update_file", views.update_file, name="update_file"),
  path("update_company_repo", views.update_company_repo, name="update_company_repo"),
  path("update_trending_repo", views.update_trending_repo, name="update_trending_repo"),
]


