"""
Django Settings Configuration for S3 Storage
Add these settings to your main Django project's settings.py
"""

from decouple import config
import os

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')

# Australia Region Bucket
AWS_STORAGE_BUCKET_NAME_AU = config('AWS_STORAGE_BUCKET_NAME_AU', default='evol-assistant-docs-au')
AWS_S3_REGION_NAME_AU = config('AWS_S3_REGION_NAME_AU', default='ap-southeast-2')

# India Region Bucket
AWS_STORAGE_BUCKET_NAME_IN = config('AWS_STORAGE_BUCKET_NAME_IN', default='evol-assistant-docs-in')
AWS_S3_REGION_NAME_IN = config('AWS_S3_REGION_NAME_IN', default='ap-south-1')

# S3 Settings
AWS_S3_ENCRYPTION = config('AWS_S3_ENCRYPTION', default='AES256')
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = None  # Private by default
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600  # Presigned URL expiration (1 hour)

# File Upload Settings
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=52428800, cast=int)  # 50MB
ALLOWED_DOCUMENT_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/s3_storage.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        's3_storage': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Add 's3_storage' to INSTALLED_APPS
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',
    'corsheaders',
    'storages',
    's3_storage',
]

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

