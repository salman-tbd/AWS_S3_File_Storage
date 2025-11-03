# 🚀 Evol Assistant CMS - S3 Integration Implementation Guide

**Status:** AWS S3 Setup Complete ✅ | Ready for Django Integration

---

## 📍 Current Status

✅ **Completed:**
- S3 Bucket created: `evol-assistant-docs` (Mumbai, ap-south-1)
- IAM User created: `evol-assistant-s3-user`
- Permissions configured: `EvolAssistantS3Policy`
- Credentials stored in `.env`
- AWS CLI tested successfully
- Python boto3 tested successfully

---

## 🎯 Next Steps: Integration Paths

### Path A: Quick Test Project (Recommended First)

Create a standalone Django project to test S3 integration before adding to production:

```bash
# 1. Create new Django project
django-admin startproject evolassistant_test
cd evolassistant_test

# 2. Copy S3 storage module
cp -r ../AWS-S3-file-storage/s3_storage ./

# 3. Copy configuration files
cp ../AWS-S3-file-storage/.env ./
cp ../AWS-S3-file-storage/requirements.txt ./

# 4. Install dependencies
pip install -r requirements.txt

# 5. Update settings (see below)

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Run server
python manage.py runserver
```

---

### Path B: Integrate into Existing Evol Assistant CMS

If you have the main CMS project ready:

```bash
# 1. Navigate to your Django project
cd /path/to/evolassistant_cms

# 2. Copy s3_storage module
cp -r /path/to/AWS-S3-file-storage/s3_storage ./

# 3. Copy/merge .env file
cp /path/to/AWS-S3-file-storage/.env ./
# OR add AWS variables to existing .env

# 4. Install additional dependencies
pip install boto3 django-storages celery pillow PyPDF2 python-magic

# 5. Update settings.py (see configuration below)

# 6. Update urls.py (see URL configuration below)

# 7. Run migrations
python manage.py makemigrations s3_storage
python manage.py migrate

# 8. Test
python manage.py runserver
```

---

## ⚙️ Django Settings Configuration

Add to your `settings.py`:

```python
# ===========================
# S3 STORAGE CONFIGURATION
# ===========================

from decouple import config

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',
    'corsheaders',
    'storages',
    's3_storage',  # ← Add this
]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-south-1')
AWS_S3_ENCRYPTION = config('AWS_S3_ENCRYPTION', default='AES256')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600  # 1 hour

# File Upload Settings
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=52428800, cast=int)  # 50MB
ALLOWED_DOCUMENT_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']

# Celery Configuration (for async processing)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# REST Framework (if not already configured)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

---

## 🔗 URL Configuration

Add to your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # S3 Storage API endpoints
    path('api/storage/', include('s3_storage.urls')),
    
    # ... your other URLs ...
]
```

---

## 🗄️ Database Migration

```bash
# Create migrations
python manage.py makemigrations s3_storage

# Apply migrations
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying s3_storage.0001_initial... OK
```

This will create 3 tables:
- `s3_storage_client` - Store client information
- `s3_storage_document` - Store document metadata
- `s3_storage_documentaccesslog` - Track file access

---

## 🧪 Testing the Integration

### 1. **Test via Django Admin**

```bash
# Create superuser (if not exists)
python manage.py createsuperuser

# Run server
python manage.py runserver

# Open browser
http://localhost:8000/admin/

# Navigate to:
# - S3 Storage > Clients (create a test client)
# - S3 Storage > Documents (upload a test file)
```

### 2. **Test via REST API**

**Using DRF Browsable API:**
```
http://localhost:8000/api/storage/
```

**Using cURL:**
```bash
# Get auth token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Create client
curl -X POST http://localhost:8000/api/storage/clients/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Client","email":"test@example.com","phone":"1234567890"}'

# Upload document
curl -X POST http://localhost:8000/api/storage/documents/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "client_id=CLIENT_UUID" \
  -F "document_type=passport" \
  -F "title=Test Document" \
  -F "file=@test.pdf"
```

