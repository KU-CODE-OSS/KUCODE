from django.db import models
from account.models import Student
from repo.models import Repository
# Create your models here.

class Course(models.Model):
    course_id = models.CharField(max_length=20)
    year = models.IntegerField()
    semester = models.IntegerField()
    name = models.CharField(max_length=100)
    prof = models.CharField(max_length=100)
    ta = models.CharField(max_length=100, blank=True, null=True)
    student_count = models.IntegerField(default=0)  # 기본값으로 0 설정
    course_repo_name = models.CharField(max_length=100, null =True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'year', 'semester'], name='unique_course')
        ]


class Course_registration(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_year=models.IntegerField(null=True)
    course_semester=models.IntegerField(null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null = True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'course_year', 'course_semester','student'], name='unique_course_registration')
        ]


    def __str__(self):
        return self.name

class Course_project(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_year=models.IntegerField(null=True)
    course_semester=models.IntegerField(null=True)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, null= True)
    repo_name = models.CharField(max_length=100,null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course','course_year', 'course_semester','repo','repo_name'], name='unique_course_project')
        ]

    def __str__(self):
        return self.name