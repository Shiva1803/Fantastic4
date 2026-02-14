"""
FileStorage service for managing physical file uploads.

This module handles saving files to disk, ensuring unique filenames,
and validating file types and sizes.
"""

import os
import uuid
import shutil
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage


class FileStorage:
    """
    Manages file storage operations.
    
    Attributes:
        upload_dir: Directory where files are stored
        max_size_bytes: Maximum allowed file size
        allowed_extensions: Set of allowed file extensions
    """
    
    def __init__(self, upload_dir: str = 'uploads', max_size_mb: int = 10):
        """
        Initialize file storage service.
        
        Args:
            upload_dir: Directory to save files (relative to backend)
            max_size_mb: Maximum file size in megabytes
        """
        # Ensure absolute path
        if not os.path.isabs(upload_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.upload_dir = os.path.join(base_dir, upload_dir)
        else:
            self.upload_dir = upload_dir
            
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Allowed file types
        self.allowed_extensions = {
            'pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'
        }
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
            
    def save_file(self, file: WerkzeugFileStorage) -> Tuple[str, str, int]:
        """
        Save an uploaded file to disk.
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            Tuple containing (filename, file_path, file_size)
            
        Raises:
            ValueError: If file is invalid or too large
        """
        if not file:
            raise ValueError("No file provided")
            
        if not file.filename:
            raise ValueError("No filename provided")
            
        if not self._is_allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
            
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > self.max_size_bytes:
            raise ValueError(f"File too large. Maximum size is {self.max_size_bytes / (1024*1024)}MB")
            
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        return unique_filename, file_path, size
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            True if deleted, False if not found/error
        """
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """
        Get absolute path for a file if it exists.
        
        Args:
            filename: Name of file
            
        Returns:
            Absolute path or None
        """
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            return file_path
        return None
