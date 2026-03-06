"""Platform detection and binary path utilities."""
import os
import platform
import shutil
from pathlib import Path


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == 'Darwin'


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == 'Linux'


def get_apkeep_binary_path() -> str:
    """
    Get path to apkeep binary.
    
    Priority:
    1. Local binary in project root (apkeep_macos or apkeep_linux)
    2. System binary in PATH (apkeep)
    
    Returns:
        Path to apkeep binary.
        
    Raises:
        RuntimeError: If apkeep binary is not found.
    """
    # Try local binaries first (project root)
    project_root = Path(__file__).parent.parent.parent
    if is_macos():
        local_binary = project_root / 'apkeep_macos'
    elif is_linux():
        local_binary = project_root / 'apkeep_linux'
    else:
        local_binary = None
    
    if local_binary and local_binary.exists() and local_binary.is_file():
        # Make binary executable if needed
        os.chmod(local_binary, 0o755)
        return str(local_binary.absolute())
    
    # Fallback to system PATH
    system_binary = shutil.which('apkeep')
    if system_binary:
        return system_binary
    
    # Not found
    platform_name = 'macOS' if is_macos() else 'Linux' if is_linux() else platform.system()
    local_binary_name = 'apkeep_macos' if is_macos() else 'apkeep_linux' if is_linux() else 'apkeep'
    raise RuntimeError(
        f'Google Play: apkeep binary not found. '
        f'Expected local binary: {local_binary_name} in project root, '
        f'or system binary "apkeep" in PATH. '
        f'Platform: {platform_name}'
    )

