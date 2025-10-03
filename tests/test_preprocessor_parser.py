"""
Unit tests for the preprocessor parser module.
Tests directive parsing, validation, and error handling.
"""

import unittest
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.preprocessor_parser import PreprocessorParser
from src.data_models import DirectiveType, ErrorSeverity


class TestPreprocessorParser(unittest.TestCase):
    """Test cases for the PreprocessorParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = PreprocessorParser()
    
    def test_parse_define_directive(self):
        """Test parsing #define directives."""
        line = "#define MAX_SIZE 1024"
        directive = self.parser._parse_line(line, 1, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.DEFINE)
        self.assertEqual(directive.symbol_name, "MAX_SIZE")
        self.assertEqual(directive.content, "#define MAX_SIZE 1024")
        self.assertEqual(directive.line_number, 1)
    
    def test_parse_ifdef_directive(self):
        """Test parsing #ifdef directives."""
        line = "#ifdef DEBUG"
        directive = self.parser._parse_line(line, 5, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.IFDEF)
        self.assertEqual(directive.symbol_name, "DEBUG")
        self.assertEqual(directive.condition, "DEBUG")
    
    def test_parse_ifndef_directive(self):
        """Test parsing #ifndef directives."""
        line = "#ifndef RELEASE"
        directive = self.parser._parse_line(line, 3, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.IFNDEF)
        self.assertEqual(directive.symbol_name, "RELEASE")
        self.assertEqual(directive.condition, "!RELEASE")
    
    def test_parse_if_directive(self):
        """Test parsing #if directives."""
        line = "#if defined(WINDOWS) && DEBUG_LEVEL > 2"
        directive = self.parser._parse_line(line, 8, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.IF)
        self.assertEqual(directive.condition, "defined(WINDOWS) && DEBUG_LEVEL > 2")
    
    def test_parse_else_directive(self):
        """Test parsing #else directives."""
        line = "#else"
        directive = self.parser._parse_line(line, 10, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.ELSE)
    
    def test_parse_elif_directive(self):
        """Test parsing #elif directives."""
        line = "#elif defined(LINUX)"
        directive = self.parser._parse_line(line, 12, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.ELIF)
        self.assertEqual(directive.condition, "defined(LINUX)")
    
    def test_parse_endif_directive(self):
        """Test parsing #endif directives."""
        line = "#endif"
        directive = self.parser._parse_line(line, 15, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.ENDIF)
    
    def test_parse_include_directive(self):
        """Test parsing #include directives."""
        line = '#include "config.h"'
        directive = self.parser._parse_line(line, 2, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.INCLUDE)
        self.assertEqual(directive.condition, "config.h")
    
    def test_parse_undef_directive(self):
        """Test parsing #undef directives."""
        line = "#undef TEMP_MACRO"
        directive = self.parser._parse_line(line, 20, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.UNDEF)
        self.assertEqual(directive.symbol_name, "TEMP_MACRO")
    
    def test_parse_unknown_directive(self):
        """Test parsing unknown directives."""
        line = "#pragma once"
        directive = self.parser._parse_line(line, 1, "test.cpp")
        
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.UNKNOWN)
    
    def test_parse_non_directive_line(self):
        """Test parsing non-directive lines."""
        line = "int main() { return 0; }"
        directive = self.parser._parse_line(line, 25, "test.cpp")
        
        self.assertIsNone(directive)
    
    def test_parse_lines(self):
        """Test parsing multiple lines."""
        lines = [
            "#ifndef CONFIG_H",
            "#define CONFIG_H",
            "#ifdef DEBUG",
            "    #define LOG_LEVEL 3",
            "#else",
            "    #define LOG_LEVEL 1", 
            "#endif",
            "#endif"
        ]
        
        directives = self.parser.parse_lines(lines, "config.h")
        
        self.assertEqual(len(directives), 6)  # Should find 6 directives
        self.assertEqual(directives[0].type, DirectiveType.IFNDEF)
        self.assertEqual(directives[1].type, DirectiveType.DEFINE)
        self.assertEqual(directives[2].type, DirectiveType.IFDEF)
        self.assertEqual(directives[3].type, DirectiveType.DEFINE)
        self.assertEqual(directives[4].type, DirectiveType.ELSE)
        self.assertEqual(directives[5].type, DirectiveType.ENDIF)
    
    def test_parse_file(self):
        """Test parsing an actual file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write("""#ifndef TEST_H
