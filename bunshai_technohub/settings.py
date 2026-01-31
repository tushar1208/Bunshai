# bunshai_technohub/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
# Your existing line
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Add this for testing (temporarily)
DEBUG = os.getenv('DEBUG', 'True') == 'True'
if DEBUG:
    # Add common tunnel domains for testing
    ALLOWED_HOSTS.extend([
       '*'
    ])
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'django_recaptcha',
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
        conn_max_age=600
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
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Headers (production only)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# reCAPTCHA Settings - For django-recaptcha package
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6Lf95TUsAAAAAHJ3XDyKOxnWRuKXga5KMMbFlhCt')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6Lf95TUsAAAAAIUjmT_m8AqPjCfty1t4kyn52m-p')
RECAPTCHA_DOMAIN = 'www.recaptcha.net'
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']  # FIXED: Changed 'captcha.' to 'django_recaptcha.'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'team.bunshailogicloop@gmail.com'
EMAIL_HOST_PASSWORD = 'BunShai@4403'
DEFAULT_FROM_EMAIL = "noreply@bunshaitechnohub.com"
CONTACT_EMAIL = "contact@bunshaitechnohub.com"
SUPPORT_EMAIL = "support@bunshaitechnohub.com"
INFO_EMAIL = "info@bunshaitechnohub.com"
ADMIN_EMAIL = "admin@bunshaitechnohub.com"

# Google Sheets Settings
GOOGLE_SHEETS_CREDENTIALS = BASE_DIR / 'google_credentials.json'
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')

# ===== SITE CUSTOM SETTINGS =====
SITE_NAME = "BunShai TECHNOHUB"
SITE_DESCRIPTION = "Your trusted technology partner for digital transformation"
SITE_KEYWORDS = "IT Consulting, Software Development, Digital Marketing, Cloud Solutions"
SITE_AUTHOR = "BunShai TECHNOHUB Team"
SITE_URL = "http://127.0.0.1:8000"

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