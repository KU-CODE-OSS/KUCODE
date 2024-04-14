from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 권한을 설정하는 ENUM 클래스
    pass