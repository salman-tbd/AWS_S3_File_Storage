"""
Celery Tasks for Async Document Processing
"""

from celery import shared_task, group
from django.utils import timezone
import logging
import boto3
from botocore.exceptions import ClientError
from decouple import config

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id):
    """
    Process uploaded document with AI
    - Extract text (OCR)
    - Classify document type
    - Extract key information
    - Validate completeness
    
    Args:
        document_id (str): UUID of document to process
    """
    from .models import Document
    
    try:
        document = Document.objects.get(id=document_id)
        logger.info(f"Processing document: {document_id}")
        
        # Mark as processing
        document.mark_as_processing()
        
        # Download from S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=document.s3_region
        )
        
        response = s3_client.get_object(
            Bucket=document.s3_bucket,
            Key=document.s3_key
        )
        file_content = response['Body'].read()
        
        # Process based on document type
        extracted_data = {}
        ocr_text = None
        
        if document.document_type in ['passport', 'photo', 'birth_certificate']:
            extracted_data, ocr_text = process_identity_document(file_content, document.file_type)
        
        elif document.document_type in ['bank_statement', 'tax_return', 'financial_proof']:
            extracted_data, ocr_text = process_financial_document(file_content, document.file_type)
        
        elif document.document_type in ['degree', 'transcript', 'english_test']:
            extracted_data, ocr_text = process_educational_document(file_content, document.file_type)
        
        elif document.document_type in ['employment_letter', 'payslip', 'resume']:
            extracted_data, ocr_text = process_employment_document(file_content, document.file_type)
        
        else:
            # Generic processing
            extracted_data, ocr_text = process_generic_document(file_content, document.file_type)
        
        # Mark as processed
        document.mark_as_processed(
            extracted_data=extracted_data,
            ocr_text=ocr_text
        )
        
        logger.info(f"Document processed successfully: {document_id}")
        
        # Send notification
        notify_case_officer.delay(document_id)
        
        return {
            'status': 'success',
            'document_id': str(document_id),
            'extracted_data': extracted_data
        }
    
    except Document.DoesNotExist:
        logger.error(f"Document not found: {document_id}")
        return {'status': 'error', 'message': 'Document not found'}
    
    except ClientError as e:
        logger.error(f"S3 error processing document {document_id}: {e}")
        # Retry on S3 errors
        raise self.retry(exc=e, countdown=60)
    
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        
        # Mark as failed
        try:
            document.status = 'uploaded'  # Reset to uploaded
            document.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}


def process_identity_document(file_content, file_type):
    """
    Process identity documents (passport, birth certificate, etc.)
    Extract: name, date of birth, passport number, expiry date, nationality
    """
    extracted_data = {
        'document_category': 'identity',
        'processed_at': timezone.now().isoformat()
    }
    ocr_text = None
    
    # TODO: Implement actual OCR/AI processing
    # Options:
    # 1. AWS Textract
    # 2. Tesseract OCR
    # 3. Google Cloud Vision
    # 4. Azure Computer Vision
    
    # Placeholder implementation
    if file_type == 'application/pdf':
        ocr_text = extract_text_from_pdf(file_content)
    elif file_type in ['image/jpeg', 'image/png']:
        ocr_text = extract_text_from_image(file_content)
    
    # Extract key information (example)
    if ocr_text:
        extracted_data.update({
            'text_length': len(ocr_text),
            'has_text': True,
            # Add more extraction logic here
        })
    
    return extracted_data, ocr_text


def process_financial_document(file_content, file_type):
    """
    Process financial documents
    Extract: account balance, transactions, dates, currency
    """
    extracted_data = {
        'document_category': 'financial',
        'processed_at': timezone.now().isoformat()
    }
    ocr_text = None
    
    if file_type == 'application/pdf':
        ocr_text = extract_text_from_pdf(file_content)
    
    # Extract financial data
    # TODO: Implement financial data extraction
    
    return extracted_data, ocr_text


def process_educational_document(file_content, file_type):
    """
    Process educational documents
    Extract: institution name, degree, GPA, graduation date
    """
    extracted_data = {
        'document_category': 'educational',
        'processed_at': timezone.now().isoformat()
    }
    ocr_text = None
    
    if file_type == 'application/pdf':
        ocr_text = extract_text_from_pdf(file_content)
    
    # Extract educational data
    # TODO: Implement educational data extraction
    
    return extracted_data, ocr_text


