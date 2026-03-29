"""
Django settings for pyme_ledger_pos project.
Configuración profesional organizada por módulos.
"""
import os
from pathlib import Path

# --- 1. CONFIGURACIÓN DE RUTAS (BASE) ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. SEGURIDAD ---
# Nota: En producción, estas deben cargarse desde variables de entorno (.env)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-mvp-secret-key-pyme-ledger-2026')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# --- 3. DEFINICIÓN DE APLICACIONES ---
CORE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
]

LOCAL_APPS = [
    'ledger_api',
]

INSTALLED_APPS = CORE_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- 4. MIDDLEWARE ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 5. CONFIGURACIÓN DE URLS Y WSGI ---
ROOT_URLCONF = 'pyme_ledger_pos.urls'
WSGI_APPLICATION = 'pyme_ledger_pos.wsgi.application'

# --- 6. TEMPLATES ---
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
            ],
        },
    },
]

# --- 7. BASE DE DATOS (ADMINISTRACIÓN) ---
# El motor principal es Beancount, pero Django requiere SQLite para auth/admin.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- 8. INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- 9. ARCHIVOS ESTÁTICOS ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# --- 10. CONFIGURACIÓN DE REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # Cambiar a IsAuthenticated para prod
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# --- 11. CORS ---
CORS_ALLOW_ALL_ORIGINS = True # Restringir en producción
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
