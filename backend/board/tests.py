import json

from django.test import RequestFactory, TestCase

from board.api.views import (
    add_comment,
    read_comments_list,
    read_posts_list,
    read_owner_candidates,
    read_post,
    update_post,
)
from board.models import Comment, Post
from login.models import Member, Role


class PostOwnershipApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.creator = Member.objects.create(
            id='creator-uuid',
            name='Creator',
            email='creator@example.com',
            role=Role.PROFESSOR,
        )
        self.co_owner = Member.objects.create(
            id='co-owner-uuid',
            name='Co-owner',
            email='co-owner@example.com',
            role=Role.ADMIN,
        )

    def create_post(self, **overrides):
        payload = {
            'author': self.creator.id,
            'owner_ids': [self.co_owner.id],
            'title': 'Shared post',
            'content': 'Content',
            'category': 'EVENT_INFO',
            'year': 2026,
            'semester': '1',
            'is_internal': True,
        }
        payload.update(overrides)
        return update_post(
            self.factory.post(
                '/api/board/update_post',
                data=json.dumps(payload),
                content_type='application/json',
            )
        )

    def test_creator_and_selected_members_become_owners(self):
        response = self.create_post()

        self.assertEqual(response.status_code, 201)
        post = Post.objects.get()
        self.assertEqual(
            set(post.owners.values_list('id', flat=True)),
            {self.creator.id, self.co_owner.id},
        )
        self.assertEqual(
            set(json.loads(response.content)['owner_ids']),
            {self.creator.id, self.co_owner.id},
        )

    def test_unknown_owner_rejects_post_without_partial_creation(self):
        response = self.create_post(owner_ids=['missing-member'])

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.exists())

    def test_post_detail_returns_owners_and_requester_ownership(self):
        create_response = self.create_post()
        post_id = json.loads(create_response.content)['post_id']

        response = read_post(
            self.factory.get(
                '/api/board/read_post',
                {'post_id': post_id, 'uuid': self.co_owner.id},
            )
        )
        body = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body['post']['is_owner'])
        self.assertEqual(
            {owner['id'] for owner in body['post']['owners']},
            {self.creator.id, self.co_owner.id},
        )

    def test_owner_candidates_do_not_expose_email_addresses(self):
        response = read_owner_candidates(
            self.factory.get('/api/board/read_owner_candidates')
        )
        body = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['results']), 2)
        self.assertNotIn('email', body['results'][0])


class LegacyPostOwnershipTests(TestCase):
    def test_author_without_member_can_still_create_legacy_post(self):
        response = update_post(
            RequestFactory().post(
                '/api/board/update_post',
                data=json.dumps({
                    'author': 'Anonymous',
                    'title': 'Legacy post',
                    'content': 'Content',
                    'category': 'EVENT_INFO',
                    'year': 2026,
                    'semester': '1',
                }),
                content_type='application/json',
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.get().owners.count(), 0)


class BoardCommentApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.author = Member.objects.create(
            id='comment-author',
            name='Comment Author',
            email='comment@example.com',
            role=Role.STUDENT,
        )
        self.post = Post.objects.create(
            author='post-author',
            title='Post',
            content='Content',
            category='EVENT_INFO',
            year=2026,
            semester='1',
        )

    def add(self, content, parent_id=None):
        return add_comment(
            self.factory.post(
                '/api/board/add_comment',
                data=json.dumps({
                    'post_id': self.post.id,
                    'author_id': self.author.id,
                    'content': content,
                    'parent_id': parent_id,
                }),
                content_type='application/json',
            )
        )

    def test_comment_and_reply_are_returned_as_one_level_thread(self):
        root_id = json.loads(self.add('Root').content)['comment_id']
        reply_response = self.add('Reply', parent_id=root_id)

        response = read_comments_list(
            self.factory.get(
                '/api/board/read_comments_list',
                {'post_id': self.post.id},
            )
        )
        body = json.loads(response.content)

        self.assertEqual(reply_response.status_code, 201)
        self.assertEqual(body['total'], 1)
        self.assertEqual(body['results'][0]['content'], 'Root')
        self.assertEqual(body['results'][0]['replies'][0]['content'], 'Reply')

    def test_reply_to_reply_is_normalized_to_root_thread(self):
        root_id = json.loads(self.add('Root').content)['comment_id']
        reply_id = json.loads(self.add('Reply', parent_id=root_id).content)['comment_id']
        nested_id = json.loads(self.add('Nested reply', parent_id=reply_id).content)['comment_id']

        self.assertEqual(Comment.objects.get(id=nested_id).parent_id, root_id)


class QnaPostApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.member = Member.objects.create(
            id='qna-author',
            name='Q&A Author',
            email='qna@example.com',
            role=Role.STUDENT,
        )

    def test_student_can_create_qna_post(self):
        response = update_post(
            self.factory.post(
                '/api/board/update_post',
                data=json.dumps({
                    'author': self.member.id,
                    'owner_ids': [],
                    'title': 'Question',
                    'content': 'How does this work?',
                    'category': 'QNA',
                    'year': 2026,
                    'semester': '1',
                }),
                content_type='application/json',
            )
        )

        self.assertEqual(response.status_code, 201)
        post = Post.objects.get()
        self.assertEqual(post.category, 'QNA')
        self.assertEqual(list(post.owners.values_list('id', flat=True)), [self.member.id])

    def test_post_list_can_be_filtered_to_qna(self):
        Post.objects.create(
            author=self.member.id,
            title='Question',
            content='Q',
            category='QNA',
            year=2026,
            semester='1',
        )
        Post.objects.create(
            author=self.member.id,
            title='Event',
            content='E',
            category='EVENT_INFO',
            year=2026,
            semester='1',
        )

        response = read_posts_list(
            self.factory.get(
                '/api/board/read_posts_list',
                {'uuid': self.member.id, 'category': 'QNA'},
            )
        )
        body = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['total'], 1)
        self.assertEqual(body['results'][0]['category'], 'QNA')
