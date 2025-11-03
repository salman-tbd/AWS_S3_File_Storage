"""
S3 Storage Package for Evol Assistant CMS
"""

__version__ = '1.0.0'

from .storage_backends import (
    AustraliaMediaStorage,
    IndiaMediaStorage,
    ProcessedDataStorage,
    get_storage_backend,
)

__all__ = [
    'AustraliaMediaStorage',
    'IndiaMediaStorage',
    'ProcessedDataStorage',
    'get_storage_backend',
]

