"""
Unit tests for the validation module.
Tests directive validation, error detection, and semantic analysis.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.validation import DirectiveValidator
from src.data_models import (
    Directive, DirectiveType, FileAnalysisResult, 
    ValidationError, ErrorSeverity
)


class TestDirectiveValidator(unittest.TestCase):
    """Test cases for the DirectiveValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = DirectiveValidator()
    
    def create_directive(self, directive_type, content, symbol_name=None, condition=None, line_number=1):
        """Helper method to create test directives."""
        directive = Directive(
            type=directive_type,
            content=content,
            line_number=line_number,
            file_path="test.cpp",
            symbol_name=symbol_name,
            condition=condition
        )
        return directive
    
    def test_validate_valid_define(self):
        """Test validation of valid #define directive."""
        directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define VALID_SYMBOL 42",
            symbol_name="VALID_SYMBOL"
        )
        
        errors = self.validator._validate_define_directive(directive)
        self.assertEqual(len(errors), 0)
    
    def test_validate_define_missing_symbol(self):
        """Test validation of #define without symbol name."""
        directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define",
            symbol_name=None
        )
        
        errors = self.validator._validate_define_directive(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_define_invalid_symbol(self):
        """Test validation of #define with invalid symbol name."""
        directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define 123_INVALID 42",
            symbol_name="123_INVALID"
        )
        
        errors = self.validator._validate_define_directive(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_define_reserved_identifier(self):
        """Test validation of #define with reserved identifier in strict mode."""
        self.validator.strict_mode = True
        directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define _RESERVED_NAME 42",
            symbol_name="_RESERVED_NAME"
        )
        
        errors = self.validator._validate_define_directive(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.WARNING)
    
    def test_validate_ifdef_valid(self):
        """Test validation of valid #ifdef directive."""
        directive = self.create_directive(
            DirectiveType.IFDEF,
            "#ifdef DEBUG",
            symbol_name="DEBUG"
        )
        
        errors = self.validator._validate_ifdef_directive(directive)
        self.assertEqual(len(errors), 0)
    
    def test_validate_ifdef_missing_symbol(self):
        """Test validation of #ifdef without symbol name."""
        directive = self.create_directive(
            DirectiveType.IFDEF,
            "#ifdef",
            symbol_name=None
        )
        
        errors = self.validator._validate_ifdef_directive(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_if_valid_condition(self):
        """Test validation of valid #if directive."""
        directive = self.create_directive(
            DirectiveType.IF,
            "#if defined(DEBUG) && VERSION > 2",
            condition="defined(DEBUG) && VERSION > 2"
        )
        
        errors = self.validator._validate_if_directive(directive)
        self.assertEqual(len(errors), 0)
    
    def test_validate_if_empty_condition(self):
        """Test validation of #if without condition."""
        directive = self.create_directive(
            DirectiveType.IF,
            "#if",
            condition=None
        )
        
        errors = self.validator._validate_if_directive(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_if_unbalanced_parentheses(self):
        """Test validation of #if with unbalanced parentheses."""
        directive = self.create_directive(
            DirectiveType.IF,
            "#if (defined(DEBUG) && VERSION > 2",
            condition="(defined(DEBUG) && VERSION > 2"
        )
        
        errors = self.validator._validate_condition_expression(directive)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_directive_balance_simple(self):
        """Test validation of simple balanced directives."""
        directives = [
            self.create_directive(DirectiveType.IFDEF, "#ifdef DEBUG", "DEBUG", line_number=1),
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 3", "LOG_LEVEL", line_number=2),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=3)
        ]
        
        errors = self.validator._validate_directive_balance(directives)
        self.assertEqual(len(errors), 0)
    
    def test_validate_directive_balance_unmatched_ifdef(self):
        """Test validation of unmatched #ifdef."""
        directives = [
            self.create_directive(DirectiveType.IFDEF, "#ifdef DEBUG", "DEBUG", line_number=1),
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 3", "LOG_LEVEL", line_number=2)
            # Missing #endif
        ]
        
        errors = self.validator._validate_directive_balance(directives)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_directive_balance_orphaned_endif(self):
        """Test validation of orphaned #endif."""
        directives = [
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 3", "LOG_LEVEL", line_number=1),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=2)  # Orphaned
        ]
        
        errors = self.validator._validate_directive_balance(directives)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_directive_balance_orphaned_else(self):
        """Test validation of orphaned #else."""
        directives = [
            self.create_directive(DirectiveType.ELSE, "#else", line_number=1)  # Orphaned
        ]
        
        errors = self.validator._validate_directive_balance(directives)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.ERROR)
    
    def test_validate_directive_balance_nested(self):
        """Test validation of nested balanced directives."""
        directives = [
            self.create_directive(DirectiveType.IFDEF, "#ifdef DEBUG", "DEBUG", line_number=1),
            self.create_directive(DirectiveType.IFNDEF, "#ifndef RELEASE", "RELEASE", line_number=2),
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 3", "LOG_LEVEL", line_number=3),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=4),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=5)
        ]
        
        errors = self.validator._validate_directive_balance(directives)
        self.assertEqual(len(errors), 0)
    
    def test_check_duplicate_defines(self):
        """Test checking for duplicate #define directives."""
        file_result = FileAnalysisResult("test.cpp")
        
        # Add duplicate defines
        define1 = self.create_directive(DirectiveType.DEFINE, "#define SYMBOL 1", "SYMBOL", line_number=1)
        define2 = self.create_directive(DirectiveType.DEFINE, "#define SYMBOL 2", "SYMBOL", line_number=5)
        
        file_result.add_directive(define1)
        file_result.add_directive(define2)
        
        errors = self.validator._check_duplicate_defines(file_result)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.WARNING)
    
    def test_check_undefined_symbols(self):
        """Test checking for references to undefined symbols."""
        file_result = FileAnalysisResult("test.cpp")
        
        # Add ifdef referencing undefined symbol
        ifdef_directive = self.create_directive(
            DirectiveType.IFDEF, 
            "#ifdef UNDEFINED_SYMBOL", 
            "UNDEFINED_SYMBOL",
            line_number=1
        )
        file_result.add_directive(ifdef_directive)
        
        errors = self.validator._check_undefined_symbols(file_result)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.WARNING)
    
    def test_check_naming_conventions(self):
        """Test checking naming convention compliance."""
        file_result = FileAnalysisResult("test.cpp")
        
        # Add define with lowercase name (should trigger warning in strict mode)
        define_directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define lower_case_macro 1",
            "lower_case_macro",
            line_number=1
        )
        file_result.add_directive(define_directive)
        
        errors = self.validator._check_naming_conventions(file_result)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].severity, ErrorSeverity.WARNING)
    
    def test_validate_complete_file(self):
        """Test complete validation of a file result."""
        file_result = FileAnalysisResult("test.cpp")
        
        # Add various directives
        directives = [
            self.create_directive(DirectiveType.IFNDEF, "#ifndef TEST_H", "TEST_H", line_number=1),
            self.create_directive(DirectiveType.DEFINE, "#define TEST_H", "TEST_H", line_number=2),
            self.create_directive(DirectiveType.IFDEF, "#ifdef DEBUG", "DEBUG", line_number=3),
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 3", "LOG_LEVEL", line_number=4),
            self.create_directive(DirectiveType.ELSE, "#else", line_number=5),
            self.create_directive(DirectiveType.DEFINE, "#define LOG_LEVEL 1", "LOG_LEVEL", line_number=6),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=7),
            self.create_directive(DirectiveType.ENDIF, "#endif", line_number=8)
        ]
        
        for directive in directives:
            file_result.add_directive(directive)
        
        errors = self.validator.validate(file_result, strict=False, check_balance=True)
        
        # Should have some warnings but no critical errors for this well-formed structure
        critical_errors = [e for e in errors if e.severity == ErrorSeverity.ERROR]
        self.assertEqual(len(critical_errors), 0)
    
    def test_is_valid_identifier(self):
        """Test identifier validation."""
        # Valid identifiers
        self.assertTrue(self.validator._is_valid_identifier("valid_name"))
        self.assertTrue(self.validator._is_valid_identifier("_underscore"))
        self.assertTrue(self.validator._is_valid_identifier("Name123"))
        self.assertTrue(self.validator._is_valid_identifier("UPPER_CASE"))
        
        # Invalid identifiers
        self.assertFalse(self.validator._is_valid_identifier("123invalid"))
        self.assertFalse(self.validator._is_valid_identifier("invalid-name"))
        self.assertFalse(self.validator._is_valid_identifier("invalid.name"))
        self.assertFalse(self.validator._is_valid_identifier(""))
    
    def test_is_reserved_identifier(self):
        """Test reserved identifier detection."""
        # Reserved patterns
        self.assertTrue(self.validator._is_reserved_identifier("_reserved"))
        self.assertTrue(self.validator._is_reserved_identifier("__double_underscore"))
        self.assertTrue(self.validator._is_reserved_identifier("name__with__double"))
        
        # Non-reserved
        self.assertFalse(self.validator._is_reserved_identifier("normal_name"))
        self.assertFalse(self.validator._is_reserved_identifier("NORMAL_NAME"))
    
    def test_strict_mode_validation(self):
        """Test additional validation in strict mode."""
        file_result = FileAnalysisResult("test.cpp")
        
        # Add define with potentially problematic name
        define_directive = self.create_directive(
            DirectiveType.DEFINE,
            "#define _reserved_name 1",
            "_reserved_name",
            line_number=1
        )
        file_result.add_directive(define_directive)
        
        # Test with strict mode off
        errors_normal = self.validator.validate(file_result, strict=False)
        
        # Test with strict mode on
        errors_strict = self.validator.validate(file_result, strict=True)
        
        # Strict mode should produce more warnings
        self.assertGreaterEqual(len(errors_strict), len(errors_normal))


if __name__ == '__main__':
    unittest.main()