"""
Exit codes for mdast_cli application.
Following Unix conventions and providing clear error categorization.
"""
from enum import IntEnum


class ExitCode(IntEnum):
    """Standard exit codes for the application."""
    SUCCESS = 0
    """Operation completed successfully."""
    
    INVALID_ARGS = 2
    """Invalid command-line arguments provided."""
    
    DOWNLOAD_FAILED = 4
    """Failed to download application from distribution system."""
    
    SCAN_FAILED = 5
    """Failed to create or execute scan."""
    
    NETWORK_ERROR = 6
    """Network-related error (timeout, connection failed, etc.)."""
    
    AUTH_ERROR = 7
    """Authentication or authorization error."""
    
    INTERNAL_ERROR = 1
    """Internal application error (default for unexpected errors)."""

