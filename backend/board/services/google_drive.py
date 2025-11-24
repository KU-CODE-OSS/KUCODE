"""
Google Drive service module for handling file uploads and link validation.

This module provides functionality to:
- Upload files to Google Drive using a service account
- Validate Google Drive links
- Retrieve file metadata from Google Drive
"""

import json
import re
from typing import Dict, Optional, Tuple
from io import BytesIO

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError


class GoogleDriveServiceError(Exception):
    """Base exception for Google Drive service errors."""
    pass


class GoogleDriveService:
    """Service for interacting with Google Drive API."""

    # Google Drive file URL patterns
    DRIVE_URL_PATTERNS = [
        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'https://docs\.google\.com/[a-z]+/d/([a-zA-Z0-9_-]+)',
    ]

    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self):
        """Initialize the Google Drive service with credentials from settings."""
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Drive API service."""
        try:
            credentials_json = settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON
            if not credentials_json:
                raise GoogleDriveServiceError("Google Drive service account credentials not configured")

            # Parse credentials JSON
            if isinstance(credentials_json, str):
                credentials_info = json.loads(credentials_json)
            else:
                credentials_info = credentials_json

            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=self.SCOPES
            )

            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)

        except json.JSONDecodeError as e:
            raise GoogleDriveServiceError(f"Invalid service account JSON: {str(e)}")
        except Exception as e:
            raise GoogleDriveServiceError(f"Failed to initialize Google Drive service: {str(e)}")

    def upload_file(self, file_obj, filename: str, mime_type: str = None) -> Dict[str, str]:
        """
        Upload a file to Google Drive.

        Args:
            file_obj: File-like object or Django UploadedFile
            filename: Name for the file in Google Drive
            mime_type: MIME type of the file (auto-detected if not provided)

        Returns:
            Dictionary containing:
                - file_id: Google Drive file ID
                - web_view_link: Link to view the file in browser
                - web_content_link: Direct download link
                - name: File name
                - size: File size in bytes

        Raises:
            GoogleDriveServiceError: If upload fails
        """
        if not self.service:
            raise GoogleDriveServiceError("Google Drive service not initialized")

        folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        if not folder_id:
            raise GoogleDriveServiceError("Google Drive folder ID not configured")

        try:
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            # Read file content
            if hasattr(file_obj, 'read'):
                file_content = file_obj.read()
                file_obj.seek(0)  # Reset file pointer
            else:
                file_content = file_obj

            # Auto-detect MIME type if not provided
            if not mime_type:
                mime_type = self._guess_mime_type(filename)

            # Create media upload
            media = MediaIoBaseUpload(
                BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )

            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink,size,mimeType'
            ).execute()

            # Make file accessible to anyone with the link
            self._make_file_public(file['id'])

            return {
                'file_id': file['id'],
                'web_view_link': file.get('webViewLink', ''),
                'web_content_link': file.get('webContentLink', ''),
                'name': file['name'],
                'size': file.get('size', '0'),
                'mime_type': file.get('mimeType', mime_type)
            }

        except HttpError as e:
            raise GoogleDriveServiceError(f"Failed to upload file: {str(e)}")
        except Exception as e:
            raise GoogleDriveServiceError(f"Unexpected error during upload: {str(e)}")

    def _make_file_public(self, file_id: str):
        """Make a file publicly accessible with the link."""
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
        except HttpError as e:
            # Log but don't fail the upload if permission setting fails
            print(f"Warning: Failed to make file public: {str(e)}")

    def get_file_metadata(self, file_id_or_url: str) -> Optional[Dict[str, str]]:
        """
        Get metadata for a file from Google Drive.

        Args:
            file_id_or_url: Either a file ID or a Google Drive URL

        Returns:
            Dictionary containing file metadata, or None if file not found

        Raises:
            GoogleDriveServiceError: If metadata retrieval fails
        """
        if not self.service:
            raise GoogleDriveServiceError("Google Drive service not initialized")

        # Extract file ID if URL is provided
        file_id = self.extract_file_id(file_id_or_url)
        if not file_id:
            raise GoogleDriveServiceError("Invalid Google Drive file ID or URL")

        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,webViewLink,webContentLink,size,mimeType,createdTime,modifiedTime'
            ).execute()

            return {
                'file_id': file['id'],
                'name': file['name'],
                'web_view_link': file.get('webViewLink', ''),
                'web_content_link': file.get('webContentLink', ''),
                'size': file.get('size', '0'),
                'mime_type': file.get('mimeType', ''),
                'created_time': file.get('createdTime', ''),
                'modified_time': file.get('modifiedTime', '')
            }

        except HttpError as e:
            if e.resp.status == 404:
                return None
            raise GoogleDriveServiceError(f"Failed to get file metadata: {str(e)}")
        except Exception as e:
            raise GoogleDriveServiceError(f"Unexpected error getting metadata: {str(e)}")

    @classmethod
    def extract_file_id(cls, url_or_id: str) -> Optional[str]:
        """
        Extract Google Drive file ID from a URL or return the ID if already provided.

        Args:
            url_or_id: Google Drive URL or file ID

        Returns:
            File ID if found, None otherwise
        """
        if not url_or_id:
            return None

        # If it looks like a direct file ID (alphanumeric, underscores, hyphens)
        if re.match(r'^[a-zA-Z0-9_-]+$', url_or_id):
            return url_or_id

        # Try to extract from URL patterns
        for pattern in cls.DRIVE_URL_PATTERNS:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        return None

    @classmethod
    def validate_drive_link(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a URL is a valid Google Drive link.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, file_id or error_message)
        """
        if not url:
            return False, "URL is required"

        file_id = cls.extract_file_id(url)
        if not file_id:
            return False, "Invalid Google Drive URL format"

        return True, file_id

    @staticmethod
    def _guess_mime_type(filename: str) -> str:
        """Guess MIME type based on file extension."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
