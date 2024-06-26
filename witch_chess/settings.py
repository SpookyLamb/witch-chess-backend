"""
Django settings for witch_chess project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os

APP_NAME = os.getenv("FLY_APP_NAME", None)
DATABASE_PATH = os.getenv("DATABASE_PATH", None)
CSRF_TRUSTED_ORIGINS = [f"https://{APP_NAME}.fly.dev"]

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-gh=ukkizt2-+0#(t_u4d9yekp4p320x7-b^f)@e0w#@wf%msi+') #this is only used in local dev

ALLOWED_HOSTS = ['127.0.0.1', 'http://localhost:8080', f"{APP_NAME}.fly.dev", 'https://witch-chess.vercel.app']

ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

DEBUG = False
if ENVIRONMENT == 'local':
    DEBUG = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'rest_framework',
    'witch_chess_app',
]

#sockets

ASGI_APPLICATION = "witch_chess.asgi.application"

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from witch_chess_app.consumers import MatchConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path('ws/match/', MatchConsumer.as_asgi()),
    ]),
})

#middleware

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #necessary for deployment
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'https://witch-chess.vercel.app',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'Content-Type',
    'Authorization',
    'authentication',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
      'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

ROOT_URLCONF = 'witch_chess.urls'

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

WSGI_APPLICATION = 'witch_chess.wsgi.application'

#REDIS

from urllib.parse import urlparse
# code from https://stackoverflow.com/questions/62777377/long-url-including-a-key-causes-unicode-idna-codec-decoding-error-whilst-using

def parse_redis_url(url):
    """ parses a redis url into component parts, stripping password from the host.
    Long keys in the url result in parsing errors, since labels within a hostname cannot exceed 64 characters under
    idna rules.
    In that event, we remove the key/password so that it can be passed separately to the RedisChannelLayer.
    """
    parsed = urlparse(url)
    parts = parsed.netloc.split(':')
    host = ':'.join(parts[0:-1])
    port = parts[-1]
    path = parsed.path.split('/')[1:]
    db = int(path[0]) if len(path) >= 1 else 0

    user, password = (None, None)
    if '@' in host:
        creds, host = host.split('@')
        user, password = creds.split(':')
        host = f'{user}@{host}'

    return host, port, user, password, db

REDIS_URL = os.environ.get('REDIS_URL', default='redis://localhost:6379')
REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, REDIS_DB = parse_redis_url(REDIS_URL)

CHANNEL_LAYERS = { #production
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                'address': f'redis://{REDIS_HOST}:{REDIS_PORT}',
                'db': REDIS_DB,
                'password': REDIS_PASSWORD,
            }],
        },
    },
}

# CHANNEL_LAYERS = { #local
#     'default': {
#         'BACKEND': "channels.layers.InMemoryChannelLayer"
#     }
# }

# CHANNEL_LAYERS = { #local, with redis and docker
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = { #local
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = { #production
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH if APP_NAME else BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#deployment:

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    'default': {
        'BACKEND': "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}