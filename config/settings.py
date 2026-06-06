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

# =========================================================
# VERCEL BUILD & FORMATTING SHIELD
# =========================================================
_cloud_url = os.environ.get('CLOUDINARY_URL', '')


def get_env_value(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ImproperlyConfigured(f"The {name} environment variable is required.")
    return value


# Quick-start development settings
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-vercel-build-fallback')
else:
    SECRET_KEY = get_env_value('SECRET_KEY', required=True)

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Use Cloudinary if CLOUDINARY_URL is configured AND we are in production/Vercel (or explicitly enabled)
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


# Application definition
INSTALLED_APPS = [
    'cloudinary_storage', 
    'cloudinary',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_build' / 'static'

TAILWIND_APP_NAME = 'theme'

INTERNAL_IPS = ["127.0.0.1"]

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ==========================================
# MEDIA & CLOUDINARY CONFIGURATION
# ==========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {}
if os.getenv('CLOUDINARY_CLOUD_NAME'):
    CLOUDINARY_STORAGE['CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
if os.getenv('CLOUDINARY_API_KEY'):
    CLOUDINARY_STORAGE['API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
if os.getenv('CLOUDINARY_API_SECRET'):
    CLOUDINARY_STORAGE['API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')

# Explicitly defining legacy settings to stop AttributeError
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
if USE_CLOUDINARY:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {
                'location': MEDIA_ROOT,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'