"""Feature lookup for the E-Profile repository modal and student profile."""
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from account.models import Student
from login.models import Role
from repo.feature_lookup import DEFAULT_DICTIONARY, DICTIONARIES, LookupFailure, load_snapshot
from repo.models import Repo_contributor, Repository


logger = logging.getLogger(__name__)


def student_can_view_repository(student_id, repository):
    github_id = Student.objects.filter(pk=student_id).values_list('github_id', flat=True).first()
    github_id = (github_id or '').strip().casefold()
    if not github_id:
        return False
    if github_id == (repository.owner_github_id or '').strip().casefold():
        return True
    contributor_list = repository.contributors or ''
    listed_contributors = set() if contributor_list == 'None' else {
        contributor.strip().casefold() for contributor in contributor_list.split(',')
    }
    return github_id in listed_contributors or Repo_contributor.objects.filter(
        repo_id=repository.pk, contributor_id__iexact=github_id,
    ).exists()


def read_page(query):
    try:
        limit = int(query.get('limit', '50'))
        offset = int(query.get('offset', '0'))
    except ValueError as exc:
        raise LookupFailure(400, 'invalid_pagination', 'limit과 offset은 정수여야 합니다.') from exc
    if not 1 <= limit <= 100 or offset < 0:
        raise LookupFailure(400, 'invalid_pagination', 'limit은 1~100, offset은 0 이상이어야 합니다.')
    return limit, offset


def lookup(request):
    member = getattr(request, 'member', None)
    if member is None:
        raise LookupFailure(401, 'authentication_required', 'KUCODE 로그인이 필요합니다.')
    if member.role not in (Role.ADMIN, Role.STUDENT):
        raise LookupFailure(403, 'forbidden', '기능 조회 권한이 없습니다.')

    own_id = getattr(request, 'member_student_id', None)
    requested_student = (request.GET.get('student_id') or '').strip() or None
    repo_id = (request.GET.get('repo_id') or '').strip()
    if len(repo_id) > 50 or (requested_student and len(requested_student) > 50):
        raise LookupFailure(400, 'invalid_selector', '유효한 KUCODE 레포 ID 또는 학생 ID가 필요합니다.')
    student_id = requested_student
    if member.role == Role.STUDENT:
        if own_id is None or (requested_student and requested_student != str(own_id)):
            raise LookupFailure(403, 'forbidden_student', '본인 학생 정보만 조회할 수 있습니다.')
        student_id = str(own_id)

    default_scope = 'repository' if repo_id and not requested_student else 'contributed'
    scope = request.GET.get('scope') or default_scope
    if scope not in ('repository', 'contributed'):
        raise LookupFailure(400, 'invalid_scope', 'scope는 repository 또는 contributed여야 합니다.')
    if scope == 'repository' and not repo_id:
        raise LookupFailure(400, 'missing_repository', '레포 전체 조회에는 repo_id가 필요합니다.')
    if scope == 'contributed' and not student_id:
        raise LookupFailure(400, 'missing_student', '기여 조회에는 학생 ID가 필요합니다.')

    dictionary = request.GET.get('dictionary') or DEFAULT_DICTIONARY
    if dictionary not in DICTIONARIES:
        raise LookupFailure(400, 'invalid_dictionary', '지원하는 기능 사전 이름을 지정하세요.')
    limit, offset = read_page(request.GET)

    repository = None
    if repo_id:
        repository = Repository.objects.filter(pk=repo_id).first()
        if repository is None or (member.role == Role.STUDENT and not student_can_view_repository(student_id, repository)):
            raise LookupFailure(404, 'repository_not_found', '조회할 수 있는 레포를 찾을 수 없습니다.')

    snapshot_path = settings.FEATURE_LOOKUP_SNAPSHOT
    if not snapshot_path:
        raise LookupFailure(503, 'snapshot_unavailable', '기능 분석 데이터가 아직 연결되지 않았습니다.')
    try:
        snapshot = load_snapshot(snapshot_path)
    except (OSError, KeyError, ValueError, TypeError, AttributeError):
        logger.exception('Feature analysis snapshot could not be loaded')
        raise LookupFailure(503, 'snapshot_unavailable', '기능 분석 데이터를 사용할 수 없습니다.')
    return snapshot.features(
        repository=repository, student_id=student_id, dictionary=dictionary,
        scope=scope, limit=limit, offset=offset,
    )


@never_cache
@require_GET
def repository_features(request):
    try:
        return JsonResponse(lookup(request))
    except LookupFailure as exc:
        return JsonResponse({'code': exc.code, 'message': str(exc)}, status=exc.status)