### 3. **Test Python Script**

Already created: `test_s3_connection.py` ✅

---

## 🔧 Celery Setup (For Async Document Processing)

### Install Redis (if not already):
```bash
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# Mac: brew install redis
```

### Create celery.py in your project config:

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('evol_assistant')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Run Celery worker:

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat (for scheduled tasks)
celery -A config beat -l info
```

---

## 📊 API Endpoints Available

Once integrated, you'll have these endpoints:

### Client Management
- `GET /api/storage/clients/` - List all clients
- `POST /api/storage/clients/` - Create client
- `GET /api/storage/clients/{id}/` - Get client details
- `PUT /api/storage/clients/{id}/` - Update client
- `DELETE /api/storage/clients/{id}/` - Delete client

### Document Management
- `GET /api/storage/documents/` - List all documents
- `POST /api/storage/documents/` - Upload document
- `GET /api/storage/documents/{id}/` - Get document details
- `GET /api/storage/documents/{id}/download/` - Download document
- `DELETE /api/storage/documents/{id}/` - Delete document
- `POST /api/storage/documents/bulk-upload/` - Bulk upload

### Statistics
- `GET /api/storage/stats/` - Get storage statistics

---

## ✅ Post-Integration Checklist

- [ ] S3 storage module copied to Django project
- [ ] Dependencies installed from requirements.txt
- [ ] Settings.py updated with S3 configuration
- [ ] URLs.py includes s3_storage routes
- [ ] .env file copied with AWS credentials
- [ ] Migrations created and applied
- [ ] Superuser created for admin access
- [ ] Test client created in Django admin
- [ ] Test document uploaded successfully
- [ ] Document downloaded successfully
- [ ] REST API endpoints tested
- [ ] Celery worker running (optional but recommended)

---

## 🔒 Security Reminders

- ✅ `.env` file is in `.gitignore` (never commit credentials)
- ✅ `env.example` has placeholder values only
- ✅ S3 bucket is private (no public access)
- ✅ IAM user has minimum required permissions
- ✅ All API endpoints require authentication

---

## 🐛 Troubleshooting

### Issue: Import errors
**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: S3 connection fails
**Solution:** Verify .env file has correct AWS credentials:
```bash
python test_s3_connection.py
```

### Issue: Migrations fail
**Solution:** Check database connection and try:
```bash
python manage.py migrate --fake-initial
```

### Issue: File upload fails
**Solution:** Check:
1. AWS credentials are correct
2. IAM user has PutObject permission
3. File size is within MAX_UPLOAD_SIZE limit
4. File type is in ALLOWED_DOCUMENT_TYPES

---

## 📚 Documentation Reference

- **API Documentation:** `docs/API.md`
- **AWS Setup:** `docs/AWS_SETUP.md`
- **Integration Guide:** `docs/INTEGRATION.md`
- **Deployment Guide:** `DEPLOYMENT.md`

---

## 🎯 What to Implement Next

After basic integration is working:

1. **Customize Document Types**
   - Edit `s3_storage/models.py` DOCUMENT_TYPES
   - Add your specific document categories

2. **Add Business Logic**
   - Extend models with custom fields
   - Add custom validators
   - Implement approval workflows

3. **Frontend Integration**
   - Connect React/Vue/Angular frontend
   - Use REST API endpoints
   - Handle file uploads with progress bars

4. **Advanced Features**
   - OCR text extraction (Tesseract)
   - Document classification (ML)
   - Email notifications
   - Audit trail enhancements

---

## 📞 Need Help?

Review the documentation in `docs/` folder:
- Step-by-step integration guide
- Complete API reference
- Troubleshooting tips

---

**Status:** ✅ Ready to integrate into Evol Assistant CMS!

**Next Action:** Choose Path A (test project) or Path B (existing project) and follow the steps above.

