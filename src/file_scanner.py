"""
File scanner module for discovering C++ source files.
Provides functionality to recursively scan directories and identify C++ files.
"""

import os
import fnmatch
from typing import List, Set
from pathlib import Path


class FileScanner:
    """
    Scans directories and files to find C++ source files for analysis.
    Supports filtering by file extensions and exclude patterns.
    """
    
    # Default C++ file extensions
    CPP_EXTENSIONS = {'.cpp', '.cxx', '.cc', '.c++', '.C'}
    HEADER_EXTENSIONS = {'.h', '.hpp', '.hxx', '.h++', '.H', '.hh'}
    
    def __init__(self):
        self.supported_extensions = self.CPP_EXTENSIONS.copy()
    
    def scan(self, 
             path: str, 
             recursive: bool = True, 
             include_headers: bool = False,
             exclude_patterns: List[str] = None) -> List[str]:
        """
        Scan for C++ files in the given path.
        
        Args:
            path: File or directory path to scan
            recursive: Whether to scan subdirectories recursively
            include_headers: Whether to include header files in the scan
            exclude_patterns: List of glob patterns to exclude
        
        Returns:
            List of absolute paths to C++ files found
        """
        if exclude_patterns is None:
            exclude_patterns = []
        
        # Update supported extensions based on include_headers flag
        extensions = self.CPP_EXTENSIONS.copy()
        if include_headers:
            extensions.update(self.HEADER_EXTENSIONS)
        
        files = []
        path_obj = Path(path)
        
        if path_obj.is_file():
            # Single file case
            if self._is_cpp_file(str(path_obj), extensions):
                if not self._should_exclude(str(path_obj), exclude_patterns):
                    files.append(str(path_obj.absolute()))
        elif path_obj.is_dir():
            # Directory case
            files = self._scan_directory(
                str(path_obj), 
                extensions, 
                recursive, 
                exclude_patterns
            )
        else:
            raise ValueError(f"Path does not exist: {path}")
        
        return sorted(files)
    
    def _scan_directory(self, 
                       directory: str, 
                       extensions: Set[str], 
                       recursive: bool,
                       exclude_patterns: List[str]) -> List[str]:
        """
        Scan a directory for C++ files.
        
        Args:
            directory: Directory path to scan
            extensions: Set of file extensions to include
            recursive: Whether to scan subdirectories
            exclude_patterns: Patterns to exclude
        
        Returns:
            List of absolute file paths found
        """
        files = []
        
        try:
            if recursive:
                # Use os.walk for recursive scanning
                for root, dirs, filenames in os.walk(directory):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs 
                              if not self._should_exclude(os.path.join(root, d), exclude_patterns)]
                    
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if (self._is_cpp_file(file_path, extensions) and 
                            not self._should_exclude(file_path, exclude_patterns)):
                            files.append(os.path.abspath(file_path))
            else:
                # Non-recursive scanning - only current directory
                try:
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        if (os.path.isfile(item_path) and 
                            self._is_cpp_file(item_path, extensions) and
                            not self._should_exclude(item_path, exclude_patterns)):
                            files.append(os.path.abspath(item_path))
                except PermissionError:
                    print(f"Warning: Permission denied accessing directory: {directory}")
        
        except OSError as e:
            print(f"Warning: Error scanning directory {directory}: {e}")
        
        return files
    
    def _is_cpp_file(self, file_path: str, extensions: Set[str]) -> bool:
        """
        Check if a file is a C++ source file based on its extension.
        
        Args:
            file_path: Path to the file to check
            extensions: Set of valid extensions
        
        Returns:
            True if the file is a C++ file, False otherwise
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in extensions
    
    def _should_exclude(self, path: str, exclude_patterns: List[str]) -> bool:
        """
        Check if a path should be excluded based on exclude patterns.
        
        Args:
            path: Path to check
            exclude_patterns: List of glob patterns to match against
        
        Returns:
            True if the path should be excluded, False otherwise
        """
        if not exclude_patterns:
            return False
        
        path_name = os.path.basename(path)
        full_path = os.path.normpath(path)
        
        for pattern in exclude_patterns:
            # Check against both basename and full path
            if (fnmatch.fnmatch(path_name, pattern) or 
                fnmatch.fnmatch(full_path, pattern) or
                fnmatch.fnmatch(full_path, f"*{pattern}*")):
                return True
        
        return False
    
    def get_supported_extensions(self, include_headers: bool = False) -> Set[str]:
        """
        Get the set of supported file extensions.
        
        Args:
            include_headers: Whether to include header file extensions
        
        Returns:
            Set of supported file extensions
        """
        extensions = self.CPP_EXTENSIONS.copy()
        if include_headers:
            extensions.update(self.HEADER_EXTENSIONS)
        return extensions
    
    def add_extension(self, extension: str) -> None:
        """
        Add a custom file extension to be recognized as C++ files.
        
        Args:
            extension: File extension to add (e.g., '.cpp')
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        self.supported_extensions.add(extension)
    
    def remove_extension(self, extension: str) -> None:
        """
        Remove a file extension from recognition.
        
        Args:
            extension: File extension to remove (e.g., '.cpp')
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        self.supported_extensions.discard(extension)
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary containing file information
        """
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path_obj.stat()
        
        return {
            'path': str(path_obj.absolute()),
            'name': path_obj.name,
            'extension': path_obj.suffix,
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime,
            'is_header': path_obj.suffix.lower() in self.HEADER_EXTENSIONS,
            'is_source': path_obj.suffix.lower() in self.CPP_EXTENSIONS
        }
    
    def validate_path(self, path: str) -> bool:
        """
        Validate that a path exists and is accessible.
        
        Args:
            path: Path to validate
        
        Returns:
            True if path is valid and accessible, False otherwise
        """
        try:
            path_obj = Path(path)
            return path_obj.exists() and (path_obj.is_file() or path_obj.is_dir())
        except (OSError, ValueError):
            return False
    
    def get_directory_stats(self, directory: str, recursive: bool = True, 
                           include_headers: bool = False) -> dict:
        """
        Get statistics about C++ files in a directory.
        
        Args:
            directory: Directory to analyze
            recursive: Whether to scan recursively
            include_headers: Whether to include header files
        
        Returns:
            Dictionary with statistics about the directory
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Not a directory: {directory}")
        
        files = self.scan(directory, recursive, include_headers)
        
        total_size = 0
        source_files = 0
        header_files = 0
        
        for file_path in files:
            file_info = self.get_file_info(file_path)
            total_size += file_info['size_bytes']
            
            if file_info['is_source']:
                source_files += 1
            elif file_info['is_header']:
                header_files += 1
        
        return {
            'directory': directory,
            'total_files': len(files),
            'source_files': source_files,
            'header_files': header_files,
            'total_size_bytes': total_size,
            'recursive_scan': recursive,
            'included_headers': include_headers
        }