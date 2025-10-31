"""
URL Configuration for Document Management API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, DocumentViewSet, DocumentAccessLogViewSet

# Create router
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'access-logs', DocumentAccessLogViewSet, basename='access-log')

app_name = 's3_storage'

urlpatterns = [
    path('', include(router.urls)),
]

"""
API Endpoints:

Clients:
    GET     /api/clients/                   - List all clients
    POST    /api/clients/                   - Create new client
    GET     /api/clients/{id}/              - Get client details
    PUT     /api/clients/{id}/              - Update client
    DELETE  /api/clients/{id}/              - Delete client
    GET     /api/clients/{id}/documents/    - Get client's documents
    POST    /api/clients/{id}/assign/       - Assign to case officer

Documents:
    GET     /api/documents/                 - List all documents
    POST    /api/documents/                 - Upload new document
    GET     /api/documents/{id}/            - Get document details
    PUT     /api/documents/{id}/            - Update document
    DELETE  /api/documents/{id}/            - Delete document
    GET     /api/documents/{id}/download/   - Get download URL
    POST    /api/documents/{id}/verify/     - Verify document
    POST    /api/documents/{id}/reprocess/  - Reprocess with AI
    POST    /api/documents/bulk_upload/     - Upload multiple documents
    GET     /api/documents/statistics/      - Get document statistics

Access Logs:
    GET     /api/access-logs/               - List access logs (admin only)
    GET     /api/access-logs/{id}/          - Get log details

Query Parameters:
    - ?status=uploaded                      - Filter by status
    - ?document_type=passport               - Filter by document type
    - ?client_id=<uuid>                     - Filter by client
    - ?search=john                          - Search clients
    - ?region=AU                            - Filter by region
"""