#define TEST_H

#ifdef DEBUG
    #define LOG_ENABLED 1
#else
    #define LOG_ENABLED 0
#endif

#include <iostream>

#endif // TEST_H
""")
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            self.assertEqual(result.file_path, temp_file)
            self.assertGreater(result.directive_count, 0)
            self.assertGreater(len(result.directives), 0)
            
            # Check specific directives
            directive_types = [d.type for d in result.directives]
            self.assertIn(DirectiveType.IFNDEF, directive_types)
            self.assertIn(DirectiveType.DEFINE, directive_types)
            self.assertIn(DirectiveType.IFDEF, directive_types)
            self.assertIn(DirectiveType.INCLUDE, directive_types)
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_define_syntax(self):
        """Test validating #define directive syntax."""
        # Valid define
        line = "#define VALID_NAME 42"
        directive = self.parser._parse_line(line, 1, "test.cpp")
        errors = self.parser.validate_directive_syntax(directive)
        self.assertEqual(len(errors), 0)
        
        # Invalid define - missing name
        line = "#define"
        directive = self.parser._parse_line(line, 2, "test.cpp")
        if directive:  # Parser might not create directive for malformed syntax
            errors = self.parser.validate_directive_syntax(directive)
            self.assertGreater(len(errors), 0)
    
    def test_balanced_parentheses(self):
        """Test balanced parentheses checking."""
        # Balanced
        self.assertTrue(self.parser._check_balanced_parentheses("(a && b) || (c && d)"))
        
        # Unbalanced - missing closing
        self.assertFalse(self.parser._check_balanced_parentheses("(a && b || c"))
        
        # Unbalanced - extra closing
        self.assertFalse(self.parser._check_balanced_parentheses("a && b) || c"))
        
        # No parentheses
        self.assertTrue(self.parser._check_balanced_parentheses("a && b || c"))
    
    def test_extract_symbol_names(self):
        """Test extracting symbol names from directives."""
        lines = [
            "#define SYMBOL1 1",
            "#define SYMBOL2 2", 
            "#ifdef SYMBOL3",
            "#endif"
        ]
        
        directives = self.parser.parse_lines(lines, "test.cpp")
        symbols = self.parser.extract_symbol_names(directives)
        
        self.assertEqual(set(symbols), {"SYMBOL1", "SYMBOL2"})
    
    def test_extract_conditions(self):
        """Test extracting conditions from directives."""
        lines = [
            "#ifdef DEBUG",
            "#if defined(WINDOWS) && VERSION > 2",
            "#elif defined(LINUX)",
            "#endif"
        ]
        
        directives = self.parser.parse_lines(lines, "test.cpp")
        conditions = self.parser.extract_conditions(directives)
        
        expected = {"DEBUG", "defined(WINDOWS) && VERSION > 2", "defined(LINUX)"}
        self.assertEqual(set(conditions), expected)
    
    def test_get_directive_statistics(self):
        """Test getting directive statistics."""
        lines = [
            "#define SYMBOL1 1",
            "#define SYMBOL2 2",
            "#ifdef DEBUG", 
            "#define SYMBOL3 3",
            "#endif"
        ]
        
        directives = self.parser.parse_lines(lines, "test.cpp")
        stats = self.parser.get_directive_statistics(directives)
        
        self.assertEqual(stats['total_directives'], 5)
        self.assertEqual(stats['by_type']['define'], 3)
        self.assertEqual(stats['by_type']['ifdef'], 1)
        self.assertEqual(stats['by_type']['endif'], 1)
        self.assertEqual(stats['unique_symbols'], 3)
    
    def test_find_matching_endif(self):
        """Test finding matching #endif directives."""
        lines = [
            "#ifdef LEVEL1",     # 0
            "  #ifdef LEVEL2",   # 1
            "    #define TEST",  # 2
            "  #endif",          # 3 - matches index 1
            "#endif"             # 4 - matches index 0
        ]
        
        directives = self.parser.parse_lines(lines, "test.cpp")
        
        # Find endif for first ifdef
        endif_index = self.parser.find_matching_endif(directives, 0)
        self.assertEqual(endif_index, 4)
        
        # Find endif for nested ifdef
        endif_index = self.parser.find_matching_endif(directives, 1)
        self.assertEqual(endif_index, 3)


if __name__ == '__main__':
    unittest.main()