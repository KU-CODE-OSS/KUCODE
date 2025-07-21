import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session
from django.utils.decorators import method_decorator
from django.views import View
from .models import CustomUser
from .firebase_config import verify_firebase_token, get_firebase_user

@method_decorator(csrf_exempt, name='dispatch')
class FirebaseLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            id_token = data.get('idToken')
            
            if not id_token:
                return JsonResponse({'error': 'ID token is required'}, status=400)
            
            # Verify Firebase token
            decoded_token = verify_firebase_token(id_token)
            if not decoded_token:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            
            # Check if email is from korea.ac.kr domain
            if not email.endswith('@korea.ac.kr'):
                return JsonResponse({
                    'error': '사용 가능한 @korea.ac.kr 이메일을 입력해주세요'
                }, status=400)
            
            # Get or create user
            user, created = CustomUser.objects.get_or_create(
                firebase_uid=firebase_uid,
                defaults={
                    'email': email,
                    'username': email.split('@')[0],
                    'korea_email': email,
                    'is_verified': decoded_token.get('email_verified', False)
                }
            )
            
            # Create Django session
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'isVerified': user.is_verified
                },
                'sessionId': request.session.session_key
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    @method_decorator(login_required)
    def post(self, request):
        logout(request)
        return JsonResponse({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class SessionStatusView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                    'isVerified': request.user.is_verified
                }
            })
        else:
            return JsonResponse({'authenticated': False})

@method_decorator(csrf_exempt, name='dispatch')
class ProtectedView(View):
    @method_decorator(login_required)
    def get(self, request):
        return JsonResponse({
            'message': 'This is a protected route',
            'user': request.user.username
        })