def process_employment_document(file_content, file_type):
    """
    Process employment documents
    Extract: employer name, position, salary, dates
    """
    extracted_data = {
        'document_category': 'employment',
        'processed_at': timezone.now().isoformat()
    }
    ocr_text = None
    
    if file_type == 'application/pdf':
        ocr_text = extract_text_from_pdf(file_content)
    
    # Extract employment data
    # TODO: Implement employment data extraction
    
    return extracted_data, ocr_text


def process_generic_document(file_content, file_type):
    """
    Generic document processing
    """
    extracted_data = {
        'document_category': 'generic',
        'processed_at': timezone.now().isoformat()
    }
    ocr_text = None
    
    if file_type == 'application/pdf':
        ocr_text = extract_text_from_pdf(file_content)
    elif file_type in ['image/jpeg', 'image/png']:
        ocr_text = extract_text_from_image(file_content)
    
    return extracted_data, ocr_text


def extract_text_from_pdf(file_content):
    """
    Extract text from PDF using PyPDF2
    """
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None


def extract_text_from_image(file_content):
    """
    Extract text from image using OCR (Tesseract)
    Note: Requires pytesseract and tesseract-ocr installation
    """
    try:
        # Option 1: Using Tesseract (local)
        # import pytesseract
        # from PIL import Image
        # from io import BytesIO
        # 
        # image = Image.open(BytesIO(file_content))
        # text = pytesseract.image_to_string(image)
        # return text
        
        # Option 2: Using AWS Textract (cloud)
        # textract = boto3.client('textract', region_name='ap-southeast-2')
        # response = textract.detect_document_text(
        #     Document={'Bytes': file_content}
        # )
        # text = ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
        # return text
        
        # Placeholder
        return "OCR text extraction not implemented yet"
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return None


@shared_task
def process_bulk_documents(document_ids):
    """
    Process multiple documents in parallel
    
    Args:
        document_ids (list): List of document UUIDs
    """
    logger.info(f"Processing {len(document_ids)} documents in bulk")
    
    # Create group of tasks
    job = group(process_document.s(doc_id) for doc_id in document_ids)
    result = job.apply_async()
    
    return {
        'status': 'queued',
        'document_count': len(document_ids),
        'task_id': result.id
    }


@shared_task
def notify_case_officer(document_id):
    """
    Notify case officer that document is processed
    
    Args:
        document_id (str): Document UUID
    """
    from .models import Document
    
    try:
        document = Document.objects.get(id=document_id)
        
        if document.client.assigned_to:
            officer = document.client.assigned_to
            
            # TODO: Implement notification
            # Options:
            # 1. Send email
            # 2. Push notification
            # 3. In-app notification
            # 4. Slack/Teams webhook
            
            logger.info(f"Notification sent to {officer.email} for document {document_id}")
            
            return {'status': 'notified', 'recipient': officer.email}
        
        return {'status': 'no_assignment'}
    
    except Document.DoesNotExist:
        logger.error(f"Document not found: {document_id}")
        return {'status': 'error', 'message': 'Document not found'}


@shared_task
def archive_old_documents():
    """
    Periodic task to archive completed cases to Glacier
    Run this as a scheduled task (e.g., daily)
    """
    from .models import Document, Client
    from .utils import copy_to_archive
    from datetime import timedelta
    
    # Find completed cases older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_clients = Client.objects.filter(
        status='completed',
        updated_at__lt=cutoff_date
    )
    
    archived_count = 0
    
    for client in old_clients:
        documents = client.documents.all()
        
        for document in documents:
            if document.s3_bucket and document.s3_key:
                # Copy to archive bucket with Glacier storage class
                archive_key = f"archive/{client.id}/{document.s3_key}"
                
                success = copy_to_archive(
                    source_bucket=document.s3_bucket,
                    source_key=document.s3_key,
                    archive_bucket=document.s3_bucket,  # Same bucket, different prefix
                    archive_key=archive_key,
                    region=document.s3_region
                )
                
                if success:
                    archived_count += 1
    
    logger.info(f"Archived {archived_count} documents")
    
    return {
        'status': 'completed',
        'archived_count': archived_count
    }


@shared_task
def cleanup_temp_files():
    """
    Periodic task to clean up temporary/failed uploads
    """
    from .models import Document
    from .utils import delete_s3_file
    from datetime import timedelta
    
    # Find documents stuck in processing for more than 1 hour
    cutoff_time = timezone.now() - timedelta(hours=1)
    
    stuck_documents = Document.objects.filter(
        status='processing',
        updated_at__lt=cutoff_time
    )
    
    for document in stuck_documents:
        # Reset status
        document.status = 'uploaded'
        document.save()
    
    logger.info(f"Reset {stuck_documents.count()} stuck documents")
    
    return {
        'status': 'completed',
        'reset_count': stuck_documents.count()
    }

