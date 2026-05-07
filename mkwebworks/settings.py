import os
import dj_database_url
from pathlib import Path

# 1. PATHS
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-co-cmmm6pf7do9j*sniaukj3p3w&hm21(f(p4o(q=g!w=bmfsw')

# DEBUG este False în producție, True doar dacă ești pe localhost
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['mkwebworks.onrender.com', '127.0.0.1', 'localhost', '.onrender.com']

# 3. APPLICATION DEFINITION
INSTALLED_APPS = [
    'main',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mkwebworks.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'main/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.language_choices', 
            ],
        },
    },
]

WSGI_APPLICATION = 'mkwebworks.wsgi.application'

# 4. DATABASE
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# 5. AUTHENTICATION & VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 6. INTERNATIONALIZATION
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
    ('uk', 'Украînська'),
    ('ro', 'Română'),
    ('cs', 'Čeština'),
]

LOCALE_PATHS = [
    BASE_DIR / 'main' / 'locale',
]

# 7. STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), os.path.join(BASE_DIR, 'main', 'static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# 8. EMAIL SETTINGS - CORECTAT
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kristianmaryna13@gmail.com'
# Am scos os.environ.get pentru că parola era scrisă direct acolo
EMAIL_HOST_PASSWORD = 'ibln kmpa xmcu kiqu' 
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 9. CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 10. SECURITY EXTRAS
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = ["https://mkwebworks.onrender.com", "https://*.onrender.com"]