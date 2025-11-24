"""
Base interface for all distribution system downloaders.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class BaseDownloader(ABC):
    """
    Abstract base class for all distribution system downloaders.
    
    All distribution systems should implement this interface to ensure
    consistent behavior and easier testing.
    """
    
    @abstractmethod
    def download_app(self, download_path: str, **kwargs) -> str:
        """
        Download application from the distribution system.
        
        Args:
            download_path: Directory where the application should be saved
            **kwargs: Distribution-specific parameters
            
        Returns:
            Path to the downloaded application file
            
        Raises:
            RuntimeError: If download fails
        """
        pass
    
    @abstractmethod
    def get_app_info(self, **kwargs) -> Dict[str, Any]:
        """
        Get application metadata from the distribution system.
        
        Args:
            **kwargs: Distribution-specific parameters (e.g., package_name, app_id)
            
        Returns:
            Dictionary with application information:
            - integration_type: str
            - package_name: Optional[str]
            - version_name: Optional[str]
            - version_code: Optional[int]
            - file_size: Optional[int]
            - icon_url: Optional[str]
            - Additional distribution-specific fields
            
        Raises:
            RuntimeError: If info retrieval fails
        """
        pass

