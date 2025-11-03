# API Documentation - S3 Storage Module

**Part of [Evol Assistant Customer Management System (CMS)](https://evolassistant.com/)**

Complete REST API documentation for document management.

---

## 🔐 Authentication

All endpoints require authentication. Use one of:

1. **Session Authentication** (for browsable API)
2. **Token Authentication** (for API clients)

### Get Authentication Token:

```bash
POST /api/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

Use token in headers:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## 📁 Clients API

### **List All Clients**

```
GET /api/storage/clients/
```

**Query Parameters:**
- `status` - Filter by status (inquiry, documents, submitted, etc.)
- `region` - Filter by region (AU, IN)
- `search` - Search by name or email

**Example:**
```bash
curl -X GET "http://localhost:8000/api/storage/clients/?status=documents&region=AU" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/storage/clients/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+61412345678",
      "destination_country": "AU",
      "visa_type": "skilled",
      "status": "documents",
      "region": "AU",
      "assigned_to": {
        "id": 1,
        "username": "caseofficer",
        "email": "officer@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "created_at": "2025-10-15T10:30:00Z",
      "updated_at": "2025-10-20T15:45:00Z",
      "document_count": 8
    }
  ]
}
```

---

### **Create New Client**

```
POST /api/storage/clients/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+61412345678",
  "destination_country": "AU",
  "visa_type": "skilled",
  "region": "AU"
}
```

**Response:** `201 Created`

---

### **Get Client Details**

```
GET /api/storage/clients/{client_id}/
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/storage/clients/123e4567-e89b-12d3-a456-426614174000/" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### **Update Client**

```
PUT /api/storage/clients/{client_id}/
PATCH /api/storage/clients/{client_id}/
```

---

### **Delete Client**

```
DELETE /api/storage/clients/{client_id}/
```

---

### **Get Client's Documents**

```
GET /api/storage/clients/{client_id}/documents/
```

**Response:**
```json
[
  {
    "id": "doc-uuid-1",
    "client_name": "John Doe",
    "document_type": "passport",
    "title": "Passport Copy",
    "status": "verified",
    "file_size": 2048576,
    "uploaded_at": "2025-10-15T10:30:00Z",
    "uploaded_by_name": "Jane Smith"
  }
]
```

---

### **Assign Client to Case Officer**

```
POST /api/storage/clients/{client_id}/assign/
```

**Request Body:**
```json
{
  "user_id": 5
}
```

---

## 📄 Documents API

### **List All Documents**

```
GET /api/storage/documents/
```

**Query Parameters:**
- `client_id` - Filter by client UUID
- `document_type` - Filter by type (passport, bank_statement, etc.)
- `status` - Filter by status (uploaded, processing, verified, etc.)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/storage/documents/?client_id=CLIENT_UUID&status=verified" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### **Upload Document**

```
POST /api/storage/documents/
Content-Type: multipart/form-data
```

**Form Data:**
- `client_id` (required) - Client UUID
- `document_type` (required) - Document type
- `title` (required) - Document title
- `description` (optional) - Description
- `file` (required) - File to upload

**Example:**
```bash
curl -X POST "http://localhost:8000/api/storage/documents/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "client_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "document_type=passport" \
  -F "title=Passport Front Page" \
  -F "description=Main identification page" \
  -F "file=@/path/to/passport.pdf"
```

**Response:** `201 Created`
```json
{
  "id": "doc-uuid",
  "client": { ... },
  "document_type": "passport",
  "title": "Passport Front Page",
  "description": "Main identification page",
  "file": "documents/clients/123e.../passport/20251031_passport.pdf",
  "file_size": 2048576,
  "file_size_mb": 2.0,
  "file_type": "application/pdf",
  "original_filename": "passport.pdf",
  "s3_bucket": "evol-assistant-docs",
  "s3_key": "documents/clients/123e.../passport/20251031_passport.pdf",
  "s3_region": "ap-south-1",
  "status": "uploaded",
  "uploaded_at": "2025-10-31T10:30:00Z",
  "uploaded_by": { ... },
  "download_url": "https://evol-assistant-docs.s3.ap-south-1.amazonaws.com/..."
}
```

---

### **Get Document Details**

```
GET /api/storage/documents/{document_id}/
```

---

### **Download Document**

```
GET /api/storage/documents/{document_id}/download/
```

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/...?presigned-params",
  "expires_in": 3600,
  "filename": "passport.pdf"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/storage/documents/DOC_UUID/download/" \
  -H "Authorization: Token YOUR_TOKEN"
