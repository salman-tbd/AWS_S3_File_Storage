# Test cases for S3 Storage Module

import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from s3_storage.models import Client, Document, DocumentAccessLog
from unittest.mock import patch, MagicMock


class ClientModelTestCase(TestCase):
    """Test Client model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_client(self):
        """Test creating a client"""
        client = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+61412345678',
            destination_country='AU',
            visa_type='skilled',
            region='AU'
        )
        
        self.assertEqual(client.first_name, 'John')
        self.assertEqual(client.status, 'inquiry')
        self.assertEqual(str(client), 'John Doe - Skilled Migration')
    
    def test_get_storage_backend(self):
        """Test storage backend selection"""
        client_au = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+61412345678',
            destination_country='AU',
            visa_type='skilled',
            region='AU'
        )
        
        client_in = Client.objects.create(
            first_name='Priya',
            last_name='Sharma',
            email='priya@example.com',
            phone='+919876543210',
            destination_country='AU',
            visa_type='skilled',
            region='IN'
        )
        
        backend_au = client_au.get_storage_backend()
        backend_in = client_in.get_storage_backend()
        
        self.assertIn('au', backend_au.bucket_name)
        self.assertIn('in', backend_in.bucket_name)


class DocumentModelTestCase(TestCase):
    """Test Document model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+61412345678',
            destination_country='AU',
            visa_type='skilled',
            region='AU'
        )
    
    @patch('s3_storage.models.Document.file')
    def test_create_document(self, mock_file):
        """Test creating a document"""
        mock_file.size = 1024
        mock_file.name = 'passport.pdf'
        
        document = Document.objects.create(
            client=self.client,
            document_type='passport',
            title='Passport Copy',
            description='Main identification page',
            file=mock_file,
            uploaded_by=self.user
        )
        
        self.assertEqual(document.title, 'Passport Copy')
        self.assertEqual(document.status, 'uploaded')
        self.assertEqual(document.client, self.client)
    
    def test_mark_as_processing(self):
        """Test marking document as processing"""
        document = Document.objects.create(
            client=self.client,
            document_type='passport',
            title='Test Document'
        )
        
        document.mark_as_processing()
        self.assertEqual(document.status, 'processing')
    
    def test_mark_as_processed(self):
        """Test marking document as processed"""
        document = Document.objects.create(
            client=self.client,
            document_type='passport',
            title='Test Document'
        )
        
        extracted_data = {'name': 'John Doe', 'passport_number': 'A1234567'}
        ocr_text = 'Passport information text...'
        
        document.mark_as_processed(
            extracted_data=extracted_data,
            ocr_text=ocr_text
        )
        
        self.assertEqual(document.status, 'processed')
        self.assertIsNotNone(document.processed_at)
        self.assertEqual(document.ai_extracted_data, extracted_data)
        self.assertEqual(document.ocr_text, ocr_text)
    
    def test_verify_document(self):
        """Test verifying document"""
        document = Document.objects.create(
            client=self.client,
            document_type='passport',
            title='Test Document'
        )
        
        document.verify(self.user, notes='Verified successfully')
        
        self.assertEqual(document.status, 'verified')
        self.assertEqual(document.verified_by, self.user)
        self.assertIsNotNone(document.verified_at)
        self.assertEqual(document.verification_notes, 'Verified successfully')


class DocumentAccessLogTestCase(TestCase):
    """Test DocumentAccessLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_obj = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+61412345678',
            destination_country='AU',
            visa_type='skilled',
            region='AU'
        )
        
        self.document = Document.objects.create(
            client=self.client_obj,
            document_type='passport',
            title='Test Document'
        )
    
    def test_create_access_log(self):
        """Test creating an access log entry"""
        log = DocumentAccessLog.objects.create(
            document=self.document,
            user=self.user,
            action='view',
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(log.action, 'view')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.document, self.document)


# Run tests:
# python manage.py test s3_storage.tests

