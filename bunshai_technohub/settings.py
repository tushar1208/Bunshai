# bunshai_technohub/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-insecure-key-change-me-in-production')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

DEBUG = os.getenv('DEBUG', 'True') == 'True'
if DEBUG:
    ALLOWED_HOSTS.extend(['*'])

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',') if o.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    _render_origin = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'corsheaders',
    
    # Local
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'bunshai_technohub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'bunshai_technohub.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Persist form-rate-limit/captcha state across requests
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Security Headers (production only)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'


# Email settings (credentials come from .env, never hard-code them)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'team.bunshailogicloop@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
_has_real_smtp = bool(EMAIL_HOST_PASSWORD) and 'your-app-password' not in EMAIL_HOST_PASSWORD
# Without real SMTP credentials, emails are printed to the console instead of failing.
EMAIL_BACKEND = ('django.core.mail.backends.smtp.EmailBackend' if _has_real_smtp
                 else 'django.core.mail.backends.console.EmailBackend')
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
CONTACT_EMAIL = "contact@bunshaitechnohub.com"
SUPPORT_EMAIL = "support@bunshaitechnohub.com"
INFO_EMAIL = "info@bunshaitechnohub.com"
ADMIN_EMAIL = "admin@bunshaitechnohub.com"

# Google Sheets Settings
GOOGLE_SHEETS_CREDENTIALS = BASE_DIR / 'google_credentials.json'
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')
# Alternative to the credentials file: paste the service-account JSON into this env var
GOOGLE_SHEETS_JSON = os.getenv('GOOGLE_SHEETS_JSON', '')

# ===== SITE CUSTOM SETTINGS =====
SITE_NAME = "BunShai TECHNOHUB"
SITE_DESCRIPTION = "Your trusted technology partner for digital transformation"
SITE_KEYWORDS = "IT Consulting, Software Development, Digital Marketing, Cloud Solutions"
SITE_AUTHOR = "BunShai TECHNOHUB Team"
SITE_URL = os.getenv(
    'SITE_URL',
    f'https://{RENDER_EXTERNAL_HOSTNAME}' if RENDER_EXTERNAL_HOSTNAME else 'http://127.0.0.1:8000',
)

# Contact Information
SITE_EMAIL = "team.bunshailogicloop@gmail.com"
SITE_PHONE = "+91 8091401208"
SITE_ADDRESS = "Global / Remote-first Company"
SITE_COUNTRY = "India"

# Social Media
SITE_FACEBOOK = "https://www.facebook.com/share/1DFuBTBXN2/"
SITE_YOUTUBE = "https://www.youtube.com/@Bun_Shai"
SITE_LINKEDIN = "https://www.linkedin.com/company/bunshai-technohub"
SITE_TWITTER = "https://twitter.com"
SITE_INSTAGRAM = "https://instagram.com"

# Business Info
BUSINESS_HOURS_START = "9:00 AM"
BUSINESS_HOURS_END = "6:00 PM"
BUSINESS_DAYS = "Monday to Friday"
EMERGENCY_CONTACT = "+91 8091401208"

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if RENDER_EXTERNAL_HOSTNAME:
    _render_cors = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if _render_cors not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(_render_cors)

# WhatsApp Cloud API Automation Settings
WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'True') == 'True'
WHATSAPP_DRY_RUN = os.getenv('WHATSAPP_DRY_RUN', 'True') == 'True'
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v21.0').strip()
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '').strip()
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '').strip()
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'bunshai-whatsapp-verify-token').strip()
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET', '').strip()
WHATSAPP_ADMIN_PHONE = os.getenv('WHATSAPP_ADMIN_PHONE', '918091401208').strip()
WHATSAPP_DEFAULT_COUNTRY_CODE = os.getenv('WHATSAPP_DEFAULT_COUNTRY_CODE', '91').strip()
WHATSAPP_AUTO_NOTIFY_USERS = os.getenv('WHATSAPP_AUTO_NOTIFY_USERS', 'True') == 'True'
WHATSAPP_AUTO_NOTIFY_TEAM = os.getenv('WHATSAPP_AUTO_NOTIFY_TEAM', 'True') == 'True'
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY', '').strip()
