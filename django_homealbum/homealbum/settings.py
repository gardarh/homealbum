"""
Django settings for homealbum project.

See README.md at root of project for instructions on how this settings file
should be augmented.
"""

import os

HOMEALBUM_VERSION = '0.9.0'
HOMEALBUM_BUILDNO = int(open('HOMEALBUM_BUILDNO', 'r').read()) if os.path.isfile('HOMEALBUM_BUILDNO') else 0


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('HOMEALBUM_DEBUG', 'n').lower() == 'y'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'homealbum.urls'

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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'core.api_auth.IsAuthenticatedObjectOwner'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

WSGI_APPLICATION = 'homealbum.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = "/admin/login/"

# Static files (CSS, JavaScript, Images - NOTE: not application photos/thumbs, just icons, etc.)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# SECURITY WARNING: keep the secret key used in production secret!
# Generate key with
# import string, random
# SECRET_KEY = ''.join([random.SystemRandom().choice((string.ascii_letters + string.digits + string.punctuation).replace("'",'')) for i in range(50)])
SECRET_KEY = os.getenv('HOMEALBUM_SECRET_KEY')
PHOTOS_BASEDIR = os.getenv('HOMEALBUM_PHOTOS_BASEDIR')
PHOTOS_THUMBS_BASEDIR = os.getenv('HOMEALBUM_THUMBS_BASEDIR')
STATIC_ROOT = os.getenv('HOMEALBUM_STATIC_FILES_DIR')
ALLOWED_HOSTS = os.getenv('HOMEALBUM_ALLOWED_HOSTS', '').split(',')