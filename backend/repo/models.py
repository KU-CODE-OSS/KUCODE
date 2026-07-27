from django.db import models

# Create your models here.
class Repository(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=500,null=True)
    url = models.CharField(max_length=500,null=True)
    owner_github_id = models.CharField(max_length=100,null=True)
    default_branch = models.CharField(max_length=255,null=True)
    created_at = models.CharField(max_length=100,null=True)
    updated_at = models.CharField(max_length=100,null=True)
    pushed_at = models.CharField(max_length=100,null=True)
    forked = models.BooleanField(null=True)
    fork_count = models.IntegerField(null=True)
    star_count = models.IntegerField(null=True)
    commit_count = models.IntegerField(null=True)
    open_issue_count = models.IntegerField(null=True)
    closed_issue_count = models.IntegerField(null=True)
    open_pr_count = models.IntegerField(null=True)
    closed_pr_count = models.IntegerField(null=True)
    contributed_commit_count = models.IntegerField(null=True)
    contributed_open_issue_count = models.IntegerField(null=True)
    contributed_closed_issue_count = models.IntegerField(null=True)
    contributed_open_pr_count = models.IntegerField(null=True)
    contributed_closed_pr_count = models.IntegerField(null=True)
    language = models.CharField(max_length=500,null=True)
    language_bytes = models.JSONField(null=True)
    language_percentage = models.JSONField(null=True)
    contributors = models.CharField(max_length=5000,null=True)
    license = models.CharField(max_length=500,null=True)
    has_readme = models.BooleanField(null=True)
    description = models.CharField(max_length=1000,null=True)
    release_version = models.CharField(max_length=100,null=True)
    etc = models.CharField(max_length=100,null=True)
    crawled_date = models.CharField(max_length=100,null=True)
    summary = models.TextField(null=True) 
    is_course = models.BooleanField(null=True)
    category = models.CharField(max_length=50, null=True)
    repo_introduction = models.TextField(blank=True, null=True)

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
    issue_number = models.IntegerField(null=True)  # GitHub issue number
    repo_url = models.CharField(max_length=255,null=True)  # Repository URL
    owner_github_id = models.CharField(max_length=255,null=True)  # Repository 소유자 Github ID
    state = models.CharField(max_length=255,null=True)  # Issue 상태 (Open or Closed)
    title = models.CharField(max_length=255,null=True)  # Issue 이름
    publisher_github_id = models.CharField(max_length=255,null=True)  # Issue 발행자 Github ID
    created_at = models.DateTimeField(null=True)  # Issue 생성 일자
    closed_at = models.DateTimeField(null=True)  # Issue 종료 일자
    last_update = models.CharField(max_length=255,null=True)  # Issue 마지막 업데이트 일자

    def __str__(self):
        return self.repo_id

class Repo_pr(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # PR 고유 ID
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')  # Repository ID, ForeignKey
    pr_number = models.IntegerField(null=True)  # GitHub pull request number
    repo_url = models.CharField(max_length=255,null=True)  # Repository URL
    owner_github_id = models.CharField(max_length=255)  # Repository 소유자 Github ID
    title = models.CharField(max_length=255,null=True)  # pull request 이름
    requester_id = models.CharField(max_length=255,null=True)  # pull request 발행자 Github ID
    created_at = models.DateTimeField(null=True)  # PR 생성 일자
    closed_at = models.DateTimeField(null=True)  # PR 종료 일자
    merged_at = models.DateTimeField(null=True)  # PR merge 일자
    merged_by = models.CharField(max_length=255,null=True)  # PR merge 수행자
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
    author_github_id = models.CharField(max_length=255,null=True)  # 커밋 발행자 Github ID
    added_lines = models.IntegerField()  # 추가된 줄
    deleted_lines = models.IntegerField()  # 제거된 줄
    committed_at = models.DateTimeField(null=True)  # Commit 작성 일자
    last_update = models.CharField(max_length=255,null=True)  # Commit 마지막 업데이트 일자

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sha','repo'], name='unique_repo_commit')
        ]

    def __str__(self):
        return self.id


