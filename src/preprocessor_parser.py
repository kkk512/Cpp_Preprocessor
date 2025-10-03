"""
Preprocessor parser module for tokenizing and parsing C++ preprocessor directives.
Handles extraction and analysis of #define, #ifdef, #ifndef, #if, #else, #elif, #endif directives.
"""

import re
import os
from typing import List, Optional, Tuple
from .data_models import (
    Directive, DirectiveType, FileAnalysisResult, 
    ValidationError, ErrorSeverity
)


class PreprocessorParser:
    """
    Parser for C++ preprocessor directives.
    Extracts directives from source files and creates structured representations.
    """
    
    # Regex patterns for different directive types
    DIRECTIVE_PATTERNS = {
        DirectiveType.DEFINE: re.compile(r'^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s*(.*?)(?://.*)?$'),
        DirectiveType.IFDEF: re.compile(r'^\s*#\s*ifdef\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?://.*)?$'),
        DirectiveType.IFNDEF: re.compile(r'^\s*#\s*ifndef\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?://.*)?$'),
        DirectiveType.IF: re.compile(r'^\s*#\s*if\s+(.+?)(?://.*)?$'),
        DirectiveType.ELSE: re.compile(r'^\s*#\s*else\s*(?://.*)?$'),
        DirectiveType.ELIF: re.compile(r'^\s*#\s*elif\s+(.+?)(?://.*)?$'),
        DirectiveType.ENDIF: re.compile(r'^\s*#\s*endif\s*(?://.*)?$'),
        DirectiveType.UNDEF: re.compile(r'^\s*#\s*undef\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?://.*)?$'),
        DirectiveType.INCLUDE: re.compile(r'^\s*#\s*include\s+[<"]([^">]+)[">]\s*(?://.*)?$'),
    }
    
    # General directive detection pattern
    GENERAL_DIRECTIVE = re.compile(r'^\s*#\s*([A-Za-z_][A-Za-z0-9_]*)')
    
    def __init__(self):
        self.current_file = ""
        self.line_number = 0
    
    def parse_file(self, file_path: str) -> FileAnalysisResult:
        """
        Parse a single C++ file for preprocessor directives.
        
        Args:
            file_path: Path to the C++ file to parse
        
        Returns:
            FileAnalysisResult containing all found directives and metadata
        """
        result = FileAnalysisResult(file_path=file_path)
        self.current_file = file_path
        
        if not os.path.exists(file_path):
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"File not found: {file_path}",
                file_path=file_path,
                line_number=0
            )
            result.add_error(error)
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            result.line_count = len(lines)
            
            for line_num, line in enumerate(lines, 1):
                self.line_number = line_num
                directive = self._parse_line(line, line_num, file_path)
                
                if directive:
                    result.add_directive(directive)
        
        except Exception as e:
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Failed to read file: {str(e)}",
                file_path=file_path,
                line_number=0
            )
            result.add_error(error)
        
        return result
    
    def _parse_line(self, line: str, line_number: int, file_path: str) -> Optional[Directive]:
        """
        Parse a single line for preprocessor directives.
        
        Args:
            line: Line content to parse
            line_number: Line number in the file
            file_path: Path to the source file
        
        Returns:
            Directive object if a directive is found, None otherwise
        """
        line = line.rstrip('\n\r')
        
        # Quick check if line contains a directive
        if not line.strip().startswith('#'):
            return None
        
        # Try to match against each directive type
        for directive_type, pattern in self.DIRECTIVE_PATTERNS.items():
            match = pattern.match(line)
            if match:
                return self._create_directive(
                    directive_type, line, line_number, file_path, match
                )
        
        # Check for unknown directive
        general_match = self.GENERAL_DIRECTIVE.match(line)
        if general_match:
            return self._create_directive(
                DirectiveType.UNKNOWN, line, line_number, file_path, general_match
            )
        
        return None
    
    def _create_directive(self, 
                         directive_type: DirectiveType, 
                         content: str, 
                         line_number: int, 
                         file_path: str,
                         match: re.Match) -> Directive:
        """
        Create a Directive object from parsed information.
        
        Args:
            directive_type: Type of the directive
            content: Full line content
            line_number: Line number in file
            file_path: Path to source file
            match: Regex match object
        
        Returns:
            Directive object
        """
        directive = Directive(
            type=directive_type,
            content=content.strip(),
            line_number=line_number,
            file_path=file_path
        )
        
        # Extract specific information based on directive type
        if directive_type == DirectiveType.DEFINE:
            directive.symbol_name = match.group(1)
            
        elif directive_type == DirectiveType.IFDEF:
            directive.condition = match.group(1)
            directive.symbol_name = match.group(1)
            
        elif directive_type == DirectiveType.IFNDEF:
            directive.condition = f"!{match.group(1)}"
            directive.symbol_name = match.group(1)
            
        elif directive_type == DirectiveType.IF:
            directive.condition = match.group(1).strip()
            
        elif directive_type == DirectiveType.ELIF:
            directive.condition = match.group(1).strip()
            
        elif directive_type == DirectiveType.UNDEF:
            directive.symbol_name = match.group(1)
            
        elif directive_type == DirectiveType.INCLUDE:
            directive.condition = match.group(1)  # Store included file path
        
        return directive
    
    def parse_lines(self, lines: List[str], file_path: str = "unknown") -> List[Directive]:
        """
        Parse a list of lines for preprocessor directives.
        
        Args:
            lines: List of lines to parse
            file_path: Path identifier for the source
        
        Returns:
            List of Directive objects found
        """
        directives = []
        
        for line_num, line in enumerate(lines, 1):
            directive = self._parse_line(line, line_num, file_path)
            if directive:
                directives.append(directive)
        
        return directives
    
    def validate_directive_syntax(self, directive: Directive) -> List[ValidationError]:
        """
        Validate the syntax of a preprocessor directive.
        
        Args:
            directive: Directive to validate
        
        Returns:
            List of validation errors found
        """
        errors = []
        
        if directive.type == DirectiveType.DEFINE:
            errors.extend(self._validate_define_syntax(directive))
        elif directive.type == DirectiveType.IF or directive.type == DirectiveType.ELIF:
            errors.extend(self._validate_condition_syntax(directive))
        elif directive.type == DirectiveType.UNKNOWN:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message=f"Unknown directive: {directive.content}",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_define_syntax(self, directive: Directive) -> List[ValidationError]:
        """Validate #define directive syntax."""
        errors = []
        
        if not directive.symbol_name:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Define directive missing symbol name",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        elif not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', directive.symbol_name):
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Invalid symbol name: {directive.symbol_name}",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Symbol names must start with letter or underscore"
            ))
        
        return errors
    
    def _validate_condition_syntax(self, directive: Directive) -> List[ValidationError]:
        """Validate condition syntax in #if/#elif directives."""
        errors = []
        
        if not directive.condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Conditional directive missing condition expression",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        else:
            # Basic validation - check for balanced parentheses
            if not self._check_balanced_parentheses(directive.condition):
                errors.append(ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message="Unbalanced parentheses in condition",
                    file_path=directive.file_path,
                    line_number=directive.line_number,
                    directive_content=directive.content
                ))
        
        return errors
    
    def _check_balanced_parentheses(self, expression: str) -> bool:
        """Check if parentheses are balanced in an expression."""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    def extract_symbol_names(self, directives: List[Directive]) -> List[str]:
        """
        Extract all symbol names from define directives.
        
        Args:
            directives: List of directives to process
        
        Returns:
            List of unique symbol names
        """
        symbols = set()
        for directive in directives:
            if directive.type == DirectiveType.DEFINE and directive.symbol_name:
                symbols.add(directive.symbol_name)
        return sorted(list(symbols))
    
    def extract_conditions(self, directives: List[Directive]) -> List[str]:
        """
        Extract all conditional expressions from directives.
        
        Args:
            directives: List of directives to process
        
        Returns:
            List of unique condition expressions
        """
        conditions = set()
        for directive in directives:
            if directive.condition and directive.type in [
                DirectiveType.IF, DirectiveType.ELIF, 
                DirectiveType.IFDEF, DirectiveType.IFNDEF
            ]:
                conditions.add(directive.condition)
        return sorted(list(conditions))
    
    def get_directive_statistics(self, directives: List[Directive]) -> dict:
        """
        Get statistics about the directives found.
        
        Args:
            directives: List of directives to analyze
        
        Returns:
            Dictionary containing statistics
        """
        stats = {
            'total_directives': len(directives),
            'by_type': {},
            'unique_symbols': len(self.extract_symbol_names(directives)),
            'unique_conditions': len(self.extract_conditions(directives))
        }
        
        for directive in directives:
            directive_type = directive.type.value
            stats['by_type'][directive_type] = stats['by_type'].get(directive_type, 0) + 1
        
        return stats
    
    def find_matching_endif(self, directives: List[Directive], start_index: int) -> Optional[int]:
        """
        Find the matching #endif for a conditional directive.
        
        Args:
            directives: List of all directives
            start_index: Index of the opening conditional directive
        
        Returns:
            Index of matching #endif, or None if not found
        """
        if start_index >= len(directives):
            return None
        
        start_directive = directives[start_index]
        if start_directive.type not in [DirectiveType.IF, DirectiveType.IFDEF, DirectiveType.IFNDEF]:
            return None
        
        nesting_level = 1
        
        for i in range(start_index + 1, len(directives)):
            directive = directives[i]
            
            if directive.type in [DirectiveType.IF, DirectiveType.IFDEF, DirectiveType.IFNDEF]:
                nesting_level += 1
            elif directive.type == DirectiveType.ENDIF:
                nesting_level -= 1
                if nesting_level == 0:
                    return i
        
        return None