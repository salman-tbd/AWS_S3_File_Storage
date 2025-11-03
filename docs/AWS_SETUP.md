# AWS S3 Setup Guide

**Part of [Evol Assistant Customer Management System (CMS)](https://evolassistant.com/)**

Complete guide to set up AWS S3 buckets for the Evol Assistant CMS document storage system.

---

## 📋 Overview

You'll create:
- **2 S3 Buckets** (Australia + India regions)
- **1 IAM User** with programmatic access
- **IAM Policy** with minimum required permissions
- **Lifecycle Policies** for cost optimization
- **Encryption & Security** configurations

**Estimated Time:** 30 minutes  
**Cost:** ~$15-30/month (for 500GB storage)

---

## 🚀 Step 1: Create AWS Account

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the signup process
4. Add payment method
5. Verify identity

---

## 📦 Step 2: Create S3 Buckets

### **A. Australia Region Bucket**

1. **Sign in** to AWS Console
2. Go to **S3** service
3. Click **"Create bucket"**

**Bucket Configuration:**

| Setting | Value |
|---------|-------|
| **Bucket name** | `evol-assistant-docs-au` (must be globally unique) |
| **AWS Region** | **Asia Pacific (Sydney)** `ap-southeast-2` |
| **Block all public access** | ✅ **Enabled** (keep private) |
| **Bucket Versioning** | ✅ **Enable** (recover deleted files) |
| **Default encryption** | ✅ **Enable** - SSE-S3 (AES-256) |
| **Object Lock** | ❌ Disable (not needed) |

4. Click **"Create bucket"**

---

### **B. India Region Bucket**

Repeat the process with:

| Setting | Value |
|---------|-------|
| **Bucket name** | `evol-assistant-docs-in` |
| **AWS Region** | **Asia Pacific (Mumbai)** `ap-south-1` |
| **All other settings** | Same as Australia bucket |

---

## 🔐 Step 3: Create IAM User

### **A. Create User**

1. Go to **IAM** service in AWS Console
2. Click **"Users"** → **"Add users"**
3. **User name:** `evol-assistant-s3-user`
4. **Access type:** ✅ **Programmatic access** (API, CLI, SDK)
5. Click **"Next: Permissions"**

---

### **B. Create Custom Policy**

1. Click **"Attach policies directly"**
2. Click **"Create policy"**
3. Click **"JSON"** tab
4. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBuckets",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::evol-assistant-docs-au",
        "arn:aws:s3:::evol-assistant-docs-in"
      ]
    },
    {
      "Sid": "ObjectOperations",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:GetObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::evol-assistant-docs-au/*",
        "arn:aws:s3:::evol-assistant-docs-in/*"
      ]
    }
  ]
}
```

5. Click **"Next: Tags"**
6. **Policy name:** `EvolAssistantS3Policy`
7. **Description:** `S3 access for Evol Assistant CMS document storage`
8. Click **"Create policy"**

---

### **C. Attach Policy to User**

1. Go back to **"Add user"** tab
2. Refresh the policy list
3. Search for `EvolAssistantS3Policy`
4. ✅ Check the policy
5. Click **"Next: Tags"** (skip tags)
6. Click **"Next: Review"**
7. Click **"Create user"**

---

### **D. Save Credentials** ⚠️

**IMPORTANT:** Save these credentials immediately (shown only once):

```
Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Add to your `.env` file:**

```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

⚠️ **Never commit these to Git!**

---

## ⚡ Step 4: Configure Lifecycle Policies

Automatically move old documents to cheaper storage classes.

### **A. Australia Bucket Lifecycle**

1. Go to S3 → **evol-assistant-docs-au**
2. Click **"Management"** tab
3. Click **"Create lifecycle rule"**

**Rule Configuration:**

| Setting | Value |
|---------|-------|
| **Rule name** | `archive-old-documents` |
| **Rule scope** | ✅ Apply to all objects |
| **Lifecycle rule actions** | ✅ Transition current versions, ✅ Transition previous versions |

**Transitions:**

| Days | Storage Class | Cost |
|------|---------------|------|
| 0-30 | S3 Standard | $23/TB |
| 31-90 | S3 Standard-IA | $12.50/TB |
| 91+ | S3 Glacier Instant Retrieval | $4/TB |

**Configure:**
1. **After 30 days:** Transition to **S3 Standard-IA**
2. **After 90 days:** Transition to **S3 Glacier Instant Retrieval**
3. (Optional) **After 2555 days (7 years):** Delete objects

4. Click **"Create rule"**

---

### **B. India Bucket Lifecycle**

Repeat the same lifecycle policy for `evol-assistant-docs-in`.

---

## 🔒 Step 5: Enable Security Features

### **A. Enable Access Logging**

1. Create a **logging bucket**: `evol-assistant-logs`
2. For each document bucket:
   - Click **"Properties"** tab
   - Scroll to **"Server access logging"**
   - Click **"Edit"**
   - ✅ Enable
   - **Target bucket:** `evol-assistant-logs`
   - **Target prefix:** `au-docs-logs/` or `in-docs-logs/`
   - Click **"Save changes"**

---

### **B. Enable Bucket Versioning** (Already done in Step 2)

✅ Versioning allows you to:
- Recover deleted files
- Restore previous versions
- Protect against accidental deletion

---

### **C. Configure CORS** (for web uploads)

If uploading directly from browser:

1. Go to bucket → **"Permissions"** tab
2. Scroll to **"Cross-origin resource sharing (CORS)"**
3. Click **"Edit"**
4. Paste:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["https://yourdomain.com", "http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

5. Click **"Save changes"**

---

## 💰 Step 6: Set Up Cost Alerts

1. Go to **AWS Budgets**
2. Click **"Create budget"**
3. **Budget type:** Cost budget
4. **Name:** `S3 Storage Budget`
5. **Amount:** $50/month (adjust based on usage)
6. **Alerts:**
   - Alert at 80% ($40)
   - Alert at 100% ($50)
7. **Email:** your-email@example.com
8. Click **"Create budget"**

---

## 📊 Step 7: Monitor Usage

### **A. Enable CloudWatch Metrics**

1. Go to bucket → **"Metrics"** tab
2. View storage usage, requests, data transfer

### **B. S3 Storage Lens**

1. Go to **S3** → **"Storage Lens"**
2. View organization-wide storage analytics
3. Track cost optimization opportunities

---

## ✅ Step 8: Test Configuration

### **Test with AWS CLI:**

Install AWS CLI:
```bash
pip install awscli
```

Configure:
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Region: ap-southeast-2
# Output format: json
```

**Test upload:**
```bash
# Create a test file
echo "Test document" > test.txt

# Upload to Australia bucket
aws s3 cp test.txt s3://evol-assistant-docs-au/test/test.txt

# List files
aws s3 ls s3://evol-assistant-docs-au/test/

# Download file
aws s3 cp s3://evol-assistant-docs-au/test/test.txt downloaded.txt

# Delete file
aws s3 rm s3://evol-assistant-docs-au/test/test.txt
```

**Expected Output:**
```
upload: ./test.txt to s3://evol-assistant-docs-au/test/test.txt
2025-10-31 10:30:00      13 test.txt
download: s3://evol-assistant-docs-au/test/test.txt to ./downloaded.txt
delete: s3://evol-assistant-docs-au/test/test.txt
```

✅ If all commands work, your setup is correct!

---

## 🧹 Step 9: Clean Up Test Files

```bash
aws s3 rm s3://evol-assistant-docs-au/test/ --recursive
aws s3 rm s3://evol-assistant-docs-in/test/ --recursive
```

---

## 📝 Final Checklist

- [ ] Created 2 S3 buckets (AU + IN)
- [ ] Enabled encryption (AES-256)
- [ ] Enabled versioning
- [ ] Blocked all public access
- [ ] Created IAM user with programmatic access
- [ ] Attached custom policy with minimum permissions
- [ ] Saved AWS credentials to `.env` file
- [ ] Configured lifecycle policies
- [ ] Enabled access logging
- [ ] Set up cost alerts
- [ ] Tested upload/download with AWS CLI
- [ ] Configured CORS (if needed)

---

## 💰 Cost Estimate

### **Scenario 1: Small (100GB storage, 50GB egress)**
- Storage: $2.30/month
- Egress: $4.50/month
- Requests: $0.50/month
- **Total: ~$7/month** ✅

### **Scenario 2: Medium (500GB storage, 100GB egress)**
- Storage (mixed tiers): $9/month
- Egress: $9/month
- Requests: $2/month
- **Total: ~$20/month** ✅

### **Scenario 3: Large (2TB storage, 500GB egress)**
- Storage (with lifecycle): $30/month
- Egress: $45/month
- Requests: $5/month
- **Total: ~$80/month** ✅

**Compare to Wasabi:**
- Wasabi 1TB: $6.99/month (but 1TB minimum + 90-day retention)
- AWS S3 with lifecycle: $15-20/month (more flexible)

---

## 🚨 Troubleshooting

### **Problem: "Access Denied" errors**

**Solutions:**
1. Check IAM policy has correct permissions
2. Verify bucket names in policy match actual bucket names
3. Ensure AWS credentials are correct in `.env`
4. Check bucket region matches code configuration

### **Problem: High costs**

**Solutions:**
1. Enable lifecycle policies
2. Delete unnecessary files
3. Use S3 Intelligent-Tiering
4. Review CloudWatch metrics
5. Check for failed/incomplete uploads

### **Problem: Slow uploads**

**Solutions:**
1. Use multipart upload for large files
2. Choose region closest to your server
3. Check network connection
4. Enable S3 Transfer Acceleration (extra cost)

---

## 🔗 Useful AWS Resources

- [S3 Pricing Calculator](https://calculator.aws/)
- [S3 User Guide](https://docs.aws.amazon.com/s3/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/)

---

## 🎯 Next Steps

1. ✅ Complete this AWS setup
2. 📦 Integrate with Django app (see `INTEGRATION.md`)
3. 🧪 Test API endpoints (see `API.md`)
4. 🚀 Deploy to production
5. 📊 Monitor usage and costs

---

## 📞 Support

**AWS Support:**
- Basic: Free (community forums)
- Developer: $29/month
- Business: $100/month (recommended for production)

**AWS Documentation:**
- https://docs.aws.amazon.com/s3/

---

**AWS S3 Setup Complete!** 🎉

Your buckets are now ready for production use with proper security, cost optimization, and monitoring.

