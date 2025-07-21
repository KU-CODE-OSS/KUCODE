from django.urls import path
from .views import FirebaseLoginView, LogoutView, SessionStatusView, ProtectedView

urlpatterns = [
    path('login/', FirebaseLoginView.as_view(), name='firebase_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('session-status/', SessionStatusView.as_view(), name='session_status'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]