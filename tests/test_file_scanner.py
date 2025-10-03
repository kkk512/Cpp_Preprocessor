"""
Unit tests for the file scanner module.
Tests file discovery, filtering, and validation functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.file_scanner import FileScanner


class TestFileScanner(unittest.TestCase):
    """Test cases for the FileScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scanner = FileScanner()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = {
            'test.cpp': '#include <iostream>\nint main() { return 0; }',
            'test.h': '#ifndef TEST_H\n#define TEST_H\n#endif',
            'test.hpp': 'class Test {};',
            'readme.txt': 'This is a readme file',
            'subdir/nested.cpp': '#define NESTED 1',
            'subdir/nested.h': '#pragma once',
            'subdir/deep/very_nested.cxx': '// Deep file'
        }
        
        for file_path, content in self.test_files.items():
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_scan_single_file(self):
        """Test scanning a single C++ file."""
        test_file = os.path.join(self.temp_dir, 'test.cpp')
        files = self.scanner.scan(test_file, recursive=False)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(os.path.basename(files[0]), 'test.cpp')
    
    def test_scan_directory_non_recursive(self):
        """Test scanning directory without recursion."""
        files = self.scanner.scan(self.temp_dir, recursive=False)
        
        # Should find cpp and h files in root only
        basenames = [os.path.basename(f) for f in files]
        expected = {'test.cpp', 'test.h', 'test.hpp'}
        self.assertEqual(set(basenames), expected)
    
    def test_scan_directory_recursive(self):
        """Test scanning directory with recursion."""
        files = self.scanner.scan(self.temp_dir, recursive=True)
        
        # Should find all cpp/h files including nested ones
        basenames = [os.path.basename(f) for f in files]
        expected = {'test.cpp', 'test.h', 'test.hpp', 'nested.cpp', 'nested.h', 'very_nested.cxx'}
        self.assertEqual(set(basenames), expected)
    
    def test_include_headers(self):
        """Test including header files in scan."""
        files = self.scanner.scan(self.temp_dir, recursive=True, include_headers=True)
        
        # Should include both source and header files
        basenames = [os.path.basename(f) for f in files]
        self.assertIn('test.h', basenames)
        self.assertIn('test.hpp', basenames)
        self.assertIn('nested.h', basenames)
    
    def test_exclude_headers(self):
        """Test excluding header files from scan."""
        files = self.scanner.scan(self.temp_dir, recursive=True, include_headers=False)
        
        # Should not include header files
        basenames = [os.path.basename(f) for f in files]
        self.assertNotIn('test.h', basenames)
        self.assertNotIn('test.hpp', basenames)
        self.assertNotIn('nested.h', basenames)
    
    def test_exclude_patterns(self):
        """Test excluding files by patterns."""
        exclude_patterns = ['*nested*', '*.h']
        files = self.scanner.scan(
            self.temp_dir, 
            recursive=True, 
            include_headers=True,
            exclude_patterns=exclude_patterns
        )
        
        basenames = [os.path.basename(f) for f in files]
        # Should exclude nested files and .h files
        self.assertNotIn('nested.cpp', basenames)
        self.assertNotIn('nested.h', basenames)
        self.assertNotIn('test.h', basenames)
        self.assertIn('test.cpp', basenames)  # Should still include .cpp files
    
    def test_nonexistent_path(self):
        """Test handling of non-existent paths."""
        with self.assertRaises(ValueError):
            self.scanner.scan('/nonexistent/path')
    
    def test_get_supported_extensions(self):
        """Test getting supported file extensions."""
        extensions = self.scanner.get_supported_extensions(include_headers=False)
        self.assertIn('.cpp', extensions)
        self.assertIn('.cxx', extensions)
        self.assertNotIn('.h', extensions)
        
        extensions_with_headers = self.scanner.get_supported_extensions(include_headers=True)
        self.assertIn('.h', extensions_with_headers)
        self.assertIn('.hpp', extensions_with_headers)
    
    def test_file_info(self):
        """Test getting file information."""
        test_file = os.path.join(self.temp_dir, 'test.cpp')
        info = self.scanner.get_file_info(test_file)
        
        self.assertEqual(info['name'], 'test.cpp')
        self.assertEqual(info['extension'], '.cpp')
        self.assertTrue(info['is_source'])
        self.assertFalse(info['is_header'])
        self.assertGreater(info['size_bytes'], 0)
    
    def test_directory_stats(self):
        """Test getting directory statistics."""
        stats = self.scanner.get_directory_stats(self.temp_dir, recursive=True, include_headers=True)
        
        self.assertEqual(stats['directory'], self.temp_dir)
        self.assertGreater(stats['total_files'], 0)
        self.assertGreater(stats['source_files'], 0)
        self.assertGreater(stats['header_files'], 0)
        self.assertTrue(stats['recursive_scan'])
        self.assertTrue(stats['included_headers'])


if __name__ == '__main__':
    unittest.main()