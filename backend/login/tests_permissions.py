"""Permission regressions: identities, role boundaries and private ranking data."""
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import path
from django.utils import timezone

from account.models import Student
from board.models import Comment, Post
from board.api.views import add_comment, delete_comment, update_post
from course.models import Course, Course_registration
from login.middleware import MemberPermissionsMiddleware
from login.models import Member, Student as LoginStudent
from login.profile import profile_student
from scoring.api.views import course_ranking, student_aptitude
from scoring.models import ScoringParameterSet, ScoringRun, StudentCourseScore


urlpatterns = [
    path('api/board/update_post', update_post, name='update_post'),
    path('api/board/add_comment', add_comment, name='add_comment'),
    path('api/board/delete_comment', delete_comment, name='delete_comment'),
    path('api/scoring/student-aptitude', student_aptitude, name='scoring-student-aptitude'),
    path('api/scoring/course-ranking', course_ranking, name='scoring-course-ranking'),
]


class MemberPermissionsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = MemberPermissionsMiddleware(lambda request: None)
        self.member = Member.objects.create(id='uid-a', name='Student A', role='STUDENT', email='a@example.com')
        self.student = Student.objects.create(id='student-a', name='Student A', github_id='a')
        LoginStudent.objects.create(id=self.student.pk, member=self.member)
        self.other = Student.objects.create(id='student-b', name='Student B')
        Member.objects.create(id='admin', name='Admin', role='ADMIN', email='admin@example.com')
        Member.objects.create(id='professor', name='Professor', role='PROFESSOR', email='prof@example.com')

    def request(self, app, name, data=None, method='POST', uid='uid-a', token=True):
        headers = {'HTTP_AUTHORIZATION': 'Bearer test-token'} if token else {}
        path = f'/api/{app}/{name}'
        if method == 'GET':
            request = self.factory.get(path, data or {}, **headers)
        else:
            request = self.factory.post(path, json.dumps(data or {}), content_type='application/json', **headers)
        request.resolver_match = SimpleNamespace(url_name=name)
        with patch('login.middleware.verify_firebase_token', return_value={'uid': uid, 'email_verified': True}):
            response = self.middleware.process_view(request, lambda req: None, (), {})
        return request, response

    def test_unauthenticated_reads_are_denied(self):
        for app, name in [('board', 'read_posts_list'), ('scoring', 'scoring-course-ranking'), ('account', 'student_read_total')]:
            with self.subTest(name=name):
                _, response = self.request(app, name, method='GET', token=False)
                self.assertEqual(response.status_code, 401)

    def test_invalid_token_is_denied(self):
        request = self.factory.get('/api/board/read_post', HTTP_AUTHORIZATION='Bearer invalid')
        request.resolver_match = SimpleNamespace(url_name='read_post')
        with patch('login.middleware.verify_firebase_token', side_effect=ValueError):
            response = self.middleware.process_view(request, None, (), {})
        self.assertEqual(response.status_code, 401)

    def test_unverified_email_is_denied(self):
        request = self.factory.get('/api/board/read_post', HTTP_AUTHORIZATION='Bearer test-token')
        request.resolver_match = SimpleNamespace(url_name='read_post')
        with patch('login.middleware.verify_firebase_token', return_value={'uid': self.member.pk, 'email_verified': False}):
            response = self.middleware.process_view(request, None, (), {})
        self.assertEqual(response.status_code, 403)

    def test_missing_student_mapping_is_denied(self):
        LoginStudent.objects.filter(member=self.member).delete()
        _, response = self.request('scoring', 'scoring-course-ranking', method='GET')
        self.assertEqual(response.status_code, 403)

    @override_settings(ROOT_URLCONF='login.tests_permissions', MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'])
    def test_http_dispatch_creates_qna_with_verified_author(self):
        with patch('login.middleware.verify_firebase_token', return_value={'uid': self.member.pk, 'email_verified': True}):
            response = Client().post('/api/board/update_post', {
                'author': 'admin', 'title': 'Question', 'content': 'Content',
                'category': 'QNA', 'year': 2026, 'semester': '1',
            }, content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token')
        self.assertEqual(response.status_code, 201)
        post = Post.objects.get()
        self.assertEqual(post.author, self.member.pk)
        self.assertTrue(post.is_owner(self.member.pk))

    @override_settings(ROOT_URLCONF='login.tests_permissions', MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'])
    def test_http_dispatch_rejects_forbidden_comment_before_saving(self):
        post = Post.objects.create(author='admin', title='Event', content='Text', category='EVENT_INFO', year=2026, semester='1')
        with patch('login.middleware.verify_firebase_token', return_value={'uid': self.member.pk, 'email_verified': True}):
            response = Client().post('/api/board/add_comment', {
                'author_id': 'admin', 'content': 'Comment', 'post_id': post.pk,
            }, content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Comment.objects.exists())

    @override_settings(ROOT_URLCONF='login.tests_permissions', MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'])
    def test_http_dispatch_rejects_cross_student_aptitude(self):
        with patch('login.middleware.verify_firebase_token', return_value={'uid': self.member.pk, 'email_verified': True}):
            client = Client(HTTP_AUTHORIZATION='Bearer test-token')
            response = client.get('/api/scoring/student-aptitude', {'student_id': self.other.pk})
            self.assertEqual(response.status_code, 403)
            response = client.get('/api/scoring/student-aptitude')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['student_id'], self.student.pk)

    @override_settings(ROOT_URLCONF='login.tests_permissions', MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'])
    def test_student_cannot_delete_another_authors_qna_comment(self):
        post = Post.objects.create(author='admin', title='Q', content='Text', category='QNA', year=2026, semester='1')
        comment = Comment.objects.create(post=post, author_id='admin', content='Answer')
        with patch('login.middleware.verify_firebase_token', return_value={'uid': self.member.pk, 'email_verified': True}):
            response = Client().post('/api/board/delete_comment', {
                'author_id': 'admin', 'comment_id': comment.pk,
            }, content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())

    @override_settings(ROOT_URLCONF='login.tests_permissions', MIDDLEWARE=['login.middleware.MemberPermissionsMiddleware'])
    def test_admin_can_delete_non_qna_comment_from_another_author(self):
        post = Post.objects.create(author='admin', title='Event', content='Text', category='EVENT_INFO', year=2026, semester='1')
        comment = Comment.objects.create(post=post, author=self.member, content='Comment')
        with patch('login.middleware.verify_firebase_token', return_value={'uid': 'admin', 'email_verified': True}):
            response = Client().post('/api/board/delete_comment', {
                'author_id': self.member.pk, 'comment_id': comment.pk,
            }, content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_unregistered_and_professor_accounts_are_denied(self):
        for uid in ('missing-member', 'professor'):
            _, response = self.request('board', 'read_posts_list', method='GET', uid=uid)
            self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_admin_endpoints(self):
        for app, name in [('account', 'student_excel_import'), ('repo', 'repo_read_db'), ('course', 'course_read_db')]:
            _, response = self.request(app, name)
            self.assertEqual(response.status_code, 403)

    def test_admin_can_access_admin_endpoints(self):
        _, response = self.request('account', 'student_excel_import', uid='admin')
        self.assertIsNone(response)

    def test_signin_uses_verified_identity_instead_of_supplied_uid(self):
        request, response = self.request('login', 'signin', {'uuid': 'admin'})
        self.assertIsNone(response)
        self.assertEqual(json.loads(request.body)['uuid'], self.member.pk)

    def test_profile_uses_own_database_mapping(self):
        request, response = self.request('repo', 'repo_account_read_db', {'uuid': 'empty', 'student_num': self.student.pk})
        self.assertIsNone(response)
        self.assertEqual(request.member_student_id, self.student.pk)
        self.assertEqual(json.loads(request.body)['uuid'], self.member.pk)
        self.assertEqual(profile_student(request, 'forged-uid'), self.student)

    def test_student_cannot_substitute_another_uid_or_student_number(self):
        for data in ({'uuid': 'admin'}, {'student_num': self.other.pk}, {'student_id': self.other.pk}):
            for app, name in [('repo', 'repo_account_read_db'), ('account', 'update_student_introduction')]:
                _, response = self.request(app, name, data)
                self.assertEqual(response.status_code, 403)

    def test_admin_can_select_student_without_a_login_mapping(self):
        request, response = self.request('account', 'update_student_introduction', {'uuid': 'admin', 'student_id': self.other.pk}, uid='admin')
        self.assertIsNone(response)
        self.assertEqual(profile_student(request, 'admin'), self.other)

    def test_students_can_create_qna_only_and_cannot_impersonate_author(self):
        request, response = self.request('board', 'update_post', {'category': 'QNA', 'author': 'admin'})
        self.assertIsNone(response)
        self.assertEqual(json.loads(request.body)['author'], self.member.pk)
        for category in ('EVENT_INFO', 'LEARNING_MATERIAL', 'OPENSOURCE_REPO'):
            _, response = self.request('board', 'update_post', {'category': category})
            self.assertEqual(response.status_code, 403)

    def test_students_cannot_comment_or_like_outside_qna(self):
        post = Post.objects.create(author='admin', title='Event', content='Text', category='EVENT_INFO', year=2026, semester='1')
        _, response = self.request('board', 'add_comment', {'post_id': post.pk})
        self.assertEqual(response.status_code, 403)
        _, response = self.request('board', 'toggle_post_like', {'post_id': post.pk})
        self.assertEqual(response.status_code, 403)

    def test_qna_comments_use_verified_author(self):
        post = Post.objects.create(author='admin', title='Question', content='Text', category='QNA', year=2026, semester='1')
        request, response = self.request('board', 'add_comment', {'post_id': post.pk, 'author_id': 'admin'})
        self.assertIsNone(response)
        self.assertEqual(json.loads(request.body)['author_id'], self.member.pk)

    def test_link_requires_qna_ownership_for_students(self):
        post = Post.objects.create(author='admin', title='Question', content='Text', category='QNA', year=2026, semester='1')
        _, response = self.request('board', 'link_drive_file', {'post_id': post.pk})
        self.assertEqual(response.status_code, 403)
        post.owners.add(self.member)
        _, response = self.request('board', 'link_drive_file', {'post_id': post.pk})
        self.assertIsNone(response)

    def test_crawling_and_signup_paths_keep_existing_behavior(self):
        for app, name in [('repo', 'sync_repo_commit_db'), ('repo', 'generate_repo_summary'), ('account', 'sync_student_db'), ('course', 'course_project_update'), ('login', 'signup'), ('authentication', 'studentIdNumber_verification')]:
            _, response = self.request(app, name, token=False)
            self.assertIsNone(response)

    def test_role_is_read_from_database_each_request(self):
        _, response = self.request('course', 'course_read_db', uid='admin')
        self.assertIsNone(response)
        Member.objects.filter(pk='admin').update(role='PROFESSOR')
        _, response = self.request('course', 'course_read_db', uid='admin')
        self.assertEqual(response.status_code, 403)

    def test_ranking_returns_only_attended_scored_courses_and_real_position(self):
        courses = []
        for i in range(3):
            course = Course.objects.create(course_id=f'TEST{i}', name=f'Course {i}', prof='Professor', year=2026, semester=1)
            parameter = ScoringParameterSet.objects.create(course=course)
            run = ScoringRun.objects.create(course=course, parameter_set=parameter, status=ScoringRun.Status.COMPLETED, is_canonical=True, completed_at=timezone.now())
            StudentCourseScore.objects.create(run=run, student=self.other, overall_score=90)
            if i != 2:
                StudentCourseScore.objects.create(run=run, student=self.student, overall_score=60)
            if i != 1:
                Course_registration.objects.create(course=course, student=self.student, course_year=2026, course_semester=1)
            courses.append(course)
        request, response = self.request('scoring', 'scoring-course-ranking', method='GET')
        self.assertIsNone(response)
        result = json.loads(course_ranking(request).content)
        self.assertEqual([row['course_id'] for row in result], ['TEST0'])
        self.assertEqual(len(result[0]['students']), 1)
        self.assertEqual(result[0]['students'][0]['student_id'], self.student.pk)
        self.assertEqual(result[0]['students'][0]['rank'], 2)
        request, response = self.request('scoring', 'scoring-course-ranking', method='GET', uid='admin')
        self.assertIsNone(response)
        self.assertEqual(len(json.loads(course_ranking(request).content)), 3)
