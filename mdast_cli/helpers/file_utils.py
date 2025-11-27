"""
Common file and directory utilities for distribution systems.
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def ensure_download_dir(download_path: str) -> None:
    """
    Ensure download directory exists, create if it doesn't.
    
    Args:
        download_path: Path to the download directory
        
    Raises:
        OSError: If directory cannot be created
    """
    try:
        os.makedirs(download_path, exist_ok=True)
    except OSError as e:
        logger.error(f'Failed to create download directory {download_path}: {e}')
        raise


def cleanup_file(file_path: str) -> None:
    """
    Safely remove a file, logging but not raising on failure.
    
    Args:
        file_path: Path to file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f'Cleaned up file: {file_path}')
    except Exception as e:
        logger.warning(f'Failed to cleanup file {file_path}: {e}')


def cleanup_directory(dir_path: str) -> None:
    """
    Safely remove a directory and all its contents, logging but not raising on failure.
    
    Args:
        dir_path: Path to directory to remove
    """
    try:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            logger.debug(f'Cleaned up directory: {dir_path}')
    except Exception as e:
        logger.warning(f'Failed to cleanup directory {dir_path}: {e}')


def safe_path_join(base: str, *parts: str) -> str:
    """
    Safely join path parts, preventing path traversal.
    
    Args:
        base: Base directory path
        *parts: Additional path components
        
    Returns:
        Joined path
        
    Raises:
        ValueError: If path traversal is detected
    """
    base_path = Path(base).resolve()
    full_path = base_path.joinpath(*parts).resolve()
    
    # Check that resolved path is still within base directory
    try:
        full_path.relative_to(base_path)
    except ValueError:
        raise ValueError(f'Path traversal detected: {full_path} is outside {base_path}')
    
    return str(full_path)


def get_file_size_mb(file_path: str) -> Optional[float]:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB, or None if file doesn't exist
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return None

