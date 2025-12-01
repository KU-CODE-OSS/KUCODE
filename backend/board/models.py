from django.db import models
from login.models import Member

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
    # author를 Member 모델과 연결 (작성자)
    # null=True를 설정하여 익명(비로그인) 또는 회원 탈퇴 시에도 데이터가 남도록 함

    # author = models.ForeignKey(
    #     Member,
    #     on_delete=models.SET_NULL,  # 작성자가 삭제되면 NULL로 설정
    #     related_name='posts',
    #     null=True,
    #     blank=True  # 폼 검증 시 필수 입력 아님
    # )

    author = models.CharField(max_length=100, null=False, default='Anonymous')
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
    
    # 좋아요 기능을 위한 ManyToManyField (중복 방지 및 누가 눌렀는지 기록)
    likes = models.ManyToManyField(
        Member,
        related_name='liked_posts',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'board_post'
        ordering = ['-created_at']  # 최신순 정렬

    def __str__(self):
        return self.title
    
    # 좋아요 수를 반환하는 프로퍼티 추가
    @property
    def like_count(self):
        return self.likes.count()


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


class Comment(models.Model):
    """게시글 댓글"""
    # id는 Django가 자동으로 생성
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    # 작성자를 Member 모델과 연결
    author = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,  # 작성자가 삭제되면 NULL로 설정
        related_name='comments',
        null=True,
        blank=True
    )
    content = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    
    # 대댓글(답글) 기능을 위한 자기 참조 (Self-referencing)
    # parent가 지정되면 해당 댓글의 대댓글로 간주
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        db_table = 'board_comment'
        ordering = ['created_at']  # 작성순 정렬

    def __str__(self):
        # Member 모델의 name을 사용, author가 없으면 'Anonymous' 표시
        author_name = self.author.name if self.author else 'Anonymous'
        return f'{author_name} - {self.content[:20]}'
