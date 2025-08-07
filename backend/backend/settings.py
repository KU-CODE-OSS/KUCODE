from pathlib import Path
import environ
import os

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default='').split(",")

PUBLIC_IP = env("PUBLIC_IP")
FASTAPI_PORT = env("FASTAPI_PORT")

OAUTH_CLIENT_ID = env("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = env ("OAUTH_CLIENT_SECRET")
KOREAUNIV_OPENAPI_CLIENT_ID=env("KOREAUNIV_OPENAPI_CLIENT_ID")
KOREAUNIV_OPENAPI_CLIENT_SECRET=env("KOREAUNIV_OPENAPI_CLIENT_SECRET")

STUDENT_SYNC_URL=env("STUDENT_SYNC_URL")
REPO_SYNC_URL=env("REPO_SYNC_URL")
REPO_COMMIT_SYNC_URL=env("REPO_COMMIT_SYNC_URL")
REPO_ISSUE_SYNC_URL=env("REPO_ISSUE_SYNC_URL")
REPO_PR_SYNC_URL=env("REPO_PR_SYNC_URL")
REPO_CONTRIBUTOR_SYNC_URL=env("REPO_CONTRIBUTOR_SYNC_URL")

# COURSE_20241OS01_SYNC_URL= env("COURSE_20241OS01_SYNC_URL")
# COURSE_20241CAPSTONE00_SYNC_URL= env("COURSE_20241CAPSTONE00_SYNC_URL")
# COURSE_20242CLOUD00_SYNC_URL= env("COURSE_20242CLOUD00_SYNC_URL")
# COURSE_20242SWPROJECT00_SYNC_URL= env("COURSE_20242SWPROJECT00_SYNC_URL")
# COURSE_20242CAPSTONE02_SYNC_URL= env("COURSE_20242CAPSTONE02_SYNC_URL")
# COURSE_20242SWENGINEERING00_SYNC_URL= env("COURSE_20242SWENGINEERING00_SYNC_URL")
# COURSE_20242DL02_SYNC_URL=env("COURSE_20242DL02_SYNC_URL")
# COURSE_20242CAPSTONE01_SYNC_URL=env("COURSE_20242CAPSTONE01_SYNC_URL")

# COURSE_20251OS02_SYNC_URL=env("COURSE_20251OS02_SYNC_URL")
# COURSE_20251OS03_SYNC_URL=env("COURSE_20251OS03_SYNC_URL")
# COURSE_20251COLLOQUIUM_SYNC_URL=env("COURSE_20251COLLOQUIUM_SYNC_URL")
# COURSE_20251DATASCIENCE_SYNC_URL=env("COURSE_20251DATASCIENCE_SYNC_URL")
# COURSE_20251DEEPLEARNING_SYNC_URL=env("COURSE_20251DEEPLEARNING_SYNC_URL")
# COURSE_20251SWPROJECT01_SYNC_URL=env("COURSE_20251SWPROJECT01_SYNC_URL")
# COURSE_20251SWPROJECT02_SYNC_URL=env("COURSE_20251SWPROJECT02_SYNC_URL")

# Firebase project configuration variables
FIREBASE_PROJECT_ID=env("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID=env("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY=env("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL=env("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID=env("FIREBASE_CLIENT_ID")
FIREBASE_CLIENT_CERT_URL=env("FIREBASE_CLIENT_CERT_URL")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'authentication'
]

THIRD_PARTY_APPS = [
    'corsheaders'
]

LOCAL_APPS = [
    "core",
    "account",
    "repo",
    "course",
    "login",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Firebase project configuration
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": FIREBASE_PROJECT_ID,
    "private_key_id": FIREBASE_PRIVATE_KEY_ID,
    "private_key": FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
    "client_email": FIREBASE_CLIENT_EMAIL,
    "client_id": FIREBASE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": FIREBASE_CLIENT_CERT_URL
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'HOST': env('DB_HOST'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASS'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = 'account.User'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_URLS_REGEX = r"^/api/.*$"
#여기서 
CORS_ORIGIN_ALLOW_ALL = True
#여기까지 


if DEBUG:
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer'
        ]
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer'
        ]
    }
