from django.db import models

# Create your models here.
# New user table
class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    PROFESSOR = 'PROFESSOR', 'Professor'
    STUDENT = 'STUDENT', 'Student'

class Status(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    LOCKED = 'LOCKED', 'Locked'
    PENDING = 'PENDING', 'Pending'

class Member(models.Model):
    id = models.UUIDField(primary_key=True)
    role = models.CharField(
        max_length=9,
        choices=Role.choices,
        default=Role.STUDENT  # 기본값을 STUDENT로 설정
    )
    name = models.CharField(max_length=30)
    email = models.EmailField()
    # hashed_pw = models.CharField(max_length=255)

    def __str__(self):
        return self.id

class Student(models.Model):
    # FK connected with user table
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        null=True
    )
    id = models.CharField(max_length=50, primary_key=True)
    github_auth = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.LOCKED  # 기본값을 LOCKED으로 설정
    )

    def __str__(self):
        return self.id
    
class Professor(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        null=True
    )
    id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.id