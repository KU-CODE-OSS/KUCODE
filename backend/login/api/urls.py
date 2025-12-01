from django.urls import path
from .import views

from account.api.views import HealthCheckAPIView

urlpatterns = [
    path("healthcheck", HealthCheckAPIView.as_view(), name="healthcheck"),

    #student_login
    path("github_login", views.github_login, name="github_login"),
    path("callback", views.callback, name="callback"),

    #admin_login
    path("admin_login", views.admin_login, name="admin_login"),
    
    #signup
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),

]