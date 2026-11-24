import logging

from django.conf import settings
from django.core.mail import send_mail

from board.models import PostCategory


logger = logging.getLogger(__name__)


def notify_post_owners(comment):
    """Email all post owners except the member who wrote the response.

    Delivery failure is logged and deliberately does not affect the saved
    comment or the API response.
    """
    actor_id = comment.author_id
    recipient_rows = (
        comment.post.owners
        .exclude(id=actor_id)
        .exclude(email__isnull=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )

    recipients = []
    seen = set()
    for email in recipient_rows:
        normalized = email.strip().lower()
        if normalized and normalized not in seen:
            recipients.append(email.strip())
            seen.add(normalized)

    if not recipients:
        return 0

    is_reply = comment.parent_id is not None
    if is_reply:
        response_name = '답글'
    elif comment.post.category == PostCategory.QNA:
        response_name = '답변'
    else:
        response_name = '댓글'

    author_name = comment.author.name if comment.author else '알 수 없는 사용자'
    subject = f'[KUOSS] 새 {response_name}: {comment.post.title}'
    message = (
        f'게시글 "{comment.post.title}"에 새 {response_name}이 등록되었습니다.\n\n'
        f'작성자: {author_name}\n'
        f'내용:\n{comment.content}'
    )

    try:
        return send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Failed to notify owners for board comment %s on post %s',
            comment.id,
            comment.post_id,
        )
        return 0
