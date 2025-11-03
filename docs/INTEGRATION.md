# Integration Guide - Merging S3 Storage into Your Main Application

**Part of [Evol Assistant Customer Management System (CMS)](https://evolassistant.com/)**

This guide will help you integrate the S3 storage module into the Evol Assistant CMS platform.

---

## 📋 Prerequisites

- Existing Django 4.2+ application
- PostgreSQL database
- Redis for Celery
- AWS account with S3 access

---

## 🚀 Step-by-Step Integration

### **Step 1: Install Dependencies**

Add to your main project's `requirements.txt`:

```bash
boto3>=1.34.0
django-storages>=1.14.0
celery>=5.3.0
python-decouple>=3.8
Pillow>=10.0.0
PyPDF2>=3.0.0
python-magic>=0.4.27
```

Install:
```bash
pip install -r requirements.txt
```

---

### **Step 2: Copy the S3 Storage Module**

Copy the entire `s3_storage` directory into your Django project:

```
your_project/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── your_app/
└── s3_storage/          ← Copy this entire folder
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── storage_backends.py
    ├── tasks.py
    ├── utils.py
    ├── validators.py
    └── urls.py
```

---

### **Step 3: Update Django Settings**

Add to your `settings.py`:

```python
# 1. Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... your existing apps
    'rest_framework',
    'corsheaders',
    'storages',
    's3_storage',  # ← Add this
]

# 2. AWS S3 Configuration
from decouple import config

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME_AU = config('AWS_STORAGE_BUCKET_NAME_AU')
AWS_S3_REGION_NAME_AU = config('AWS_S3_REGION_NAME_AU', default='ap-southeast-2')
AWS_STORAGE_BUCKET_NAME_IN = config('AWS_STORAGE_BUCKET_NAME_IN')
AWS_S3_REGION_NAME_IN = config('AWS_S3_REGION_NAME_IN', default='ap-south-1')
AWS_S3_ENCRYPTION = 'AES256'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

# 3. Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# 4. File Upload Settings
MAX_UPLOAD_SIZE = 52428800  # 50MB
ALLOWED_DOCUMENT_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
```

---

### **Step 4: Update Environment Variables**

Add to your `.env` file:

```bash
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME_AU=evol-assistant-docs-au
AWS_S3_REGION_NAME_AU=ap-southeast-2
AWS_STORAGE_BUCKET_NAME_IN=evol-assistant-docs-in
AWS_S3_REGION_NAME_IN=ap-south-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

### **Step 5: Configure Celery**

Update your `config/celery.py` (or create if doesn't exist):

```python
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('your_project_name')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'archive-old-documents-daily': {
        'task': 's3_storage.tasks.archive_old_documents',
        'schedule': crontab(hour=2, minute=0),
    },
    'cleanup-temp-files-hourly': {
        'task': 's3_storage.tasks.cleanup_temp_files',
        'schedule': crontab(minute=0),
    },
}
```

Update your `config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

### **Step 6: Add URL Routes**

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your existing URLs
    path('api/storage/', include('s3_storage.urls')),
]
```

---

### **Step 7: Integrate with Existing Client Model** (Optional)

If you already have a `Client` model, you can:

**Option A:** Use the provided Client model as-is

**Option B:** Modify the Document model to use your existing Client model

Replace in `s3_storage/models.py`:
```python
from your_app.models import Client  # Import your Client model

# Comment out or remove the Client model in s3_storage/models.py
```

---

### **Step 8: Run Migrations**

```bash
python manage.py makemigrations s3_storage
python manage.py migrate
```

---

### **Step 9: Create Superuser** (if needed)

```bash
python manage.py createsuperuser
```

---

### **Step 10: Start Services**

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (for scheduled tasks):**
```bash
celery -A config beat -l info
```

---

## ✅ Verify Installation

### **1. Check API Endpoints**

Visit: `http://localhost:8000/api/storage/`

You should see the DRF browsable API.

### **2. Test Upload**

```bash
curl -X POST http://localhost:8000/api/storage/documents/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "client_id=CLIENT_UUID" \
  -F "document_type=passport" \
  -F "title=Test Passport" \
  -F "file=@/path/to/file.pdf"
```

---

## 🔄 Integration with Existing Models

