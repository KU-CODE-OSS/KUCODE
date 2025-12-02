from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.conf import settings
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from board.models import Post, File, CompanyRepo, TrendingRepo, Comment
from login.models import Member
from board.services.google_drive import GoogleDriveService, GoogleDriveServiceError


class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def ping(request):
    return JsonResponse({"ok": True, "app": "board"})

def get_drive_config(request):
    """Return Google Drive feature configuration."""
    if request.method != 'GET':
        return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)

    return JsonResponse({
        "status": "OK",
        "enable_drive_upload": settings.ENABLE_BOARD_DRIVE_UPLOAD
    }, status=200)

def read_posts_list(request):
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)

        page_str = request.GET.get('page', '1')
        count_str = request.GET.get('count') or request.GET.get('size') or '10'

        try:
            page = int(page_str)
            count = int(count_str)
        except Exception:
            return JsonResponse({"status": "Error", "message": "page and count must be integers"}, status=400)

        if page < 1 or count < 1:
            return JsonResponse({"status": "Error", "message": "page and count must be >= 1"}, status=400)

        offset = (page - 1) * count
        total = Post.objects.count()

        rows = list(
            Post.objects.all()
            .annotate(like_count=Count('likes'))
            .values('id', 'title', 'author', 'category', 'is_internal', 'year', 'semester', 'created_at', 'like_count')[offset:offset+count]
        )

        # created_at 직렬화 보정
        for r in rows:
            dt = r.get('created_at')
            if dt is not None:
                r['created_at'] = dt.isoformat()

        return JsonResponse({
            "status": "OK",
            "page": page,
            "count": count,
            "total": total,
            "results": rows
        }, status=200)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def read_post(request):
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)

        post_id = request.GET.get('post_id')
        if not post_id:
            return JsonResponse({"status": "Error", "message": "post_id is required"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)

        # Get associated files
        files = post.files.all()
        files_data = []
        for file in files:
            files_data.append({
                "id": file.id,
                "file_name": file.file_name,
                "storage_link": file.storage_link,
                "file_extension": file.file_extension,
                "display_type": file.display_type
            })

        data = {
            "id": post.id,
            "author": post.author,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "is_internal": post.is_internal,
            "year": post.year,
            "semester": post.semester,
            "event_info": post.event_info,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            "files": files_data,
            "like_count": post.like_count  # like_count 추가
        }

        return JsonResponse({
            "status": "OK",
            "post": data
        }, status=200)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def read_company_repos_list(request):
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)

        page_str = request.GET.get('page', '1')
        count_str = request.GET.get('count') or request.GET.get('size') or '10'

        try:
            page = int(page_str)
            count = int(count_str)
        except Exception:
            return JsonResponse({"status": "Error", "message": "page and count must be integers"}, status=400)

        if page < 1 or count < 1:
            return JsonResponse({"status": "Error", "message": "page and count must be >= 1"}, status=400)

        offset = (page - 1) * count
        total = CompanyRepo.objects.count()

        rows = list(
            CompanyRepo.objects.all()
            .values()[offset:offset+count]
        )

        return JsonResponse({
            "status": "OK",
            "page": page,
            "count": count,
            "total": total,
            "results": rows
        }, status=200)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def read_trending_repos_list(request):
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)

        page_str = request.GET.get('page', '1')
        count_str = request.GET.get('count') or request.GET.get('size') or '10'

        try:
            page = int(page_str)
            count = int(count_str)
        except Exception:
            return JsonResponse({"status": "Error", "message": "page and count must be integers"}, status=400)

        if page < 1 or count < 1:
            return JsonResponse({"status": "Error", "message": "page and count must be >= 1"}, status=400)

        offset = (page - 1) * count
        total = TrendingRepo.objects.count()

        rows = list(
            TrendingRepo.objects.all()
            .values()[offset:offset+count]
        )

        return JsonResponse({
            "status": "OK",
            "page": page,
            "count": count,
            "total": total,
            "results": rows
        }, status=200)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def update_post(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        author = body.get('author')
        title = body.get('title')
        content = body.get('content')
        category = body.get('category')
        is_internal = body.get('is_internal', True)
        year = body.get('year')
        semester = body.get('semester')
        event_info = body.get('event_info')

        required_fields = {
            'author': author, 'title': title, 'content': content,
            'category': category, 'year': year, 'semester': semester
        }
        missing = [k for k, v in required_fields.items() if v in [None, ""]]
        if missing:
            return JsonResponse({"status": "Error", "message": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            year_int = int(year)
        except Exception:
            return JsonResponse({"status": "Error", "message": "year must be an integer"}, status=400)

        post = Post.objects.create(
            author=author,
            title=title,
            content=content,
            category=category,
            is_internal=bool(is_internal),
            year=year_int,
            semester=semester,
            event_info=event_info
        )

        return JsonResponse({
            "status": "OK",
            "message": "Post created",
            "post_id": post.id
        }, status=201)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
        
@csrf_exempt
def upload_file_to_drive(request):
    """
    Upload a file to Google Drive and create a File record.
    Requires ENABLE_BOARD_DRIVE_UPLOAD to be True.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)

    # Check if Drive upload is enabled
    if not settings.ENABLE_BOARD_DRIVE_UPLOAD:
        return JsonResponse({
            "status": "Error",
            "message": "Google Drive upload is not enabled"
        }, status=403)

    try:
        # Get post_id from POST data
        post_id = request.POST.get('post_id')
        display_type = request.POST.get('display_type', 'DOWNLOAD')

        if not post_id:
            return JsonResponse({"status": "Error", "message": "post_id is required"}, status=400)

        # Verify post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)

        # Get uploaded file
        if 'file' not in request.FILES:
            return JsonResponse({"status": "Error", "message": "No file provided"}, status=400)

        uploaded_file = request.FILES['file']
        if not uploaded_file.name:
            return JsonResponse({"status": "Error", "message": "File has no name"}, status=400)

        # Upload to Google Drive
        try:
            drive_service = GoogleDriveService()
            drive_result = drive_service.upload_file(
                uploaded_file,
                uploaded_file.name,
                uploaded_file.content_type
            )
        except GoogleDriveServiceError as e:
            return JsonResponse({
                "status": "Error",
                "message": f"Failed to upload to Google Drive: {str(e)}"
            }, status=500)

        # Extract file extension
        file_extension = uploaded_file.name.rsplit('.', 1)[-1] if '.' in uploaded_file.name else ''

        # Create File record in database
        file_obj = File.objects.create(
            post=post,
            file_name=drive_result['name'],
            storage_link=drive_result['web_view_link'],
            file_extension=file_extension,
            display_type=display_type
        )

        return JsonResponse({
            "status": "OK",
            "message": "File uploaded successfully",
            "file": {
                "id": file_obj.id,
                "file_name": file_obj.file_name,
                "storage_link": file_obj.storage_link,
                "file_extension": file_obj.file_extension,
                "display_type": file_obj.display_type,
                "drive_file_id": drive_result['file_id'],
                "file_size": drive_result['size']
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


@csrf_exempt
def link_drive_file(request):
    """
    Link an existing Google Drive file to a post by validating the Drive URL.
    This endpoint is always available regardless of ENABLE_BOARD_DRIVE_UPLOAD setting.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)

    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        post_id = body.get('post_id')
        drive_url = body.get('drive_url')
        file_name = body.get('file_name')
        display_type = body.get('display_type', 'DOWNLOAD')

        # Validate required fields
        if not post_id:
            return JsonResponse({"status": "Error", "message": "post_id is required"}, status=400)
        if not drive_url:
            return JsonResponse({"status": "Error", "message": "drive_url is required"}, status=400)

        # Verify post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)

        # Validate Drive URL
        is_valid, file_id_or_error = GoogleDriveService.validate_drive_link(drive_url)
        if not is_valid:
            return JsonResponse({
                "status": "Error",
                "message": f"Invalid Google Drive URL: {file_id_or_error}"
            }, status=400)

        file_id = file_id_or_error

        # Try to get file metadata (optional, may fail if service not configured)
        file_metadata = None
        try:
            drive_service = GoogleDriveService()
            file_metadata = drive_service.get_file_metadata(file_id)
        except GoogleDriveServiceError:
            # If service is not configured, continue without metadata
            pass

        # Use metadata if available, otherwise use provided name or default
        if file_metadata:
            actual_file_name = file_metadata['name']
            file_extension = actual_file_name.rsplit('.', 1)[-1] if '.' in actual_file_name else ''
        else:
            actual_file_name = file_name or "Linked File"
            file_extension = actual_file_name.rsplit('.', 1)[-1] if '.' in actual_file_name else ''

        # Normalize the Drive URL to view link format
        normalized_url = f"https://drive.google.com/file/d/{file_id}/view"

        # Create File record
        file_obj = File.objects.create(
            post=post,
            file_name=actual_file_name,
            storage_link=normalized_url,
            file_extension=file_extension,
            display_type=display_type
        )

        response_data = {
            "status": "OK",
            "message": "Google Drive file linked successfully",
            "file": {
                "id": file_obj.id,
                "file_name": file_obj.file_name,
                "storage_link": file_obj.storage_link,
                "file_extension": file_obj.file_extension,
                "display_type": file_obj.display_type,
                "drive_file_id": file_id
            }
        }

        if file_metadata:
            response_data['file']['file_size'] = file_metadata.get('size', '0')
            response_data['file']['mime_type'] = file_metadata.get('mime_type', '')

        return JsonResponse(response_data, status=201)

    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def update_company_repo(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        repo_name = body.get('repo_name')
        github_url = body.get('github_url')
        company_name = body.get('company_name')
        repo_count = body.get('repo_count', 1)
        last_updated_date_str = body.get('last_updated_date')

        required_fields = {
            'repo_name': repo_name, 'github_url': github_url,
            'last_updated_date': last_updated_date_str
        }
        missing = [k for k, v in required_fields.items() if v in [None, ""]]
        if missing:
            return JsonResponse({"status": "Error", "message": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            repo_count_int = int(repo_count)
        except Exception:
            return JsonResponse({"status": "Error", "message": "repo_count must be an integer"}, status=400)

        parsed_date = parse_date(last_updated_date_str)
        if not parsed_date:
            return JsonResponse({"status": "Error", "message": "last_updated_date must be YYYY-MM-DD"}, status=400)

        comp_repo = CompanyRepo.objects.create(
            repo_name=repo_name,
            github_url=github_url,
            company_name=company_name,
            repo_count=repo_count_int,
            last_updated_date=parsed_date
        )

        return JsonResponse({
            "status": "OK",
            "message": "CompanyRepo created",
            "company_repo_id": comp_repo.id
        }, status=201)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def update_trending_repo(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        repo_name = body.get('repo_name')
        github_url = body.get('github_url')
        trending_rank = body.get('trending_rank')
        developer_github_url = body.get('developer_github_url')
        last_updated_date_str = body.get('last_updated_date')

        required_fields = {
            'repo_name': repo_name, 'github_url': github_url,
            'trending_rank': trending_rank, 'developer_github_url': developer_github_url,
            'last_updated_date': last_updated_date_str
        }
        missing = [k for k, v in required_fields.items() if v in [None, ""]]
        if missing:
            return JsonResponse({"status": "Error", "message": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            rank_int = int(trending_rank)
        except Exception:
            return JsonResponse({"status": "Error", "message": "trending_rank must be an integer"}, status=400)

        parsed_date = parse_date(last_updated_date_str)
        if not parsed_date:
            return JsonResponse({"status": "Error", "message": "last_updated_date must be YYYY-MM-DD"}, status=400)

        trend_repo = TrendingRepo.objects.create(
            repo_name=repo_name,
            github_url=github_url,
            trending_rank=rank_int,
            developer_github_url=developer_github_url,
            last_updated_date=parsed_date
        )

        return JsonResponse({
            "status": "OK",
            "message": "TrendingRepo created",
            "trending_repo_id": trend_repo.id
        }, status=201)
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def toggle_post_like(request):
    """
    게시글 좋아요/취소 토글 API
    POST body: { "post_id": int, "member_id": int }
    """
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}
            
        post_id = body.get('post_id')
        member_id = body.get('member_id')
        
        if not post_id or not member_id:
            return JsonResponse({"status": "Error", "message": "post_id and member_id are required"}, status=400)
            
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)
            
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "member not found"}, status=404)
            
        # 좋아요 토글 로직
        if post.likes.filter(id=member.id).exists():
            post.likes.remove(member)
            liked = False
        else:
            post.likes.add(member)
            liked = True
            
        return JsonResponse({
            "status": "OK",
            "liked": liked,
            "like_count": post.likes.count()
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def add_comment(request):
    """
    댓글 및 대댓글 추가 API
    POST body: { 
        "post_id": int, 
        "author_id": int, 
        "content": str,
        "parent_id": int (Optional, 대댓글일 경우)
    }
    """
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}
            
        post_id = body.get('post_id')
        author_id = body.get('author_id')
        content = body.get('content')
        parent_id = body.get('parent_id')
        
        if not all([post_id, author_id, content]):
            return JsonResponse({"status": "Error", "message": "post_id, author_id, content are required"}, status=400)
            
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)
            
        try:
            author = Member.objects.get(id=author_id)
        except Member.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "author not found"}, status=404)
            
        parent_comment = None
        if parent_id:
            try:
                # 해당 게시글에 속한 부모 댓글인지 확인하며 조회
                parent_comment = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return JsonResponse({"status": "Error", "message": "parent comment not found in this post"}, status=404)
        
        comment = Comment.objects.create(
            post=post,
            author=author,
            content=content,
            parent=parent_comment
        )
        
        return JsonResponse({
            "status": "OK",
            "message": "Comment created",
            "comment_id": comment.id,
            "created_at": comment.created_at.isoformat()
        }, status=201)
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

@csrf_exempt
def delete_comment(request):
    """
    댓글 삭제 API
    POST body: { "comment_id": int, "author_id": int }
    
    - 자식 댓글(대댓글)이 있는 경우: 내용과 작성자 정보만 지우고 레코드는 유지 (Soft Delete)
    - 자식 댓글이 없는 경우: DB에서 완전히 삭제 (Hard Delete)
    """
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}
            
        comment_id = body.get('comment_id')
        author_id = body.get('author_id')
        
        if not comment_id or not author_id:
            return JsonResponse({"status": "Error", "message": "comment_id and author_id are required"}, status=400)
            
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "comment not found"}, status=404)
            
        try:
            author = Member.objects.get(id=author_id)
        except Member.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "member not found"}, status=404)
            
        # 작성자 권한 확인
        # author가 None인 경우(이미 삭제된 댓글)는 삭제 불가
        if not comment.author or comment.author.id != author.id:
            return JsonResponse({"status": "Error", "message": "Permission denied"}, status=403)
            
        # 자식 댓글(대댓글) 존재 여부 확인
        if comment.replies.exists():
            # 자식이 있으면 구조 유지를 위해 내용만 삭제 (Soft Delete)
            comment.content = "삭제된 댓글입니다."
            comment.author = None  # 작성자 정보 제거
            comment.save()
            message = "Comment deleted (content cleared to maintain structure)"
        else:
            # 자식이 없으면 물리적 삭제 (Hard Delete)
            comment.delete()
            message = "Comment deleted permanently"
            
        return JsonResponse({
            "status": "OK",
            "message": message
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

def read_comments_list(request):
    """
    게시글별 댓글 목록 조회 API (페이지네이션 포함)
    GET query params: post_id, page(default=1), count(default=10)
    최상위 댓글(부모가 없는 댓글)을 기준으로 페이지네이션하며, 
    각 최상위 댓글의 대댓글(replies)을 포함하여 반환합니다.
    """
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "Error", "message": "Only GET method is allowed"}, status=405)
            
        post_id = request.GET.get('post_id')
        if not post_id:
            return JsonResponse({"status": "Error", "message": "post_id is required"}, status=400)
            
        page_str = request.GET.get('page', '1')
        count_str = request.GET.get('count') or request.GET.get('size') or '10'
        
        try:
            page = int(page_str)
            count = int(count_str)
        except Exception:
            return JsonResponse({"status": "Error", "message": "page and count must be integers"}, status=400)
            
        if page < 1 or count < 1:
            return JsonResponse({"status": "Error", "message": "page and count must be >= 1"}, status=400)
            
        offset = (page - 1) * count
        
        # 최상위 댓글만 필터링
        root_comments_qs = Comment.objects.filter(
            post_id=post_id, 
            parent__isnull=True
        ).order_by('created_at')
        
        total_root_comments = root_comments_qs.count()
        
        # 페이지네이션 적용 및 필요한 관계 데이터 미리 로드 (N+1 방지)
        # select_related: author (작성자 정보)
        # prefetch_related: replies (대댓글), replies__author (대댓글 작성자)
        root_comments = list(
            root_comments_qs
            .select_related('author')
            .prefetch_related('replies', 'replies__author')
            [offset:offset+count]
        )
        
        results = []
        for comment in root_comments:
            # 대댓글 처리
            replies_data = []
            for reply in comment.replies.all().order_by('created_at'):
                replies_data.append({
                    "id": reply.id,
                    "content": reply.content,
                    "author": {
                        "id": reply.author.id if reply.author else None,
                        "name": reply.author.name if reply.author else "Anonymous"
                    },
                    "created_at": reply.created_at.isoformat(),
                    "updated_at": reply.updated_at.isoformat()
                })
                
            results.append({
                "id": comment.id,
                "content": comment.content,
                "author": {
                    "id": comment.author.id if comment.author else None,
                    "name": comment.author.name if comment.author else "Anonymous"
                },
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
                "replies": replies_data
            })
            
        return JsonResponse({
            "status": "OK",
            "post_id": post_id,
            "page": page,
            "count": count,
            "total": total_root_comments,
            "results": results
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