```

Then use the `download_url` to download the file:
```bash
curl -X GET "DOWNLOAD_URL" -o downloaded_file.pdf
```

---

### **Verify Document** (Case Officer)

```
POST /api/storage/documents/{document_id}/verify/
```

**Request Body:**
```json
{
  "notes": "Document verified. All details match the application."
}
```

**Response:**
```json
{
  "message": "Document verified successfully",
  "document": { ... }
}
```

---

### **Reprocess Document with AI**

```
POST /api/storage/documents/{document_id}/reprocess/
```

**Response:**
```json
{
  "message": "Document queued for reprocessing",
  "document_id": "doc-uuid"
}
```

---

### **Delete Document**

```
DELETE /api/storage/documents/{document_id}/
```

**Response:** `204 No Content`

---

### **Bulk Upload Documents**

```
POST /api/storage/documents/bulk_upload/
Content-Type: multipart/form-data
```

**Form Data:**
- `client_id` (required)
- `document_type` (required)
- `files` (required) - Multiple files

**Example:**
```bash
curl -X POST "http://localhost:8000/api/storage/documents/bulk_upload/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "client_id=CLIENT_UUID" \
  -F "document_type=financial_proof" \
  -F "files=@bank_statement_1.pdf" \
  -F "files=@bank_statement_2.pdf" \
  -F "files=@bank_statement_3.pdf"
```

**Response:**
```json
{
  "message": "3 documents uploaded successfully",
  "document_ids": ["uuid1", "uuid2", "uuid3"]
}
```

---

### **Get Document Statistics**

```
GET /api/storage/documents/statistics/
```

**Response:**
```json
{
  "total": 150,
  "by_status": {
    "uploaded": 20,
    "processing": 5,
    "processed": 80,
    "verified": 40,
    "rejected": 5
  },
  "by_type": {
    "passport": 25,
    "bank_statement": 30,
    "degree": 20,
    "employment_letter": 25,
    "other": 50
  }
}
```

---

## 📊 Document Types

Available document types:

| Type | Description |
|------|-------------|
| `passport` | Passport |
| `photo` | Photograph |
| `birth_certificate` | Birth Certificate |
| `marriage_certificate` | Marriage Certificate |
| `bank_statement` | Bank Statement |
| `tax_return` | Tax Return |
| `financial_proof` | Financial Proof |
| `degree` | Degree Certificate |
| `transcript` | Academic Transcript |
| `english_test` | English Language Test |
| `employment_letter` | Employment Letter |
| `payslip` | Payslip |
| `resume` | Resume/CV |
| `reference_letter` | Reference Letter |
| `application_form` | Application Form |
| `visa_application` | Visa Application |
| `police_clearance` | Police Clearance |
| `medical` | Medical Certificate |
| `other` | Other Document |

---

## 📝 Document Status Flow

```
uploaded → processing → processed → verified
                            ↓
                        rejected
```

- **uploaded**: File uploaded to S3
- **processing**: AI processing in progress (Celery)
- **processed**: AI extraction complete
- **verified**: Verified by case officer
- **rejected**: Rejected by case officer

---

## 🔍 Access Logs API (Admin Only)

### **List Access Logs**

```
GET /api/storage/access-logs/
```

**Query Parameters:**
- `document_id` - Filter by document
- `user_id` - Filter by user

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "document": "doc-uuid",
      "document_title": "Passport Copy",
      "user": {
        "id": 2,
        "username": "caseofficer",
        "email": "officer@example.com"
      },
      "action": "download",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-10-31T10:30:00Z"
    }
  ]
}
```

---

## 🧪 Testing with Postman/Insomnia

### **Import Collection:**

Create a new collection with:
- Base URL: `http://localhost:8000`
- Authorization: Token `YOUR_TOKEN`

### **Test Sequence:**

1. **Create Client**
   - POST `/api/storage/clients/`

2. **Upload Document**
   - POST `/api/storage/documents/`
   - Use client ID from step 1

3. **Check Processing Status**
   - GET `/api/storage/documents/{id}/`
   - Wait for status to change from `processing` to `processed`

4. **Download Document**
   - GET `/api/storage/documents/{id}/download/`
   - Use returned URL to download file

5. **Verify Document**
   - POST `/api/storage/documents/{id}/verify/`

---

## ⚠️ Error Responses

### **400 Bad Request**
```json
{
  "error": "Validation failed",
  "details": {
    "file": ["File size exceeds maximum allowed size of 50MB"]
  }
}
```

### **401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **403 Forbidden**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### **404 Not Found**
```json
{
  "detail": "Not found."
}
```

### **500 Internal Server Error**
```json
{
  "error": "Unable to generate download URL",
  "message": "Internal server error"
}
```

---

## 📈 Rate Limiting

- **Default:** 1000 requests/hour per user
- **Upload:** 100 uploads/hour per user
- **Download:** 500 downloads/hour per user

Configure in Django settings:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/hour'
    }
}
```

---

## 🔗 Webhooks (Future Enhancement)

Configure webhooks to receive notifications:

```json
{
  "event": "document.processed",
  "data": {
    "document_id": "uuid",
    "client_id": "uuid",
    "status": "processed",
    "timestamp": "2025-10-31T10:30:00Z"
  }
}
```

---

## 💡 Best Practices

1. **Always validate file size** before upload
2. **Use bulk upload** for multiple files
3. **Poll status endpoint** to check processing progress
4. **Cache download URLs** (valid for 1 hour)
5. **Handle errors gracefully** with retry logic
6. **Log all access** for compliance

---

**API Documentation Complete!** 🎉

