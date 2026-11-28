# bunshai_technohub/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

if not os.getenv('RENDER'):
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_host(value):
    host = (value or '').strip().lower()
    if not host or host == '*':
        return host
    if '://' in host:
        host = host.split('://', 1)[1]
    host = host.split('/', 1)[0].strip()
    if ':' in host:
        host = host.split(':', 1)[0].strip()
    return host


def _domain_variants(host):
    if not host or host == '*':
        return []
    if host.startswith('www.'):
        bare = host[4:]
        return [v for v in (bare, host) if v]
    return [host, f'www.{host}']


def _append_unique(target, item):
    if item and item not in target:
        target.append(item)


def _env_bool(name, default=False):
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-insecure-key-change-me-in-production')
RENDER_EXTERNAL_HOSTNAME = _normalize_host(os.getenv('RENDER_EXTERNAL_HOSTNAME', ''))
CUSTOM_DOMAIN = _normalize_host(os.getenv('CUSTOM_DOMAIN', '')) or (
    'bunshaitechnohub.com' if os.getenv('RENDER') else ''
)
CANONICAL_HOST = _normalize_host(os.getenv('CANONICAL_HOST', '')) or CUSTOM_DOMAIN
ENFORCE_CUSTOM_DOMAIN = _env_bool('ENFORCE_CUSTOM_DOMAIN', False)

ALLOWED_HOSTS = []
for _raw_host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','):
    _host = _normalize_host(_raw_host)
    _append_unique(ALLOWED_HOSTS, _host)

_append_unique(ALLOWED_HOSTS, RENDER_EXTERNAL_HOSTNAME)
for _variant in _domain_variants(CUSTOM_DOMAIN) + _domain_variants(CANONICAL_HOST):
    _append_unique(ALLOWED_HOSTS, _variant)

DEBUG = _env_bool('DEBUG', True)
if DEBUG:
    _append_unique(ALLOWED_HOSTS, '*')

CSRF_TRUSTED_ORIGINS = []
for _raw_origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(','):
    _append_unique(CSRF_TRUSTED_ORIGINS, _raw_origin.strip().rstrip('/'))

CORS_ALLOWED_ORIGINS = []
for _raw_origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(','):
    _append_unique(CORS_ALLOWED_ORIGINS, _raw_origin.strip().rstrip('/'))

for _host in [RENDER_EXTERNAL_HOSTNAME, *_domain_variants(CUSTOM_DOMAIN), *_domain_variants(CANONICAL_HOST), *ALLOWED_HOSTS]:
    if not _host or _host in ('localhost', '127.0.0.1', 'testserver', '*'):
        continue
    if _host.startswith('.'):
        _append_unique(CSRF_TRUSTED_ORIGINS, f'https://*{_host}')
    else:
        _origin = f'https://{_host}'
        _append_unique(CSRF_TRUSTED_ORIGINS, _origin)
        _append_unique(CORS_ALLOWED_ORIGINS, _origin)

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
    'main.middleware.CanonicalDomainMiddleware',
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
_database_url = os.getenv('DATABASE_URL', '')
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require='render.com' in _database_url,
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
WHITENOISE_MAX_AGE = 86400 if not DEBUG else 0

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
    SECURE_REDIRECT_EXEMPT = [r'^healthz/?$']
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'


# Email settings (credentials come from .env, never hard-code them)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = _env_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'team.bunshailogicloop@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
_has_real_smtp = bool(EMAIL_HOST_PASSWORD) and 'your-app-password' not in EMAIL_HOST_PASSWORD
# Without real SMTP credentials, emails are printed to the console instead of failing.
EMAIL_BACKEND = ('django.core.mail.backends.smtp.EmailBackend' if _has_real_smtp
                 else 'django.core.mail.backends.console.EmailBackend')
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", EMAIL_HOST_USER)
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", EMAIL_HOST_USER)
INFO_EMAIL = os.getenv("INFO_EMAIL", EMAIL_HOST_USER)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", EMAIL_HOST_USER)

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
_default_site_url = (
    f'https://{CANONICAL_HOST}'
    if CANONICAL_HOST
    else (f'https://{RENDER_EXTERNAL_HOSTNAME}' if RENDER_EXTERNAL_HOSTNAME else 'http://127.0.0.1:8000')
)
SITE_URL = os.getenv('SITE_URL', '').strip().rstrip('/') or _default_site_url

# Contact Information
SITE_EMAIL = "team.bunshailogicloop@gmail.com"
SITE_PHONE = "+91 8091401208"
SITE_ADDRESS = "Global / Remote-first Company"
SITE_COUNTRY = "India"

# Social Media
SITE_FACEBOOK = os.getenv("SITE_FACEBOOK", "https://www.facebook.com/share/1DFuBTBXN2/")
SITE_YOUTUBE = os.getenv("SITE_YOUTUBE", "https://www.youtube.com/@Bun_Shai")
SITE_LINKEDIN = os.getenv("SITE_LINKEDIN", "https://www.linkedin.com/company/bunshai-technohub")
SITE_TWITTER = os.getenv("SITE_TWITTER", "")
SITE_INSTAGRAM = os.getenv("SITE_INSTAGRAM", "")

# Business Info
BUSINESS_HOURS_START = "9:00 AM"
BUSINESS_HOURS_END = "6:00 PM"
BUSINESS_DAYS = "Monday to Friday"
EMERGENCY_CONTACT = "+91 8091401208"

# Logging for Render / production stdout
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# WhatsApp Cloud API Automation Settings
WHATSAPP_ENABLED = _env_bool('WHATSAPP_ENABLED', True)
WHATSAPP_DRY_RUN = _env_bool('WHATSAPP_DRY_RUN', True)
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v21.0').strip()
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '').strip()
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '').strip()
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'bunshai-whatsapp-verify-token').strip()
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET', '').strip()
WHATSAPP_ADMIN_PHONE = os.getenv('WHATSAPP_ADMIN_PHONE', '918091401208').strip()
WHATSAPP_DEFAULT_COUNTRY_CODE = os.getenv('WHATSAPP_DEFAULT_COUNTRY_CODE', '91').strip()
WHATSAPP_AUTO_NOTIFY_USERS = _env_bool('WHATSAPP_AUTO_NOTIFY_USERS', True)
WHATSAPP_AUTO_NOTIFY_TEAM = _env_bool('WHATSAPP_AUTO_NOTIFY_TEAM', True)
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY', '').strip()
