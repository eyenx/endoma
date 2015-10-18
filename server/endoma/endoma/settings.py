"""
File: settings.py
Comment: Django general settings for EnDoMa
Project: EnDoMa
Author: Antonio Tauro
"""

# module imports
import os
# BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h=^^6m$&k0d+)0g64mzyib52gz@h!4m+-2s+n^s=ey=@h6$2*x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# installed applications
# rmeove 'admin' when in production!
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'endoma'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'endoma.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'endoma.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'endoma_db',
        'USER': 'endoma',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['ENDOMA_DB_PORT_5432_TCP_ADDR'],
        'PORT': os.environ['ENDOMA_DB_PORT_5432_TCP_PORT'],
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# DATETIME FORMAT
DATETIME_FORMAT='d. M Y, H:i'

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

# LOGIN URL

LOGIN_URL='/login/'

# external URL

EXTERNAL_URL='http://dev.endoma.co/'
