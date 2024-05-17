from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 권한을 설정하는 ENUM 클래스
    github_id = models.CharField(max_length=255,default='null')


class Student(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    github_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    double_major = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    primary_email = models.EmailField()
    secondary_email = models.EmailField()
    enrollment = models.CharField(max_length=100)
    follower_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    public_repo_count = models.IntegerField(null=True)
    starred_count = models.IntegerField(null=True)
    github_profile_create_at = models.CharField(max_length=100, null=True)
    github_profile_update_at = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.name


