from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== SEGURIDAD ==========
SECRET_KEY = '12345' 
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# ========== APLICACIONES INSTALADAS ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'juegos',
    # 'paypal.standard.ipn',  # COMENTADO - No lo usas en este proyecto
    'crispy_forms',
    'crispy_tailwind',
]

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # COMENTADO - Para desarrollo local
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GameDrop.urls'

# ========== TEMPLATES ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Puedes eliminar esta línea si no tienes templates globales
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'juegos.context_processors.carrito_context',  # ELIMINADO - No existe más
            ],
        },
    },
]

# ========== BASE DE DATOS ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========== PAYPAL (opcional) ==========
# PAYPAL_TEST = True
# PAYPAL_RECEIVER_EMAIL = 'tu-email-paypal@negocio.com'

# ========== CRISPY FORMS ==========
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ========== ARCHIVOS ESTÁTICOS ==========
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'juegos' / 'static',
    # BASE_DIR / 'theme' / 'static',  # COMENTADO - Si no usas theme
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========== AUTENTICACIÓN ==========
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ========== CONFIGURACIÓN ADICIONAL ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Zona horaria (importante para las fechas)
TIME_ZONE = 'America/Mexico_City'
USE_TZ = True