"""
Utility functions for S3 storage operations
"""

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from decouple import config
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_presigned_url(bucket_name, object_key, expiration=3600, region='ap-southeast-2'):
    """
    Generate a presigned URL for secure file download
    
    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key (file path)
        expiration (int): URL expiration time in seconds (default: 1 hour)
        region (str): AWS region
        
    Returns:
        str: Presigned URL or None if error
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
        
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None


def generate_upload_presigned_url(bucket_name, object_key, expiration=3600, region='ap-southeast-2'):
    """
    Generate a presigned URL for direct upload from client
    
    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key (file path)
        expiration (int): URL expiration time in seconds
        region (str): AWS region
        
    Returns:
        dict: Presigned POST data or None if error
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_key,
            ExpiresIn=expiration
        )
        
        return response
    except ClientError as e:
        logger.error(f"Error generating presigned upload URL: {e}")
        return None


def delete_s3_file(bucket_name, object_key, region='ap-southeast-2'):
    """
    Delete a file from S3
    
    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key (file path)
        region (str): AWS region
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"Deleted file: {object_key} from bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting file from S3: {e}")
        return False


def get_file_metadata(bucket_name, object_key, region='ap-southeast-2'):
    """
    Get file metadata from S3
    
    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key (file path)
        region (str): AWS region
        
    Returns:
        dict: File metadata or None if error
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        return {
            'size': response.get('ContentLength'),
            'last_modified': response.get('LastModified'),
            'content_type': response.get('ContentType'),
            'etag': response.get('ETag'),
        }
    except ClientError as e:
        logger.error(f"Error getting file metadata: {e}")
        return None


def organize_document_path(client_id, document_type, filename):
    """
    Generate organized S3 path for documents
    
    Args:
        client_id (int): Client ID
        document_type (str): Document type (passport, financial, etc.)
        filename (str): Original filename
        
    Returns:
        str: Organized S3 path
    """
    from .validators import sanitize_filename
    
    safe_filename = sanitize_filename(filename)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    return f"clients/{client_id}/{document_type}/{timestamp}_{safe_filename}"


def copy_to_archive(source_bucket, source_key, archive_bucket, archive_key, region='ap-southeast-2'):
    """
    Copy file to archive bucket (for completed cases)
    
    Args:
        source_bucket (str): Source bucket name
        source_key (str): Source object key
        archive_bucket (str): Archive bucket name
        archive_key (str): Archive object key
        region (str): AWS region
        
    Returns:
        bool: True if successful
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=archive_bucket,
            Key=archive_key,
            StorageClass='GLACIER_IR'  # Use Glacier Instant Retrieval for archives
        )
        
        logger.info(f"Archived file: {source_key} to {archive_key}")
        return True
    except ClientError as e:
        logger.error(f"Error archiving file: {e}")
        return False