class RepositorySnapshot(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')
    collected_at = models.DateTimeField()
    default_branch = models.CharField(max_length=255, null=True)
    branch_count = models.IntegerField(null=True)
    language_bytes = models.JSONField(null=True)
    language_percentage = models.JSONField(null=True)
    workflow_yaml_count = models.IntegerField(null=True)
    workflow_yaml_total_size = models.IntegerField(null=True)
    workflow_yaml_paths = models.JSONField(default=list, blank=True)
    has_readme = models.BooleanField(null=True)
    readme_dependency_mentioned = models.BooleanField(null=True)
    dependency_evidence = models.JSONField(null=True)
    dependabot_config_present = models.BooleanField(null=True)

    class Meta:
        db_table = 'repo_repository_snapshot'
        indexes = [
            models.Index(fields=['repo', 'collected_at'], name='repo_reposi_repo_id_4bb457_idx'),
        ]

    def __str__(self):
        return f"{self.repo_id}@{self.collected_at}"


class RepoCommitFileChange(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')
    sha = models.CharField(max_length=255)
    committed_at = models.DateTimeField(null=True)
    path = models.CharField(max_length=1000)
    filename = models.CharField(max_length=255, null=True)
    extension = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=100, null=True)
    additions = models.IntegerField(null=True)
    deletions = models.IntegerField(null=True)
    changes = models.IntegerField(null=True)
    is_workflow_yaml = models.BooleanField(default=False)
    is_test_file = models.BooleanField(default=False)
    is_readme = models.BooleanField(default=False)
    is_dependency_manifest = models.BooleanField(default=False)

    class Meta:
        db_table = 'repo_commit_file_change'
        constraints = [
            models.UniqueConstraint(fields=['repo', 'sha', 'path'], name='unique_repo_commit_file_change')
        ]
        indexes = [
            models.Index(fields=['repo', 'committed_at'], name='repo_commit_repo_id_bf52f4_idx'),
            models.Index(fields=['repo', 'path'], name='repo_commit_repo_id_77b5ec_idx'),
        ]

    def __str__(self):
        return f"{self.sha}:{self.path}"


class RepoReviewComment(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')
    pr_id = models.CharField(max_length=255, null=True)
    pr_number = models.IntegerField(null=True)
    comment_id = models.CharField(max_length=255)
    author_github_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    path = models.CharField(max_length=1000, null=True)
    position = models.IntegerField(null=True)
    comment_type = models.CharField(max_length=50)
    state = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'repo_review_comment'
        constraints = [
            models.UniqueConstraint(fields=['comment_type', 'comment_id'], name='unique_repo_review_comment')
        ]
        indexes = [
            models.Index(fields=['repo', 'pr_number'], name='repo_review_repo_id_fa64c0_idx'),
            models.Index(fields=['repo', 'created_at'], name='repo_review_repo_id_fabf73_idx'),
        ]

    def __str__(self):
        return f"{self.comment_type}:{self.comment_id}"


class RepoDependabotAlert(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, db_column='repo_id')
    github_alert_number = models.IntegerField()
    state = models.CharField(max_length=100, null=True)
    package_name = models.CharField(max_length=500, null=True)
    ecosystem = models.CharField(max_length=255, null=True)
    manifest_path = models.CharField(max_length=1000, null=True)
    severity = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(null=True)
    fixed_at = models.DateTimeField(null=True)
    dismissed_at = models.DateTimeField(null=True)
    collected_at = models.DateTimeField()

    class Meta:
        db_table = 'repo_dependabot_alert'
        constraints = [
            models.UniqueConstraint(fields=['repo', 'github_alert_number'], name='unique_repo_dependabot_alert')
        ]
        indexes = [
            models.Index(fields=['repo', 'state'], name='repo_depend_repo_id_1abc71_idx'),
            models.Index(fields=['repo', 'severity'], name='repo_depend_repo_id_46050d_idx'),
        ]

    def __str__(self):
        return f"{self.repo_id}#{self.github_alert_number}"
