import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import include, path

from account.models import Student
from login.models import Member, Role, Student as LoginStudent
from repo.feature_lookup import load_snapshot
from repo.models import Repo_contributor, Repository


urlpatterns = [path('api/repo/', include('repo.api.urls'))]
FEATURE_URL = '/api/repo/features/'


def feature_snapshot():
    url = 'https://github.com/Owner/Project'
    units = {}
    for unit_id, student_id, title in [('one', 'student-a', '로그인'), ('two', 'student-b', '로그아웃')]:
        units[unit_id] = {
            'title': title, 'purpose': '인증 흐름 처리', 'kind': 'function',
            'source': {
                'codebaseId': 'cb_42', 'repoUrl': url, 'commit': 'a' * 40,
                'path': 'src/a file.py', 'qualifiedName': 'sample',
                'startLine': 3, 'endLine': 8, 'language': 'python',
            },
            'contributors': [{'studentIds': [student_id], 'lineShare': 0.5}],
        }
    entries = []
    for unit_id, unit in units.items():
        entries.append({
            'id': unit_id, 'name': unit['title'], 'definition': '기능 정의', 'status': 'draft',
            'mixedScope': False, 'reviewFlags': [], 'suspectUnitIds': ['one'],
            'memberUnitIds': [unit_id],
        })
    return {
        'schemaVersion': 'feature-api-snapshot-v1', 'run': 'test-run',
        'units': units, 'students': {'student-a': {}, 'student-b': {}},
        'repositories': {'cb_42': {
            'repoUrl': url, 'aliases': [url, 'https://github.com/team/fork'],
            'unitIds': list(units),
        }},
        'dictionaries': {
            'spec_hierarchical': {'status': 'draft', 'entries': entries, 'unassignedUnitIds': []},
            'spec_umap_hdbscan': {'status': 'draft', 'entries': entries[:1], 'unassignedUnitIds': ['two']},
        },
    }


@override_settings(
    ROOT_URLCONF=__name__,
    MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'],
)
class RepositoryFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = Member.objects.create(id='uid-a', name='A', role=Role.STUDENT, email='a@example.test')
        Member.objects.create(id='admin', name='Admin', role=Role.ADMIN, email='admin@example.test')
        Student.objects.create(id='student-a', name='A', github_id='alice')
        LoginStudent.objects.create(id='student-a', member=cls.member)
        Repository.objects.create(pk='42', name='Project', owner_github_id='Owner', contributors='ALICE, bob')
        Repository.objects.create(pk='43', name='fork', owner_github_id='team')
        Repo_contributor.objects.create(repo_id='43', contributor_id='Alice')
        Repository.objects.create(pk='44', name='Other', owner_github_id='other', contributors='alice-other')
        Repository.objects.create(pk='45', name='Missing', owner_github_id='alice')

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.addCleanup(load_snapshot.cache_clear)
        self.snapshot_path = Path(temporary.name) / 'snapshot.json'
        self.snapshot_path.write_text(json.dumps(feature_snapshot()), encoding='utf-8')
        config = override_settings(FEATURE_LOOKUP_SNAPSHOT=str(self.snapshot_path))
        config.enable()
        self.addCleanup(config.disable)

    def get(self, query, uid='uid-a'):
        claims = {'uid': uid, 'email_verified': True}
        with patch('login.middleware.verify_firebase_token', return_value=claims):
            return self.client.get(FEATURE_URL, query, HTTP_AUTHORIZATION='Bearer firebase-test-token')

    def test_modal_uses_existing_repository_id_and_returns_source_links(self):
        response = self.get({'repo_id': '42'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        result = response.json()
        self.assertEqual(result['repository']['id'], '42')
        self.assertEqual(result['dictionary'], 'spec_hierarchical')
        self.assertEqual(result['scope'], 'repository')
        self.assertEqual(result['summary']['selectedBlockCount'], 2)
        evidence = result['features'][0]['evidence'][0]
        self.assertEqual(evidence['sourceUrl'], f'https://github.com/Owner/Project/blob/{"a" * 40}/src/a%20file.py#L3-L8')
        self.assertEqual(evidence['studentLineShare'], 0.5)
        self.assertTrue(evidence['needsReview'])

    def test_contribution_scope_uses_verified_student_and_intersects_repo(self):
        for query in ({}, {'repo_id': '42', 'scope': 'contributed'}, {'repo_id': '42', 'student_id': 'student-a'}):
            with self.subTest(query=query):
                response = self.get(query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['studentId'], 'student-a')
                self.assertEqual([f['id'] for f in response.json()['features']], ['one'])

    def test_repo_alias_can_be_resolved_with_exact_current_contributor(self):
        response = self.get({'repo_id': '43'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['repository']['codebaseId'], 'cb_42')

    def test_missing_token_and_cross_student_lookup_are_denied(self):
        self.assertEqual(self.client.get(FEATURE_URL, {'repo_id': '42'}).status_code, 401)
        self.assertEqual(self.get({'repo_id': '42', 'student_id': 'student-b'}).status_code, 403)

    def test_contributor_substring_does_not_grant_access(self):
        response = self.get({'repo_id': '44'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['code'], 'repository_not_found')

    def test_admin_can_select_student_or_repository(self):
        result = self.get({'student_id': 'student-b'}, uid='admin').json()
        self.assertEqual([f['id'] for f in result['features']], ['two'])
        result = self.get({'repo_id': '42'}, uid='admin').json()
        self.assertIsNone(result['studentId'])
        self.assertEqual(result['summary']['selectedBlockCount'], 2)

    def test_no_analysis_and_missing_snapshot_have_distinct_responses(self):
        response = self.get({'repo_id': '45'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['code'], 'repository_not_analyzed')
        with override_settings(FEATURE_LOOKUP_SNAPSHOT=''):
            response = self.get({'repo_id': '42'})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['code'], 'snapshot_unavailable')

    def test_pagination_and_unassigned_counts(self):
        result = self.get({'repo_id': '42', 'limit': '1'}).json()
        self.assertEqual(result['totalFeatures'], 2)
        self.assertTrue(result['hasMore'])
        result = self.get({'repo_id': '42', 'dictionary': 'spec_umap_hdbscan'}).json()
        self.assertEqual(result['summary']['unassignedBlockCount'], 1)
        self.assertEqual(result['unassigned'][0]['unitId'], 'two')
        self.assertEqual(self.get({'repo_id': '42', 'limit': '0'}).status_code, 400)
