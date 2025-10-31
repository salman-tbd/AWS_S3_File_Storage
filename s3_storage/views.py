"""
Django REST Framework Views for Document Management API
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Client, Document, DocumentAccessLog
from .serializers import (
    ClientSerializer, ClientCreateSerializer,
    DocumentSerializer, DocumentUploadSerializer,
    DocumentListSerializer, DocumentVerifySerializer,
    DocumentAccessLogSerializer, BulkUploadSerializer
)
from .tasks import process_document, process_bulk_documents
import logging

logger = logging.getLogger(__name__)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client CRUD operations
    """
    queryset = Client.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        return ClientSerializer
    
    def get_queryset(self):
        """Filter clients based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If not superuser/staff, show only assigned clients
        if not user.is_staff:
            queryset = queryset.filter(assigned_to=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by region
        region_filter = self.request.query_params.get('region', None)
        if region_filter:
            queryset = queryset.filter(region=region_filter)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for a client"""
        client = self.get_object()
        documents = client.documents.all()
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign client to a case officer"""
        client = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            client.assigned_to = user
            client.save()
            return Response({'message': 'Client assigned successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document CRUD operations
    """
    queryset = Document.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        elif self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'verify':
            return DocumentVerifySerializer
        return DocumentSerializer
    
    def get_queryset(self):
        """Filter documents based on user role and query params"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If not staff, show only documents of assigned clients
        if not user.is_staff:
            queryset = queryset.filter(client__assigned_to=user)
        
        # Filter by client
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by document type
        doc_type = self.request.query_params.get('document_type', None)
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('client', 'uploaded_by', 'verified_by')
    
    def create(self, request, *args, **kwargs):
        """Upload document with logging"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        
        # Log upload action
        self._log_document_access(document, 'upload', request)
        
        logger.info(f"Document uploaded: {document.id} by {request.user}")
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve document with logging"""
        instance = self.get_object()
        
        # Log view action
        self._log_document_access(instance, 'view', request)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete document with logging"""
        instance = self.get_object()
        
        # Log delete action
        self._log_document_access(instance, 'delete', request)
        
        # Delete from S3
        from .utils import delete_s3_file
        if instance.s3_bucket and instance.s3_key:
            delete_s3_file(instance.s3_bucket, instance.s3_key, instance.s3_region)
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Generate presigned download URL"""
        document = self.get_object()
        
        # Log download action
        self._log_document_access(document, 'download', request)
        
        download_url = document.get_download_url(expiration=3600)
        
        if download_url:
            return Response({
                'download_url': download_url,
                'expires_in': 3600,
                'filename': document.original_filename
            })
        else:
            return Response(
                {'error': 'Unable to generate download URL'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify document by case officer"""
        document = self.get_object()
        serializer = DocumentVerifySerializer(
            document,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Document verified successfully',
            'document': DocumentSerializer(document).data
        })
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess document with AI"""
        document = self.get_object()
        
        # Trigger reprocessing
        process_document.delay(str(document.id))
        
        return Response({
            'message': 'Document queued for reprocessing',
            'document_id': str(document.id)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload multiple documents at once"""
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        client_id = serializer.validated_data['client_id']
        files = serializer.validated_data['files']
        document_type = serializer.validated_data['document_type']
        
        client = get_object_or_404(Client, id=client_id)
        
        # Create documents
        documents = []
        for file in files:
            document = Document.objects.create(
                client=client,
                document_type=document_type,
                title=file.name,
                file=file,
                uploaded_by=request.user
            )
            documents.append(document)
        
        # Trigger bulk processing
        document_ids = [str(doc.id) for doc in documents]
        process_bulk_documents.delay(document_ids)
        
        return Response({
            'message': f'{len(documents)} documents uploaded successfully',
            'document_ids': document_ids
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get document statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_status': {},
            'by_type': {},
        }
        
        # Count by status
        for status_choice, _ in Document.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            stats['by_status'][status_choice] = count
        
        # Count by document type
        for doc_type, _ in Document.DOCUMENT_TYPE_CHOICES:
            count = queryset.filter(document_type=doc_type).count()
            if count > 0:
                stats['by_type'][doc_type] = count
        
        return Response(stats)
    
    def _log_document_access(self, document, action, request):
        """Log document access for audit trail"""
        try:
            DocumentAccessLog.objects.create(
                document=document,
                user=request.user,
                action=action,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except Exception as e:
            logger.error(f"Error logging document access: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing document access logs (audit trail)
    """
    queryset = DocumentAccessLog.objects.all()
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter logs by document or user"""
        queryset = super().get_queryset()
        
        document_id = self.request.query_params.get('document_id', None)
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('document', 'user')

