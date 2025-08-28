from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 권한을 설정하는 ENUM 클래스
    pass

    github_id = models.CharField(max_length=255,default='null')
    name = models.CharField(max_length=255,default='null')

    
class Student(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    github_id = models.CharField(max_length=50,null = True)
    department = models.CharField(max_length=100,null=True)
    double_major = models.CharField(max_length=100,null=True)
    college = models.CharField(max_length=100,null=True)
    primary_email = models.EmailField(null=True)
    secondary_email = models.EmailField(null=True)
    enrollment = models.CharField(max_length=100,null=True)
    follower_count = models.IntegerField(null=True)
    following_count = models.IntegerField(null=True)
    public_repo_count = models.IntegerField(null=True)
    starred_count = models.IntegerField(null=True)
    github_profile_create_at = models.CharField(max_length=100, null=True)
    github_profile_update_at = models.CharField(max_length=100, null=True)
    total_language_percentage = models.JSONField(null=True)  # 전체 언어 비율

    def __str__(self):
        return self.name
    
class Administration(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100,null=True)
    double_major = models.CharField(max_length=100,null=True)
    college = models.CharField(max_length=100,null=True)
    primary_email = models.EmailField(null=True)
    secondary_email = models.EmailField(null=True)
    enrollment = models.CharField(max_length=100,null=True)
    is_super = models.BooleanField(default=False)  # 기본값 False로 설정

    def __str__(self):
        return self.name
