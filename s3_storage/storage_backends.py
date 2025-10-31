"""
AWS S3 Storage Backend Module
Multi-region support for Australia and India
"""

from storages.backends.s3boto3 import S3Boto3Storage
from decouple import config


class AustraliaMediaStorage(S3Boto3Storage):
    """
    S3 Storage for Australian region (Sydney: ap-southeast-2)
    Use for Australian client documents
    """
    bucket_name = config('AWS_STORAGE_BUCKET_NAME_AU', default='migration-zone-docs-au')
    region_name = config('AWS_S3_REGION_NAME_AU', default='ap-southeast-2')
    encryption = config('AWS_S3_ENCRYPTION', default='AES256')
    file_overwrite = False
    default_acl = None  # Private by default
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    
    def __init__(self, **settings):
        super().__init__(**settings)
        self.location = 'documents/au'  # Folder prefix in S3


class IndiaMediaStorage(S3Boto3Storage):
    """
    S3 Storage for India region (Mumbai: ap-south-1)
    Use for Indian client documents
    """
    bucket_name = config('AWS_STORAGE_BUCKET_NAME_IN', default='migration-zone-docs-in')
    region_name = config('AWS_S3_REGION_NAME_IN', default='ap-south-1')
    encryption = config('AWS_S3_ENCRYPTION', default='AES256')
    file_overwrite = False
    default_acl = None
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    
    def __init__(self, **settings):
        super().__init__(**settings)
        self.location = 'documents/in'


class ProcessedDataStorage(S3Boto3Storage):
    """
    Storage for AI-processed data (OCR results, extracted metadata)
    Can use cheaper region or same as primary
    """
    bucket_name = config('AWS_STORAGE_BUCKET_NAME_AU', default='migration-zone-docs-au')
    region_name = config('AWS_S3_REGION_NAME_AU', default='ap-southeast-2')
    file_overwrite = True  # Allow overwriting processed files
    default_acl = None
    
    def __init__(self, **settings):
        super().__init__(**settings)
        self.location = 'processed'  # Separate folder for processed data


def get_storage_backend(region='au'):
    """
    Factory function to get appropriate storage backend
    
    Args:
        region (str): 'au' for Australia, 'in' for India
        
    Returns:
        S3Boto3Storage: Configured storage backend
    """
    if region.lower() == 'in':
        return IndiaMediaStorage()
    return AustraliaMediaStorage()

