from .settings import *
import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['*']

# Configuración de base de datos usando la variable POSTGRESQL_ADDON_URI
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('POSTGRESQL_ADDON_URI'))
}

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Seguridad
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)