### **If you have existing models:**

**1. Client Model Integration:**

If you have a `Client` model in your app:

```python
# In s3_storage/models.py
from your_app.models import Client  # Import your model

# Remove or comment out the Client model definition
```

**2. Add Fields to Existing Models:**

If you want to keep your existing Client model, add:

```python
# In your_app/models.py
class Client(models.Model):
    # ... your existing fields
    region = models.CharField(max_length=2, choices=[('AU', 'Australia'), ('IN', 'India')], default='AU')
    
    def get_storage_backend(self):
        from s3_storage.storage_backends import AustraliaMediaStorage, IndiaMediaStorage
        if self.region == 'IN':
            return IndiaMediaStorage()
        return AustraliaMediaStorage()
```

---

## 🔧 Customization

### **1. Add Custom Document Types**

Edit `s3_storage/models.py`:

```python
DOCUMENT_TYPE_CHOICES = [
    # ... existing types
    ('custom_type', 'Your Custom Type'),
]
```

### **2. Customize AI Processing**

Edit `s3_storage/tasks.py`:

Replace the placeholder processing functions with your actual AI/OCR implementation:
- AWS Textract
- Google Cloud Vision
- Tesseract OCR
- Custom ML models

### **3. Add Notifications**

Edit `s3_storage/tasks.py` in `notify_case_officer`:

```python
# Add email notification
from django.core.mail import send_mail

send_mail(
    subject=f'Document Processed: {document.title}',
    message=f'Document for client {document.client} has been processed.',
    from_email='noreply@yourdomain.com',
    recipient_list=[officer.email],
)
```

---

## 🧪 Testing

Create test files in `tests/`:

```python
# tests/test_upload.py
from django.test import TestCase
from django.contrib.auth.models import User
from s3_storage.models import Client, Document

class DocumentUploadTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client_obj = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            destination_country='AU',
            visa_type='skilled',
            region='AU'
        )
    
    def test_document_creation(self):
        # Your test logic
        pass
```

Run tests:
```bash
python manage.py test s3_storage
```

---

## 🚨 Troubleshooting

### **Problem: S3 Upload Fails**

**Solution:**
1. Check AWS credentials in `.env`
2. Verify S3 bucket exists and has correct permissions
3. Check IAM user has `s3:PutObject` permission

### **Problem: Celery Tasks Not Running**

**Solution:**
1. Ensure Redis is running: `redis-cli ping`
2. Check Celery worker is running
3. Verify `CELERY_BROKER_URL` in settings

### **Problem: File Validation Errors**

**Solution:**
1. Install `python-magic`: `pip install python-magic`
2. On Windows: Install `python-magic-bin`
3. Check file size limits in settings

---

## 📊 Monitoring

### **View Celery Tasks:**

```bash
celery -A config inspect active
celery -A config inspect registered
```

### **Monitor S3 Usage:**

Use AWS CloudWatch or S3 Storage Lens

### **Check Document Status:**

```bash
python manage.py shell

from s3_storage.models import Document
Document.objects.filter(status='processing').count()
```

---

## 🔒 Security Checklist

- [ ] S3 buckets are private (no public access)
- [ ] IAM user has minimum required permissions
- [ ] Encryption at rest enabled (AES-256)
- [ ] HTTPS/TLS enforced
- [ ] File validation enabled
- [ ] Access logging enabled
- [ ] Authentication required for all endpoints
- [ ] CORS configured properly

---

## 📈 Next Steps

1. **Configure AWS S3** (see `AWS_SETUP.md`)
2. **Test API endpoints** (see `API.md`)
3. **Integrate with frontend** (Next.js examples available)
4. **Set up monitoring** (CloudWatch, Sentry)
5. **Configure backups** (S3 lifecycle policies)

---

## 💡 Tips

- Start with one region (Australia), add India later
- Test with small files first
- Use S3 lifecycle policies to reduce costs
- Enable versioning for important documents
- Set up CloudFront if serving files to users frequently

---

## 📞 Support

For issues or questions:
- Check logs: `logs/s3_storage.log`
- Review AWS CloudWatch logs
- Check Celery worker logs

---

**Integration Complete!** 🎉

Your Django application now has production-ready S3 document storage with AI processing capabilities.

