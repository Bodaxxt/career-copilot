"""
File storage interface and implementations.
واجهة وتطبيقات تخزين الملفات المرفوعة.
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import uuid
from typing import Optional


class FileStorage(ABC):
    """
    Abstract base class for file storage operations.
    """

    @abstractmethod
    async def save_file(self, content: bytes, original_filename: str) -> str:
        """
        Save file content and return the accessible file URL or path.
        """
        pass

    @abstractmethod
    def get_file_path(self, file_url: str) -> Optional[Path]:
        """
        Resolve the file path from its URL or identifier.
        """
        pass


class LocalFileStorage(FileStorage):
    """
    Local filesystem storage implementation saving to `./uploads/`.
    """

    def __init__(self, base_dir: str = "./uploads") -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, content: bytes, original_filename: str) -> str:
        """
        Save file to local directory with unique filename to prevent overwrites.
        """
        file_ext = Path(original_filename).suffix.lower()
        if not file_ext:
            file_ext = ".pdf"

        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        destination = self.base_dir / unique_name

        # Write file content asynchronously/synchronously
        with open(destination, "wb") as f:
            f.write(content)

        # Return relative URL / path
        return f"/uploads/{unique_name}"

    def get_file_path(self, file_url: str) -> Optional[Path]:
        """
        Get the absolute path for a local file URL.
        """
        clean_name = os.path.basename(file_url)
        path = self.base_dir / clean_name
        if path.exists() and path.is_file():
            return path
        return None
