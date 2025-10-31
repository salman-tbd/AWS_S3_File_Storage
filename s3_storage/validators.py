"""
File Validators for Document Uploads
"""

import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decouple import config


# Allowed file types
ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': ['.pdf'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}

MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=52428800, cast=int)  # 50MB


def validate_file_size(file):
    """
    Validate file size is within limits
    """
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            _('File size exceeds maximum allowed size of %(max_size)sMB'),
            params={'max_size': MAX_UPLOAD_SIZE / (1024 * 1024)},
        )


def validate_file_type(file):
    """
    Validate file type using python-magic (checks actual file content, not just extension)
    """
    # Read first chunk to determine file type
    file.seek(0)
    file_head = file.read(2048)
    file.seek(0)
    
    # Detect MIME type
    mime = magic.from_buffer(file_head, mime=True)
    
    if mime not in ALLOWED_DOCUMENT_TYPES:
        raise ValidationError(
            _('File type "%(mime)s" is not allowed. Allowed types: %(allowed)s'),
            params={
                'mime': mime,
                'allowed': ', '.join(ALLOWED_DOCUMENT_TYPES.keys())
            },
        )


def validate_filename(filename):
    """
    Validate filename doesn't contain dangerous characters
    """
    dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    
    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(
                _('Filename contains invalid character: %(char)s'),
                params={'char': char},
            )
    
    if not filename or filename.startswith('.'):
        raise ValidationError(_('Invalid filename'))


def sanitize_filename(filename):
    """
    Sanitize filename by removing/replacing dangerous characters
    """
    import re
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove any characters that aren't alphanumeric, underscore, hyphen, or period
    filename = re.sub(r'[^\w\-.]', '', filename)
    
    # Ensure filename doesn't start with a period
    if filename.startswith('.'):
        filename = 'file' + filename
    
    return filename

