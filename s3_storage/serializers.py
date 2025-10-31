"""
Django REST Framework Serializers for Document API
"""

from rest_framework import serializers
from .models import Client, Document, DocumentAccessLog
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""
    
    assigned_to = UserSerializer(read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'destination_country', 'visa_type', 'status', 'region',
            'assigned_to', 'created_at', 'updated_at', 'document_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        """Get total number of documents for this client"""
        return obj.documents.count()


class ClientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clients"""
    
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'destination_country', 'visa_type', 'region'
        ]


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    
    client = ClientSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    download_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'client', 'document_type', 'title', 'description',
            'file', 'file_size', 'file_size_mb', 'file_type', 'original_filename',
            's3_bucket', 's3_key', 's3_region',
            'status', 'ai_extracted_data', 'ocr_text',
            'verified_by', 'verified_at', 'verification_notes',
            'uploaded_at', 'processed_at', 'updated_at',
            'uploaded_by', 'download_url'
        ]
        read_only_fields = [
            'id', 'file_size', 'file_type', 'original_filename',
            's3_bucket', 's3_key', 's3_region',
            'ai_extracted_data', 'ocr_text',
            'verified_by', 'verified_at',
            'uploaded_at', 'processed_at', 'updated_at',
            'uploaded_by'
        ]
    
    def get_download_url(self, obj):
        """Generate presigned download URL"""
        return obj.get_download_url(expiration=3600)
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading documents"""
    
    client_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Document
        fields = [
            'client_id', 'document_type', 'title', 'description', 'file'
        ]
    
    def validate_client_id(self, value):
        """Validate client exists"""
        try:
            Client.objects.get(id=value)
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found")
        return value
    
    def create(self, validated_data):
        """Create document with client association"""
        client_id = validated_data.pop('client_id')
        client = Client.objects.get(id=client_id)
        
        # Set uploaded_by from request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        
        document = Document.objects.create(
            client=client,
            **validated_data
        )
        
        # Trigger async processing
        from .tasks import process_document
        process_document.delay(str(document.id))
        
        return document


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing documents"""
    
    client_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'client_name', 'document_type', 'title',
            'status', 'file_size', 'uploaded_at', 'uploaded_by_name'
        ]
    
    def get_client_name(self, obj):
        """Get client full name"""
        return f"{obj.client.first_name} {obj.client.last_name}"
    
    def get_uploaded_by_name(self, obj):
        """Get uploader name"""
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return "System"


class DocumentVerifySerializer(serializers.Serializer):
    """Serializer for verifying documents"""
    
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        """Verify document"""
        request = self.context.get('request')
        instance.verify(
            user=request.user,
            notes=validated_data.get('notes')
        )
        return instance


class DocumentAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for document access logs"""
    
    user = UserSerializer(read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentAccessLog
        fields = [
            'id', 'document', 'document_title', 'user', 'action',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class BulkUploadSerializer(serializers.Serializer):
    """Serializer for bulk document upload"""
    
    client_id = serializers.UUIDField()
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )
    document_type = serializers.ChoiceField(choices=Document.DOCUMENT_TYPE_CHOICES)
    
    def validate_client_id(self, value):
        """Validate client exists"""
        try:
            Client.objects.get(id=value)
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found")
        return value

