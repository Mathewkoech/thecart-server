from .base import *
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),

    }
}

# Replace the SQLite DATABASES configuration with PostgreSQL:
# DATABASES = {
#     'default': dj_database_url.config(
#         conn_max_age=600,
#         default=f'postgresql://{config("POSTGRES_USER")}'
#                 f':{config("POSTGRES_PASSWORD")}'
#                 f'@{config("POSTGRES_HOST")}'
#                 f':{config("DB_PORT")}/{config("POSTGRES_DB")}'
#     )
# }

# Use config for other settings as needed
SECRET_KEY = config('SECRET_KEY')


# Email BackEnd
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'