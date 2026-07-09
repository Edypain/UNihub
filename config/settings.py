"""
Django settings for config project.
"""

from pathlib import Path
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')


_cloud_url = os.environ.get('CLOUDINARY_URL', '')


def get_env_value(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ImproperlyConfigured(f"The {name} environment variable is required.")
    return value


#  development settings
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-vercel-build-fallback')
else:
    SECRET_KEY = get_env_value('SECRET_KEY', required=True)

DEBUG = os.getenv('DEBUG', 'False') == 'True'

#  Cloudinary  (or explicitly enabled)
USE_CLOUDINARY = os.getenv('USE_CLOUDINARY', 'False') == 'True'
if not USE_CLOUDINARY:
    _is_vercel = os.getenv('VERCEL') is not None or os.getenv('VERCEL_ENV') is not None
    _is_prod_or_vercel = not DEBUG or _is_vercel
    if _is_prod_or_vercel and _cloud_url.startswith('cloudinary://') and 'build-fallback' not in _cloud_url and 'dummy-cloud' not in _cloud_url:
        USE_CLOUDINARY = True

default_allowed_hosts = [
    '127.0.0.1', 
    'localhost', 
    'testserver',
    'u-nihub-dq4v.vercel.app',  
    'unihub-nvx9.onrender.com',
]

allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()] or default_allowed_hosts

if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    if '.vercel.app' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('.vercel.app')
    
    vercel_url = os.getenv('VERCEL_URL')
    if vercel_url:
        ALLOWED_HOSTS.append(vercel_url)
        if not vercel_url.startswith('.'):
            ALLOWED_HOSTS.append(f".{vercel_url}")

# Render host detection
render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    ALLOWED_HOSTS.append(render_host)
    if not render_host.startswith('.'):
        ALLOWED_HOSTS.append(f".{render_host}")


# Application definition
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'cloudinary_storage', 
    'cloudinary',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'tailwind',
    'rest_framework',

    'core',
    'books',
    'papers',
    'ai_assistant',

    'theme',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AdminAccessMiddleware',  
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

TAILWIND_APP_NAME = 'theme'

INTERNAL_IPS = ["127.0.0.1"]

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# ==========================================
# STATIC, MEDIA & CLOUDINARY CONFIGURATION
# ==========================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {}
if os.getenv('CLOUDINARY_CLOUD_NAME'):
    CLOUDINARY_STORAGE['CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
if os.getenv('CLOUDINARY_API_KEY'):
    CLOUDINARY_STORAGE['API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
if os.getenv('CLOUDINARY_API_SECRET'):
    CLOUDINARY_STORAGE['API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')

# ==========================================
# SUPABASE STORAGE CONFIGURATION (S3 API)
# ==========================================
AWS_ACCESS_KEY_ID = os.getenv('SUPABASE_AWS_ACCESS_KEY_ID') or os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('SUPABASE_AWS_SECRET_ACCESS_KEY') or os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('SUPABASE_STORAGE_BUCKET_NAME') or os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('SUPABASE_S3_ENDPOINT_URL') or os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False 

USE_SUPABASE_STORAGE = all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL])

# Dynamically construct the Public CDN Custom Domain if using Supabase
if USE_SUPABASE_STORAGE:
    # Strips "https://" and "/storage/v1/s3" out to isolate clean project domain string
    _clean_domain = AWS_S3_ENDPOINT_URL.replace('https://', '').replace('http://', '').split('/storage/v1/s3')[0]
    AWS_S3_CUSTOM_DOMAIN = f"{_clean_domain}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

# Environment-aware storage configuration logic
IS_PYTHONANYWHERE = 'pythonanywhere' in os.environ.get('HOME', '')

if USE_SUPABASE_STORAGE:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' if IS_PYTHONANYWHERE else 'whitenoise.storage.CompressedStaticFilesStorage'
    
    STORAGES = {
        'default': {
            'BACKEND': DEFAULT_FILE_STORAGE,
        },
        'staticfiles': {
            'BACKEND': STATICFILES_STORAGE,
        },
    }
elif IS_PYTHONANYWHERE:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage' if USE_CLOUDINARY else 'django.core.files.storage.FileSystemStorage'
    
    STORAGES = {
        'default': {
            'BACKEND': DEFAULT_FILE_STORAGE,
        },
        'staticfiles': {
            'BACKEND': STATICFILES_STORAGE,
        },
    }
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage' if USE_CLOUDINARY else 'django.core.files.storage.FileSystemStorage'
    
    STORAGES = {
        'default': {
            'BACKEND': DEFAULT_FILE_STORAGE,
        },
        'staticfiles': {
            'BACKEND': STATICFILES_STORAGE,
        },
    }

# ==========================================
# SECURITY & AUTHENTICATION SETTINGS
# ==========================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True