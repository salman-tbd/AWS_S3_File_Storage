"""
Django Models for Document Management
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .storage_backends import AustraliaMediaStorage, IndiaMediaStorage
from .validators import validate_file_size, validate_file_type
from .utils import organize_document_path
import uuid


class Client(models.Model):
    """
    Immigration Client Model
    Note: This is a minimal model - integrate with your existing Client model
    """
    DESTINATION_CHOICES = [
        ('AU', 'Australia'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('NZ', 'New Zealand'),
        ('US', 'United States'),
    ]
    
    VISA_TYPE_CHOICES = [
        ('skilled', 'Skilled Migration'),
        ('work', 'Work Visa'),
        ('student', 'Student Visa'),
        ('family', 'Family Visa'),
        ('business', 'Business Visa'),
    ]
    
    STATUS_CHOICES = [
        ('inquiry', 'Initial Inquiry'),
        ('documents', 'Collecting Documents'),
        ('assessment', 'Skills Assessment'),
        ('submitted', 'Application Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Case Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # Immigration specific
    destination_country = models.CharField(max_length=2, choices=DESTINATION_CHOICES)
    visa_type = models.CharField(max_length=20, choices=VISA_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    
    # Region for data residency
    region = models.CharField(max_length=2, choices=[('AU', 'Australia'), ('IN', 'India')], default='AU')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Case officer assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_visa_type_display()}"
    
    def get_storage_backend(self):
        """Return appropriate storage backend based on region"""
        if self.region == 'IN':
            return IndiaMediaStorage()
        return AustraliaMediaStorage()


def client_document_path(instance, filename):
    """
    Generate organized path for client documents
    """
    return organize_document_path(
        instance.client.id,
        instance.document_type,
        filename
    )


class Document(models.Model):
    """
    Document Model for Immigration Files
    """
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('photo', 'Photograph'),
        ('birth_certificate', 'Birth Certificate'),
        ('marriage_certificate', 'Marriage Certificate'),
        
        # Financial documents
        ('bank_statement', 'Bank Statement'),
        ('tax_return', 'Tax Return'),
        ('financial_proof', 'Financial Proof'),
        
        # Educational documents
        ('degree', 'Degree Certificate'),
        ('transcript', 'Academic Transcript'),
        ('english_test', 'English Language Test'),
        
        # Employment documents
        ('employment_letter', 'Employment Letter'),
        ('payslip', 'Payslip'),
        ('resume', 'Resume/CV'),
        ('reference_letter', 'Reference Letter'),
        
        # Application documents
        ('application_form', 'Application Form'),
        ('visa_application', 'Visa Application'),
        ('police_clearance', 'Police Clearance'),
        ('medical', 'Medical Certificate'),
        
        # Other
        ('other', 'Other Document'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded'),
        ('processing', 'AI Processing'),
        ('processed', 'Processed'),
        ('verified', 'Verified by Officer'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    
    # Document details
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # File storage (stored in S3)
    file = models.FileField(
        upload_to=client_document_path,
        validators=[validate_file_size, validate_file_type],
        max_length=500
    )
    file_size = models.BigIntegerField(null=True, blank=True)  # Size in bytes
    file_type = models.CharField(max_length=100, blank=True)  # MIME type
    original_filename = models.CharField(max_length=255)
    
    # S3 metadata
    s3_bucket = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=500, blank=True)
    s3_region = models.CharField(max_length=20, blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    
    # AI processed data (JSON field)
    ai_extracted_data = models.JSONField(null=True, blank=True)
    ocr_text = models.TextField(blank=True, null=True)  # Extracted text from OCR
    
    # Verification
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Uploaded by
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['client', 'document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.client}"
    
    def save(self, *args, **kwargs):
        """Override save to capture file metadata"""
        if self.file:
            self.file_size = self.file.size
            self.original_filename = self.file.name
            
            # Set storage based on client region
            storage_backend = self.client.get_storage_backend()
            self.file.storage = storage_backend
            
            # Capture S3 metadata after upload
            if hasattr(self.file, 'name'):
                self.s3_key = self.file.name
                self.s3_bucket = storage_backend.bucket_name
                self.s3_region = storage_backend.region_name
        
        super().save(*args, **kwargs)
    
    def get_download_url(self, expiration=3600):
        """Generate presigned URL for secure download"""
        from .utils import generate_presigned_url
        
        if self.s3_bucket and self.s3_key:
            return generate_presigned_url(
                self.s3_bucket,
                self.s3_key,
                expiration=expiration,
                region=self.s3_region
            )
        return None
    
    def mark_as_processing(self):
        """Mark document as being processed"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_processed(self, extracted_data=None, ocr_text=None):
        """Mark document as processed with AI data"""
        self.status = 'processed'
        self.processed_at = timezone.now()
        if extracted_data:
            self.ai_extracted_data = extracted_data
        if ocr_text:
            self.ocr_text = ocr_text
        self.save(update_fields=['status', 'processed_at', 'ai_extracted_data', 'ocr_text', 'updated_at'])
    
    def verify(self, user, notes=None):
        """Verify document by case officer"""
        self.status = 'verified'
        self.verified_by = user
        self.verified_at = timezone.now()
        if notes:
            self.verification_notes = notes
        self.save(update_fields=['status', 'verified_by', 'verified_at', 'verification_notes', 'updated_at'])


class DocumentAccessLog(models.Model):
    """
    Audit log for document access (compliance requirement)
    """
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('upload', 'Uploaded'),
        ('delete', 'Deleted'),
        ('update', 'Updated'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', 'timestamp']),
            models.Index(fields=['user', 'action']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.document} at {self.timestamp}"

