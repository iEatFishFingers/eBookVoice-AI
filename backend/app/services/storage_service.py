"""
Secure Cloud Storage Service
Handles file uploads/downloads to AWS S3 or Google Cloud Storage
with encryption, access controls, and secure file management.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from google.cloud import storage as gcs
from google.oauth2 import service_account
import hashlib
import mimetypes
from pathlib import Path

class SecureCloudStorage:
    """
    Secure cloud storage manager with support for AWS S3 and Google Cloud Storage.
    Implements encryption, access controls, and secure file handling.
    """
    
    def __init__(self, provider: str = "aws"):
        self.provider = provider.lower()
        self.client = None
        self.bucket_name = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize cloud storage client based on provider"""
        if self.provider == "aws":
            self._initialize_aws()
        elif self.provider == "gcp":
            self._initialize_gcp()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _initialize_aws(self):
        """Initialize AWS S3 client with proper security settings"""
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')
            
            if not self.bucket_name:
                raise ValueError("AWS_S3_BUCKET environment variable is required")
                
        except NoCredentialsError:
            raise ValueError("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    
    def _initialize_gcp(self):
        """Initialize Google Cloud Storage client"""
        try:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = gcs.Client(credentials=credentials)
            else:
                self.client = gcs.Client()  # Use default credentials
            
            self.bucket_name = os.getenv('GCP_STORAGE_BUCKET')
            if not self.bucket_name:
                raise ValueError("GCP_STORAGE_BUCKET environment variable is required")
                
        except Exception as e:
            raise ValueError(f"Failed to initialize GCP client: {str(e)}")
    
    def generate_secure_filename(self, original_filename: str, user_id: str = None) -> str:
        """Generate a secure, unique filename with timestamp and hash"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(original_filename).suffix
        
        # Create hash from original filename and timestamp for uniqueness
        hash_input = f"{original_filename}_{timestamp}_{uuid.uuid4().hex[:8]}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        
        # Include user_id in path if provided for better organization
        if user_id:
            return f"users/{user_id}/{timestamp}_{file_hash}{file_extension}"
        else:
            return f"uploads/{timestamp}_{file_hash}{file_extension}"
    
    def upload_file(self, local_file_path: str, user_id: str = None, 
                   custom_key: str = None) -> Dict[str, Any]:
        """
        Upload file to cloud storage with security measures
        
        Args:
            local_file_path: Path to local file
            user_id: Optional user ID for organization
            custom_key: Optional custom key name
            
        Returns:
            Dict with upload info including secure URL and metadata
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        # Generate secure filename
        original_filename = os.path.basename(local_file_path)
        storage_key = custom_key or self.generate_secure_filename(original_filename, user_id)
        
        # Get file metadata
        file_size = os.path.getsize(local_file_path)
        content_type = mimetypes.guess_type(local_file_path)[0] or 'application/octet-stream'
        
        try:
            if self.provider == "aws":
                return self._upload_to_s3(local_file_path, storage_key, content_type, file_size)
            elif self.provider == "gcp":
                return self._upload_to_gcs(local_file_path, storage_key, content_type, file_size)
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def _upload_to_s3(self, local_file_path: str, storage_key: str, 
                     content_type: str, file_size: int) -> Dict[str, Any]:
        """Upload file to AWS S3 with encryption"""
        extra_args = {
            'ContentType': content_type,
            'ServerSideEncryption': 'AES256',  # Server-side encryption
            'Metadata': {
                'uploaded_at': datetime.now().isoformat(),
                'file_size': str(file_size)
            }
        }
        
        self.client.upload_file(
            local_file_path,
            self.bucket_name,
            storage_key,
            ExtraArgs=extra_args
        )
        
        return {
            'provider': 'aws',
            'bucket': self.bucket_name,
            'key': storage_key,
            'size': file_size,
            'content_type': content_type,
            'uploaded_at': datetime.now().isoformat(),
            'url': f"s3://{self.bucket_name}/{storage_key}"
        }
    
    def _upload_to_gcs(self, local_file_path: str, storage_key: str,
                      content_type: str, file_size: int) -> Dict[str, Any]:
        """Upload file to Google Cloud Storage"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(storage_key)
        
        # Set metadata
        blob.metadata = {
            'uploaded_at': datetime.now().isoformat(),
            'file_size': str(file_size)
        }
        
        with open(local_file_path, 'rb') as file_obj:
            blob.upload_from_file(file_obj, content_type=content_type)
        
        return {
            'provider': 'gcp',
            'bucket': self.bucket_name,
            'key': storage_key,
            'size': file_size,
            'content_type': content_type,
            'uploaded_at': datetime.now().isoformat(),
            'url': f"gs://{self.bucket_name}/{storage_key}"
        }
    
    def download_file(self, storage_key: str, local_file_path: str) -> bool:
        """Download file from cloud storage to local path"""
        try:
            if self.provider == "aws":
                self.client.download_file(self.bucket_name, storage_key, local_file_path)
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(storage_key)
                blob.download_to_filename(local_file_path)
            
            return True
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def generate_presigned_url(self, storage_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for secure file access"""
        try:
            if self.provider == "aws":
                return self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': storage_key},
                    ExpiresIn=expiration
                )
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(storage_key)
                return blob.generate_signed_url(
                    expiration=datetime.now() + timedelta(seconds=expiration),
                    method='GET'
                )
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def delete_file(self, storage_key: str) -> bool:
        """Delete file from cloud storage"""
        try:
            if self.provider == "aws":
                self.client.delete_object(Bucket=self.bucket_name, Key=storage_key)
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(storage_key)
                blob.delete()
            
            return True
        except Exception as e:
            raise Exception(f"Delete failed: {str(e)}")
    
    def list_user_files(self, user_id: str, limit: int = 100) -> list:
        """List files for a specific user"""
        prefix = f"users/{user_id}/"
        files = []
        
        try:
            if self.provider == "aws":
                response = self.client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=limit
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat(),
                            'etag': obj['ETag'].strip('"')
                        })
            
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blobs = bucket.list_blobs(prefix=prefix, max_results=limit)
                
                for blob in blobs:
                    files.append({
                        'key': blob.name,
                        'size': blob.size,
                        'last_modified': blob.time_created.isoformat(),
                        'etag': blob.etag
                    })
            
            return files
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")


class FileManager:
    """
    Local file manager that integrates with cloud storage
    Handles temporary files and cleanup
    """
    
    def __init__(self, storage: SecureCloudStorage):
        self.storage = storage
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def save_uploaded_file(self, file, user_id: str = None) -> Dict[str, Any]:
        """Save uploaded file locally and optionally to cloud storage"""
        # Generate secure filename
        secure_filename = self.storage.generate_secure_filename(file.filename, user_id)
        local_path = os.path.join(self.temp_dir, os.path.basename(secure_filename))
        
        # Save file locally first
        file.save(local_path)
        
        # Upload to cloud storage
        upload_info = self.storage.upload_file(local_path, user_id)
        upload_info['local_path'] = local_path
        
        return upload_info
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        if not os.path.exists(self.temp_dir):
            return
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up temp file: {filename}")
                    except OSError:
                        pass