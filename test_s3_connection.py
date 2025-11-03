"""
Quick test script to verify S3 connection for Evol Assistant CMS
Run this before integrating with Django
"""

import boto3
from decouple import config
from botocore.exceptions import ClientError

def test_s3_connection():
    """Test AWS S3 connection and permissions"""
    
    print("🔍 Testing AWS S3 Connection...\n")
    
    # Load credentials from .env
    try:
        aws_access_key = config('AWS_ACCESS_KEY_ID')
        aws_secret_key = config('AWS_SECRET_ACCESS_KEY')
        bucket_name = config('AWS_STORAGE_BUCKET_NAME')
        region_name = config('AWS_S3_REGION_NAME')
        
        print(f"✓ Loaded credentials from .env")
        print(f"  Bucket: {bucket_name}")
        print(f"  Region: {region_name}\n")
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False
    
    # Create S3 client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )
        print("✓ Created S3 client\n")
        
    except Exception as e:
        print(f"❌ Error creating S3 client: {e}")
        return False
    
    # Test 1: Check bucket exists
    print("Test 1: Checking bucket exists...")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists and is accessible\n")
    except ClientError as e:
        print(f"❌ Bucket check failed: {e}")
        return False
    
    # Test 2: Upload a test file
    print("Test 2: Uploading test file...")
    test_content = "Test from Evol Assistant CMS - Python Script"
    test_key = "test/python_test.txt"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ServerSideEncryption='AES256'
        )
        print(f"✅ Uploaded test file: {test_key}\n")
    except ClientError as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Test 3: List objects
    print("Test 3: Listing files...")
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='test/'
        )
        
        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} file(s):")
            for obj in response['Contents']:
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            print()
        else:
            print("✅ No files found (bucket is empty)\n")
            
    except ClientError as e:
        print(f"❌ List failed: {e}")
        return False
    
    # Test 4: Download file
    print("Test 4: Downloading test file...")
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=test_key
        )
        downloaded_content = response['Body'].read().decode('utf-8')
        
        if downloaded_content == test_content:
            print(f"✅ Downloaded and verified content matches\n")
        else:
            print(f"⚠️  Content mismatch!")
            return False
            
    except ClientError as e:
        print(f"❌ Download failed: {e}")
        return False
    
    # Test 5: Generate presigned URL
    print("Test 5: Generating presigned URL...")
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600
        )
        print(f"✅ Presigned URL generated (expires in 1 hour)")
        print(f"   URL: {url[:80]}...\n")
        
    except ClientError as e:
        print(f"❌ Presigned URL generation failed: {e}")
        return False
    
    # Test 6: Delete test file
    print("Test 6: Cleaning up test file...")
    try:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=test_key
        )
        print(f"✅ Deleted test file\n")
        
    except ClientError as e:
        print(f"❌ Delete failed: {e}")
        return False
    
    # All tests passed!
    print("="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\n✅ Your AWS S3 setup is working perfectly!")
    print("✅ You can now integrate with Django")
    print("\nNext steps:")
    print("  1. Copy s3_storage/ to your Django project")
    print("  2. Update settings.py with S3 configuration")
    print("  3. Run migrations: python manage.py migrate")
    print("  4. Start testing with the Django REST API")
    
    return True


if __name__ == "__main__":
    try:
        test_s3_connection()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

