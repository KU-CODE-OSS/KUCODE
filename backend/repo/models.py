from django.db import models

# Create your models here.
class Repository(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=500,null=True)
    url = models.CharField(max_length=500,null=True)
    owner_github_id = models.CharField(max_length=100,null=True)
    created_at = models.CharField(max_length=100,null=True)
    updated_at = models.CharField(max_length=100,null=True)
    forked = models.BooleanField(null=True)
    fork_count = models.IntegerField(null=True)
    star_count = models.IntegerField(null=True)
    commit_count = models.IntegerField(null=True)
    open_issue_count = models.IntegerField(null=True)
    closed_issue_count = models.IntegerField(null=True)
    open_pr_count = models.IntegerField(null=True)
    closed_pr_count = models.IntegerField(null=True)
    owner_commit_count = models.IntegerField(null=True)
    owner_open_issue_count = models.IntegerField(null=True)
    owner_closed_issue_count = models.IntegerField(null=True)
    owner_open_pr_count = models.IntegerField(null=True)
    closed_pr_count = models.IntegerField(null=True)
    language = models.CharField(max_length=500,null=True)
    contributors = models.CharField(max_length=5000,null=True)
    license = models.CharField(max_length=500,null=True)
    has_readme = models.BooleanField(null=True)
    description = models.CharField(max_length=1000,null=True)
    release_version = models.CharField(max_length=100,null=True)
    etc = models.CharField(max_length=100,null=True)
    crawled_date = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name

class Repo_contributor(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')  # Repository 고유 ID, ForeignKey
    repo_url = models.CharField(max_length=255, null=True)  # Repository URL
    owner_github_id = models.CharField(max_length=255, null=True)  # Repository 소유자 Github ID
    contributor_id = models.CharField(max_length=255, null=True)  # Repository 기여자 Github ID
    contribution_count = models.IntegerField(null=True)  # Repository 기여한 횟수

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['repo_id', 'contributor_id'], name='unique_repo_contributor')
        ]

    def __str__(self):
        return self.repo_id

class Repo_issue(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # Issue 고유 ID
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')  # Repository 고유 ID, ForeignKey
    repo_url = models.CharField(max_length=255,null=True)  # Repository URL
    owner_github_id = models.CharField(max_length=255,null=True)  # Repository 소유자 Github ID
    state = models.CharField(max_length=255,null=True)  # Issue 상태 (Open or Closed)
    title = models.CharField(max_length=255,null=True)  # Issue 이름
    publisher_github_id = models.CharField(max_length=255,null=True)  # Issue 발행자 Github ID
    last_update = models.CharField(max_length=255,null=True)  # Issue 마지막 업데이트 일자

    def __str__(self):
        return self.repo_id

class Repo_pr(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # PR 고유 ID
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')  # Repository ID, ForeignKey
    repo_url = models.CharField(max_length=255,null=True)  # Repository URL
    owner_github_id = models.CharField(max_length=255)  # Repository 소유자 Github ID
    title = models.CharField(max_length=255,null=True)  # pull request 이름
    requester_id = models.CharField(max_length=255,null=True)  # pull request 발행자 Github ID
    published_date = models.CharField(max_length=255,null=True)  # pull request 발행 일자
    state = models.CharField(max_length=255)  # 상태 (Open / Closed)
    last_update = models.CharField(max_length=255,null=True)  # PR 마지막 업데이트 일자

    def __str__(self):
        return self.title
    

class Repo_commit(models.Model):
    sha = models.CharField(max_length=255)  # commit 고유 ID (SHA)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')  # Repository 고유 ID, ForeignKey
    repo_url = models.CharField(max_length=255)  # Repository URL
    owner_github_id = models.CharField(max_length=255)  # Repository 소유자 Github ID
    committer_github_id = models.CharField(max_length=255,null=True)  # 커밋 발행자 Github ID
    added_lines = models.IntegerField()  # 추가된 줄
    deleted_lines = models.IntegerField()  # 제거된 줄
    last_update = models.CharField(max_length=255,null=True)  # Commit 마지막 업데이트 일자

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sha','repo'], name='unique_repo_commit')
        ]

    def __str__(self):
        return self.id