from django.urls import path
from . import views

urlpatterns = [
  path("healthcheck", views.HealthCheckAPIView.as_view(), name="healthcheck"),
  path("ping", views.ping, name="ping"),
  path("drive_config", views.get_drive_config, name="drive_config"),
  path("read_posts_list", views.read_posts_list, name="read_posts_list"),
  path("read_post", views.read_post, name="read_post"),
  path("read_company_repos_list", views.read_company_repos_list, name="read_company_repos_list"),
  path("read_trending_repos_list", views.read_trending_repos_list, name="read_trending_repos_list"),
  path("update_post", views.update_post, name="update_post"),
  path("upload_file_to_drive", views.upload_file_to_drive, name="upload_file_to_drive"),
  path("link_drive_file", views.link_drive_file, name="link_drive_file"),
  path("update_company_repo", views.update_company_repo, name="update_company_repo"),
  path("update_trending_repo", views.update_trending_repo, name="update_trending_repo"),
  path("toggle_post_like", views.toggle_post_like, name="toggle_post_like"),
]


