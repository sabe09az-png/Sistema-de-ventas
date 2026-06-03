from .settings import *
import os
import dj_database_url

DEBUG = True  # Déjalo True por ahora para ver errores
ALLOWED_HOSTS = ['*']

# Configuración de base de datos
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('POSTGRESQL_ADDON_URI'))
}

# ========== ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES) ==========
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'juegos/static'),  # Tus archivos estáticos de la app juegos
    os.path.join(BASE_DIR, 'theme/static'), 
]

# ========== ARCHIVOS MEDIA (IMÁGENES SUBIDAS POR USUARIOS) ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== MIDDLEWARE CON WHITENOISE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Necesario para servir estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========== STORAGE PARA COMPRIMIR ESTÁTICOS ==========
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========== SEGURIDAD ==========
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

# ========== TEMPLATES ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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