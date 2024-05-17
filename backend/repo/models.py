from django.db import models

# Create your models here.
class Repository(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    owner_github_id = models.CharField(max_length=50)
    created_at = models.CharField(max_length=100)
    updated_at = models.CharField(max_length=100)
    fork_count = models.IntegerField(null=True)
    star_count = models.IntegerField(null=True)
    commit_count = models.IntegerField(null=True)
    open_issue_count = models.IntegerField(null=True)
    closed_issue_count = models.IntegerField(null=True)
    languate = models.CharField(max_length=100,null=True)
    contributor = models.CharField(max_length=100,null=True)
    license = models.CharField(max_length=100,null=True)
    has_readme = models.BooleanField()
    description = models.CharField(max_length=100,null=True)
    release_version = models.CharField(max_length=100,null=True)
    etc = models.CharField(max_length=100,null=True)
    crawled_date = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name