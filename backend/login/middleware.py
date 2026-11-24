"""Verified member identity and permissions for browser-facing APIs."""
import json
import logging

from django.http import JsonResponse

from login.firebase import verify_firebase_token
from login.models import Member, Role, Student as LoginStudent


logger = logging.getLogger(__name__)

# These operations are explicitly deferred. They keep their existing behavior.
DEFERRED = {
    'account': {
        'sync_student_db', 'sync_student_db_test', 'student_validation',
        'query_per_get_student_openapi', 'get_kuopenapi_access_token',
        'count_contributors_per_student', 'update_foreign_students',
    },
    'repo': {
        'sync_repo_db', 'sync_repo_db_optional', 'sync_repo_category',
        'sync_repo_contributor_db', 'sync_repo_issue_db', 'sync_repo_pr_db',
        'sync_repo_commit_db', 'sync_repo_snapshot_db',
        'sync_repo_review_comment_db', 'sync_repo_dependabot_alert_db',
        'sync_repo_db_test', 'sync_repo_contributor_db_test',
        'sync_repo_issue_db_test', 'sync_repo_pr_db_test',
        'sync_repo_commit_db_test', 'generate_repo_summary',
    },
    'course': {'course_project_update', 'course_validation', 'course_reg_validation'},
}
PROFILE = {
    ('repo', 'repository_features'),
    ('repo', 'repo_account_read_db'),
    ('repo', 'update_student_repository_tags'),
    ('repo', 'update_repo_introduction'),
    ('scoring', 'scoring-student-aptitude'),
    ('account', 'update_student_introduction'),
    ('account', 'update_student_technology_stack'),
}
BOARD_READ = {
    'read_posts_list', 'read_post', 'read_comments_list',
    'read_company_repos_list', 'read_trending_repos_list',
    'read_owner_candidates',
}


def error(message, status):
    return JsonResponse({'status': 'Error', 'message': message}, status=status)


class MemberPermissionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        parts = request.path.strip('/').split('/')
        if len(parts) < 3 or parts[0] != 'api' or request.method == 'OPTIONS':
            return None
        app = parts[1]
        if app not in {'account', 'repo', 'course', 'board', 'scoring', 'login', 'authentication'}:
            return None
        name = request.resolver_match.url_name
        if name in {'healthcheck', 'ping'}:
            return None
        if (app, name) in {('login', 'signup'), ('authentication', 'studentIdNumber_verification')}:
            return None
        if name in DEFERRED.get(app, set()):
            return None

        authorization = request.headers.get('Authorization', '').split()
        if len(authorization) != 2 or authorization[0].lower() != 'bearer':
            return error('Firebase ID token required.', 401)
        try:
            claims = verify_firebase_token(authorization[1])
        except ImportError:
            return error('Authentication dependency unavailable; rebuild the backend.', 503)
        except Exception as exc:
            # Never include tokens or credentials in an error/log message.
            logger.warning('Firebase token verification failed (%s)', type(exc).__name__)
            return error('Invalid or expired Firebase ID token.', 401)
        uid = claims.get('uid') or claims.get('sub')
        if not uid:
            return error('Invalid Firebase identity.', 401)
        if not claims.get('email_verified', False):
            return error('Email verification required.', 403)
        try:
            member = Member.objects.get(pk=uid)
        except Member.DoesNotExist:
            return error('Registered member not found.', 403)
        if member.role not in {Role.ADMIN, Role.STUDENT}:
            return error('Access for this role is not enabled.', 403)
        request.member = member
        request.is_admin = member.role == Role.ADMIN
        request.firebase_claims = claims
        request.member_student_id = None

        # Parse JSON once before canonicalizing legacy identity parameters.
        data = {}
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and request.content_type == 'application/json':
            try:
                data = json.loads(request.body or b'{}')
            except (ValueError, UnicodeDecodeError):
                return error('Invalid JSON body.', 400)
            if not isinstance(data, dict):
                return error('JSON body must be an object.', 400)

        if app == 'login' and name == 'signin':
            return self.bind_identity(request, data, 'uuid')

        if (app, name) in PROFILE or (app, name) == ('scoring', 'scoring-course-ranking'):
            if not request.is_admin:
                try:
                    request.member_student_id = LoginStudent.objects.get(member=member).pk
                except LoginStudent.DoesNotExist:
                    return error('Student account mapping not found.', 403)
                except LoginStudent.MultipleObjectsReturned:
                    return error('Student account mapping is ambiguous.', 403)
                target = self.check_student_target(request, data)
                if target is not None:
                    return target
                self.bind_identity(request, data, 'uuid')
                if (app, name) == ('scoring', 'scoring-student-aptitude'):
                    query = request.GET.copy()
                    query['student_id'] = request.member_student_id
                    request.GET = query
            return None

        if app == 'board':
            if name in BOARD_READ:
                query = request.GET.copy()
                query['uuid'] = member.pk
                request.GET = query
                return None
            if name == 'update_post':
                if not request.is_admin and data.get('category') != 'QNA':
                    return error('Students may create Q&A posts only.', 403)
                return self.bind_identity(request, data, 'author')
            if name == 'toggle_post_like':
                if not request.is_admin:
                    return error('This board is read-only for students.', 403)
                return self.bind_identity(request, data, 'member_id')
            if name in {'add_comment', 'delete_comment', 'link_drive_file'}:
                from board.models import Comment, Post
                try:
                    post = (
                        Comment.objects.select_related('post').get(pk=data.get('comment_id')).post
                        if name == 'delete_comment'
                        else Post.objects.get(pk=data.get('post_id'))
                    )
                except (Post.DoesNotExist, Comment.DoesNotExist, ValueError, TypeError):
                    return error('Post or comment not found.', 404)
                if not request.is_admin and post.category != 'QNA':
                    return error('This board is read-only for students.', 403)
                if name == 'link_drive_file' and not request.is_admin and not post.is_owner(member.pk):
                    return error('Only post owners may attach a link.', 403)
                if name != 'link_drive_file':
                    return self.bind_identity(request, data, 'author_id')
                return None

        if not request.is_admin:
            return error('Administrator access required.', 403)
        return None

    @staticmethod
    def bind_identity(request, data, key):
        if request.method == 'GET':
            query = request.GET.copy()
            query[key] = request.member.pk
            request.GET = query
        else:
            data[key] = request.member.pk
            request._body = json.dumps(data).encode('utf-8')
        return None

    @staticmethod
    def check_student_target(request, data):
        for source in (request.GET, data):
            uid = source.get('uuid')
            if uid not in (None, '', 'empty', request.member.pk):
                return error('Cannot access another student.', 403)
            for key in ('student_id', 'student_num'):
                value = source.get(key)
                if value not in (None, '', 'empty') and str(value) != str(request.member_student_id):
                    return error('Cannot access another student.', 403)
        return None
