import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session
from django.utils.decorators import method_decorator
from django.views import View
from authentication.models import FirebaseAuthUser
from django.conf import settings
# from .firebase_config import verify_firebase_token, get_firebase_user
from account.api.views import get_kuopenapi_access_token
import requests

@method_decorator(csrf_exempt, name='dispatch')
class FirebaseLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            id_token = data.get('idToken')
            
            if not id_token:
                return JsonResponse({'error': 'ID token is required'}, status=400)
            
            # Verify Firebase token
            decoded_token = settings.verify_firebase_token(id_token)
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
            user, created = FirebaseAuthUser.objects.get_or_create(
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
        
@csrf_exempt
# @require_http_methods(["GET"])
def studentIdNumber_verification(request):
    student_id = request.GET.get('student_id')
    student_name = request.GET.get('student_name')
    
    if not student_name:
        return JsonResponse({'error': 'student_name parameter is required'}, status=400)
    
    if not student_id:
        return JsonResponse({'error': 'student_id parameter is required'}, status=400)
    
    try:
        access_token = settings.KOREAUNIV_OPENAPI_TOKEN
        data = []
        empty_list = []
        
        #API 요청
        api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate"  # 실제 API 엔드포인트로 변경
        headers = {
            'AUTH_KEY': access_token
        }
        
        # 요청 파라미터 설정
        params = {
            'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
            'std_id' : student_id
        }
        
        # API 호출
        response = requests.get(api_url, headers=headers, params=params)

        # JSON 응답을 파싱
        response_data = response.json()
        
        # Check if the "result" key is an empty list
        if response_data.get("result") == []:
            #졸업생 쿼리 api 호출
            grad_api_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate-gra"  # 실제 API 엔드포인트로 변경

            headers = {
                'AUTH_KEY': access_token
            }
            
            params = {
                'client_id': settings.KOREAUNIV_OPENAPI_CLIENT_ID,
                'std_id' : student_id
            }
            
            # API 호출
            response = requests.get(grad_api_url, headers=headers, params=params)
            
            # JSON 응답을 파싱
            response_data = response.json()
            
            if response_data.get("result") == []:
                empty_list.append(student_id)

            else :    
                result_items = response_data.get("result", [])
                result_item = result_items[0]
                # result_list가 빈 리스트가 아닐 경우
                std_id = result_item.get("STD_ID")
                rec_sts_nm = result_item.get("REC_STS_NM")
                kor_nm = result_item.get("KOR_NM")
                col_nm = result_item.get("COL_NM")
                dept_nm = result_item.get("DEPT_NM")
                smajor_nm = result_item.get("SMAJOR_NM")          
                email_addr = result_item.get("EMAIL_ADDR")     

                # data 리스트에 새로운 딕셔너리 추가
                data.append({
                    "STD_ID": std_id,
                    "REC_STS_NM": rec_sts_nm,
                    "KOR_NM": kor_nm,
                    "COL_NM": col_nm,
                    "DEPT_NM": dept_nm,
                    "SMAJOR_NM":smajor_nm,
                    "email_addr": email_addr
                })
            
        else:
            # response_data에서 "result" 키의 값을 가져옴
            result_items = response_data.get("result", [])
            result_item = result_items[0]
            # result_list가 빈 리스트가 아닐 경우
            std_id = result_item.get("STD_ID")
            rec_sts_nm = result_item.get("REC_STS_NM")
            kor_nm = result_item.get("KOR_NM")
            col_nm = result_item.get("COL_NM")
            dept_nm = result_item.get("DEPT_NM")
            smajor_nm = result_item.get("SMAJOR_NM")          
            email_addr = result_item.get("EMAIL_ADDR")     

            # data 리스트에 새로운 딕셔너리 추가
            data.append({
                "STD_ID": std_id,
                "REC_STS_NM": rec_sts_nm,
                "KOR_NM": kor_nm,
                "COL_NM": col_nm,
                "DEPT_NM": dept_nm,
                "SMAJOR_NM":smajor_nm,
                "email_addr": email_addr
            })
 
        if data != []:
            if (data[0]['STD_ID'] == student_id) & (data[0]['KOR_NM'] == student_name):
                return JsonResponse({'verified': True})
            else:
                return JsonResponse({'verified': False})
            
        else:
            return JsonResponse({'verified': False})
    
    except Exception as e:
        print(e)
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)