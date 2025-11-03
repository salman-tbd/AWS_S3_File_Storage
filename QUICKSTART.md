# ⚡ QUICK START GUIDE

**Part of [Evol Assistant Customer Management System (CMS)](https://evolassistant.com/)**

**Get up and running in 15 minutes!**

---

## 🎯 Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- AWS Account
- Django 4.2+

---

## 🚀 Quick Setup (Development)

### **Step 1: Install Dependencies (2 min)**

```bash
pip install -r requirements.txt
```

---

### **Step 2: Configure Environment (3 min)**

```bash
# Copy environment template
cp env.example .env

# Edit .env and add your AWS credentials
# Minimum required:
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_STORAGE_BUCKET_NAME_AU=your-bucket-name
```

---

### **Step 3: Copy Module to Your Django Project (2 min)**

```bash
# Copy the entire s3_storage folder
cp -r s3_storage /path/to/your/django/project/

# Update your settings.py
# Add 's3_storage' to INSTALLED_APPS
# Copy AWS settings from config/settings.py
```

---

### **Step 4: Run Migrations (2 min)**

```bash
python manage.py makemigrations s3_storage
python manage.py migrate
```

---

### **Step 5: Create Superuser (1 min)**

```bash
python manage.py createsuperuser
```

---

### **Step 6: Start Services (1 min)**

Open 3 terminals:

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker -l info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A config beat -l info
```

---

### **Step 7: Test Upload (2 min)**

**Via Browsable API:**
1. Go to: `http://localhost:8000/api/storage/`
2. Log in with superuser credentials
3. Click "clients" → Create a test client
4. Click "documents" → Upload a test file

**Via cURL:**
```bash
# Get auth token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Upload document
curl -X POST http://localhost:8000/api/storage/documents/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "client_id=CLIENT_UUID" \
  -F "document_type=passport" \
  -F "title=Test Document" \
  -F "file=@test.pdf"
```

---

### **Step 8: Verify (2 min)**

Check:
- ✅ File uploaded to S3
- ✅ Document status = "uploaded"
- ✅ Celery task processed it (status = "processed")
- ✅ Can download file

---

## 🎉 Done!

You now have:
- ✅ S3 storage working
- ✅ API endpoints active
- ✅ Celery processing documents
- ✅ Ready to integrate into your main app

---

## 📚 Next Steps

1. **Configure AWS properly** → `docs/AWS_SETUP.md`
2. **Integrate with your app** → `docs/INTEGRATION.md`
3. **Learn the API** → `docs/API.md`
4. **Customize for your needs** → Edit models, tasks, etc.

---

## 🚨 Troubleshooting

### Django won't start?
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running

### Celery won't connect?
- Check Redis is running: `redis-cli ping`
- Verify CELERY_BROKER_URL in settings

### S3 upload fails?
- Verify AWS credentials in .env
- Check bucket exists and has correct permissions
- Ensure bucket region matches settings

### Files not processing?
- Check Celery worker is running
- Look at Celery logs for errors
- Verify task is registered: `celery -A config inspect registered`

---

## 💡 Pro Tips

- Use the browsable API first (easier than cURL)
- Start with small test files
- Check Django logs: `logs/s3_storage.log`
- Monitor Celery in real-time: `celery -A config events`

---

## 📞 Need Help?

1. Check `DEPLOYMENT.md` for detailed info
2. Review documentation in `docs/` folder
3. Check Django/Celery logs
4. Verify AWS CloudWatch logs

---

**🎉 Happy coding!**

