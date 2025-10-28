"""S3 Storage Service for file uploads."""

import mimetypes
import uuid
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.exceptions import SaaSPlatformException


class StorageService:
    """S3 Storage service for file uploads."""

    def __init__(self):
        """Initialize S3 client."""
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            raise SaaSPlatformException(
                message="AWS credentials not configured",
                error_code="STORAGE_NOT_CONFIGURED",
            )

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.aws_s3_bucket

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "uploads",
        content_type: Optional[str] = None,
    ) -> dict:
        """
        Upload file to S3.

        Args:
            file_content: File content as bytes
            filename: Original filename
            folder: S3 folder/prefix
            content_type: MIME type (auto-detected if not provided)

        Returns:
            dict with file_url, file_key, bucket, size
        """
        try:
            # Generate unique filename
            file_extension = filename.split(".")[-1] if "." in filename else ""
            unique_filename = (
                f"{uuid.uuid4()}.{file_extension}"
                if file_extension
                else str(uuid.uuid4())
            )
            file_key = (
                f"{folder}/{datetime.utcnow().strftime('%Y/%m/%d')}/{unique_filename}"
            )

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = "application/octet-stream"

            # Validate file size
            file_size = len(file_content)
            if file_size > settings.max_file_size:
                raise SaaSPlatformException(
                    message=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes",
                    error_code="FILE_TOO_LARGE",
                )

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                # ACL='public-read',  # Uncomment if you want public files
            )

            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_key}"

            return {
                "file_url": file_url,
                "file_key": file_key,
                "bucket": self.bucket_name,
                "size": file_size,
                "content_type": content_type,
                "original_filename": filename,
            }

        except ClientError as e:
            raise SaaSPlatformException(
                message=f"Failed to upload file: {str(e)}", error_code="UPLOAD_FAILED"
            )

    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            file_key: S3 object key

        Returns:
            True if deleted successfully
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True

        except ClientError as e:
            raise SaaSPlatformException(
                message=f"Failed to delete file: {str(e)}", error_code="DELETE_FAILED"
            )

    def get_presigned_url(self, file_key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for temporary access to private file.

        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            raise SaaSPlatformException(
                message=f"Failed to generate presigned URL: {str(e)}",
                error_code="PRESIGNED_URL_FAILED",
            )

    def validate_file_type(self, filename: str) -> bool:
        """
        Validate if file type is allowed.

        Args:
            filename: File name with extension

        Returns:
            True if file type is allowed
        """
        file_extension = (
            f".{filename.split('.')[-1].lower()}" if "." in filename else ""
        )
        return file_extension in settings.allowed_file_types
