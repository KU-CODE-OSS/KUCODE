from django.db import models

# Create your models here.

class PostCategory(models.TextChoices):
    """게시글 분류"""
    INTERNAL = 'INTERNAL', '교내'
    EXTERNAL = 'EXTERNAL', '교외'
    LEARNING_MATERIAL = 'LEARNING_MATERIAL', '학습 자료'
    OPENSOURCE_REPO = 'OPENSOURCE_REPO', '오픈소스 Repos'
    EVENT_INFO = 'EVENT_INFO', '행사 정보'

class Post(models.Model):
    """게시글 및 학습 자료"""
    # id는 Django가 자동으로 생성 (BigAutoField)
    author = models.CharField(max_length=100, null=False)  # 작성자 닉네임
    title = models.CharField(max_length=255, null=False)
    # 서식이 포함된 글을 저장하기 위해 TextField 사용 (HTML, 마크다운 등 저장 가능)
    content = models.TextField(null=False)
    category = models.CharField(
        max_length=50,
        choices=PostCategory.choices,
        null=False
    )
    is_internal = models.BooleanField(null=False, default=True)
    year = models.IntegerField(null=False)  # YEAR 타입은 IntegerField로 표현
    semester = models.CharField(max_length=10, null=False)
    event_info = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'board_post'
        ordering = ['-created_at']  # 최신순 정렬

    def __str__(self):
        return self.title


class FileDisplayType(models.TextChoices):
    """파일 표시 방식"""
    DOWNLOAD = 'DOWNLOAD', 'Download'
    WEB_VIEWER = 'WEB_VIEWER', 'Web Viewer'


class File(models.Model):
    """첨부 파일"""
    # id는 Django가 자동으로 생성
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_column='post_id',
        related_name='files'
    )
    file_name = models.CharField(max_length=255, null=False)
    storage_link = models.CharField(max_length=2048, null=False)  # 구글 드라이브 링크
    file_extension = models.CharField(max_length=10, null=False)
    display_type = models.CharField(
        max_length=20,
        choices=FileDisplayType.choices,
        null=False
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'board_file'

    def __str__(self):
        return self.file_name


class CompanyRepo(models.Model):
    """기업 레포지토리 정보"""
    # id는 Django가 자동으로 생성
    repo_name = models.CharField(max_length=2048, null=False)
    github_url = models.CharField(max_length=2048, null=False)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    repo_count = models.IntegerField(default=1)
    last_updated_date = models.DateField(null=False)

    class Meta:
        db_table = 'board_company_repo'

    def __str__(self):
        return self.repo_name


class TrendingRepo(models.Model):
    """트렌딩 레포지토리 정보"""
    # id는 Django가 자동으로 생성
    repo_name = models.CharField(max_length=2048, null=False)
    github_url = models.CharField(max_length=2048, null=False)
    trending_rank = models.IntegerField(null=False)
    developer_github_url = models.CharField(max_length=2048, null=False)
    last_updated_date = models.DateField(null=False)

    class Meta:
        db_table = 'board_trending_repo'
        ordering = ['trending_rank']  # 랭킹 순으로 정렬

    def __str__(self):
        return self.repo_name
