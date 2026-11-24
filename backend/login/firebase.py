"""Firebase identity verification for the application's login API."""
from threading import Lock

from django.conf import settings


_initialization_lock = Lock()


def verify_firebase_token(token):
    # Import lazily so health checks and the deferred crawler endpoints can
    # start before the rebuilt image has installed the Admin SDK.
    import firebase_admin
    from firebase_admin import auth, credentials

    with _initialization_lock:
        try:
            app = firebase_admin.get_app('kuoss-login')
        except ValueError:
            credential = credentials.Certificate(settings.FIREBASE_CONFIG)
            app = firebase_admin.initialize_app(
                credential,
                {'projectId': settings.FIREBASE_PROJECT_ID},
                name='kuoss-login',
            )
    return auth.verify_id_token(token, app=app)
