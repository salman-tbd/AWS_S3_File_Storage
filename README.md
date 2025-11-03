# AWS S3 Storage Integration Module

**Part of:** [Evol Assistant Customer Management System (CMS)](https://evolassistant.com/)

**Purpose:** Modular S3 document storage for Evol Assistant CMS

This module provides production-ready AWS S3 integration for the Evol Assistant platform with:
- ✅ Multi-region support (Australia + India)
- ✅ Secure document upload/download
- ✅ Celery-based async document processing
- ✅ AI-ready document analysis
- ✅ REST API endpoints
- ✅ Easy integration into existing Django apps

---

## 🎯 Quick Start (2 Hours Setup)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up AWS S3
Follow `docs/AWS_SETUP.md` to:
- Create S3 buckets (Australia + India regions)
- Create IAM user with appropriate permissions
- Get AWS access keys

### 3. Configure Environment
```bash
cp env.example .env
# Edit .env with your AWS credentials:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_STORAGE_BUCKET_NAME_AU=bucket-name-au
# AWS_STORAGE_BUCKET_NAME_IN=bucket-name-in
```

### 4. Integrate with Your Django App
Follow `docs/INTEGRATION.md` to:
- Copy `s3_storage/` module to your project
- Update Django settings
- Configure Celery + Redis
- Run migrations
- Test endpoints

### 5. Quick Test
```bash
python manage.py runserver                    # Terminal 1
celery -A config worker -l info               # Terminal 2
```

Visit: `http://localhost:8000/api/storage/`

---

## 📦 Module Structure

```
s3_storage/
├── storage_backends.py   # S3 storage backends (AU/IN regions)
├── models.py            # Document models
├── serializers.py       # DRF serializers
├── views.py            # API endpoints
├── urls.py             # URL routing
├── tasks.py            # Celery async tasks
├── utils.py            # Helper functions
└── validators.py       # File validation
```

---

## 🚀 Features

### Document Management
- Upload documents to region-specific S3 buckets
- Automatic file validation and virus scanning ready
- Organized folder structure per client
- Support for multiple document types (passport, financial, education, etc.)

### AI Processing (Celery)
- Async document processing with Celery workers
- OCR text extraction ready
- Document classification
- Metadata extraction
- Notification system

### Security
- Encryption at rest (AES-256)
- Private S3 buckets (no public access)
- Signed URLs for secure downloads
- File type validation
- Size limits enforcement

### Multi-Region Support
- Australia (Sydney): ap-southeast-2
- India (Mumbai): ap-south-1
- Data residency compliance

---

## 📖 Documentation

- **[Integration Guide](docs/INTEGRATION.md)** - How to merge into your main app
- **[API Documentation](docs/API.md)** - REST API endpoints
- **[AWS Setup](docs/AWS_SETUP.md)** - AWS S3 configuration guide

---

## 🔧 Tech Stack

- **Storage:** AWS S3 (boto3, django-storages)
- **Framework:** Django 4.2+ with DRF
- **Async Processing:** Celery + Redis
- **Database:** PostgreSQL (metadata)
- **File Processing:** Pillow, PyPDF2, python-magic

---

## 💰 Cost Estimate

For 500GB storage + 100GB egress/month:
- **~$15-20/month** with lifecycle policies
- See cost optimization in docs

---

## 🔒 Security Checklist

- [x] Encryption at rest (AES-256)
- [x] Private buckets (no public access)
- [x] IAM roles (least privilege)
- [x] File validation
- [x] Signed URLs with expiration
- [x] Access logging ready
- [x] Versioning support

---

## 📝 License

Internal use - Evol Assistant CMS

---

## 🌐 Evol Assistant Ecosystem

This S3 storage module is part of the **Evol Assistant Customer Management System**:

- **Main Website:** [https://evolassistant.com/](https://evolassistant.com/)
- **Frontend:** [https://www.evolassistant.com/](https://www.evolassistant.com/)
- **Backend API:** [api.evolassistant.com](https://api.evolassistant.com/)
- **Repository:** [github.com/salman-tbd/AWS_S3_File_Storage](https://github.com/salman-tbd/AWS_S3_File_Storage)

---

## 🤝 Integration Support

This module is designed to be:
1. **Dropped into** your existing Django app
2. **Configured** via environment variables
3. **Extended** with your business logic
4. **Production-ready** from day one

See `docs/INTEGRATION.md` for step-by-step merge instructions.

