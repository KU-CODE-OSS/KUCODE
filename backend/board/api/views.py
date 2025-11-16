from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from board.models import Post, File, CompanyRepo, TrendingRepo


class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

def ping(request):
    return JsonResponse({"ok": True, "app": "board"})

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
            .values('id', 'title', 'author', 'category', 'is_internal', 'year', 'semester', 'created_at')[offset:offset+count]
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

        post_id = request.GET.get('post_id') or request.GET.get('id')
        if not post_id:
            return JsonResponse({"status": "Error", "message": "post_id is required"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)

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
        
# ========================================
# unfinished
# ========================================
@csrf_exempt
def update_file(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Error", "message": "Only POST method is allowed"}, status=405)
    try:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            body = {}

        post_id = body.get('post_id')
        file_name = body.get('file_name')
        storage_link = body.get('storage_link')
        file_extension = body.get('file_extension')
        display_type = body.get('display_type')

        required_fields = {
            'post_id': post_id, 'file_name': file_name, 'storage_link': storage_link,
            'file_extension': file_extension, 'display_type': display_type
        }
        missing = [k for k, v in required_fields.items() if v in [None, ""]]
        if missing:
            return JsonResponse({"status": "Error", "message": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "post not found"}, status=404)

        file_obj = File.objects.create(
            post=post,
            file_name=file_name,
            storage_link=storage_link,
            file_extension=file_extension,
            display_type=display_type
        )

        return JsonResponse({
            "status": "OK",
            "message": "File created",
            "file_id": file_obj.id
        }, status=201)
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

