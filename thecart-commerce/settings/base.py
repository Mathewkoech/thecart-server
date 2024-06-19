from pathlib import Path
from decouple import config, Csv
import datetime
import os


BASE_DIR = Path(__file__).resolve().parent.parent


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = config("SITE_ID", cast=int)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="127.0.0.1")

print(ALLOWED_HOSTS)
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    'rest_framework.authtoken',
    'dj_rest_auth',
    "allauth",
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'rest_framework_simplejwt',
]

LOCAL_APPS = [
    'thecart_auth.apps.ThecartAuthConfig',
    'ordering.apps.OrderingConfig',
    'products.apps.ProductsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Make sure this line is present
]

ROOT_URLCONF = 'thecart-commerce.urls'

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

AUTH_USER_MODEL = 'thecart_auth.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('PAGE_SIZE', cast=int, default=10),
    'COERCE_DECIMAL_TO_STRING': False,
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

ACCOUNT_ADAPTER = 'thecart_auth.adapter.CustomAccountAdapter'
REST_USE_JWT = True
OLD_PASSWORD_FIELD_ENABLED = False
ACCOUNT_ADAPTER = 'thecart_auth.adapter.CustomAccountAdapter'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'optional'


dj_rest_auth_SERIALIZERS = {
    'PASSWORD_RESET_SERIALIZER': 'thecart_auth.serializers.CustomPasswordResetSerializer',
    'JWT_SERIALIZER': 'thecart_auth.serializers.CustomJWTSerializer',
    'USER_DETAILS_SERIALIZER': 'thecart_auth.serializers.UserSerializer',
}

dj_rest_auth_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'thecart_auth.serializers.CustomRegisterSerializer'
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
