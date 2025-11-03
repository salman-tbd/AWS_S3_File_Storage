"""
AWS S3 Storage Backend Module
Single region configuration for Mumbai, India
"""

from storages.backends.s3boto3 import S3Boto3Storage
from decouple import config


class MediaStorage(S3Boto3Storage):
    """
    S3 Storage for Mumbai region (ap-south-1)
    Use for all client documents
    """
    bucket_name = config('AWS_STORAGE_BUCKET_NAME', default='evol-assistant-docs')
    region_name = config('AWS_S3_REGION_NAME', default='ap-south-1')
    encryption = config('AWS_S3_ENCRYPTION', default='AES256')
    file_overwrite = False
    default_acl = None  # Private by default
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    
    def __init__(self, **settings):
        super().__init__(**settings)
        self.location = 'documents'  # Folder prefix in S3


class ProcessedDataStorage(S3Boto3Storage):
    """
    Storage for AI-processed data (OCR results, extracted metadata)
    Uses same bucket with different folder
    """
    bucket_name = config('AWS_STORAGE_BUCKET_NAME', default='evol-assistant-docs')
    region_name = config('AWS_S3_REGION_NAME', default='ap-south-1')
    file_overwrite = True  # Allow overwriting processed files
    default_acl = None
    
    def __init__(self, **settings):
        super().__init__(**settings)
        self.location = 'processed'  # Separate folder for processed data


def get_storage_backend():
    """
    Factory function to get storage backend
    
    Returns:
        S3Boto3Storage: Configured storage backend for Mumbai region
    """
    return MediaStorage()

