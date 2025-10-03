"""
Validation module for syntax checking and error detection in preprocessor directives.
Provides comprehensive validation of directive syntax, nesting, and semantic correctness.
"""

from typing import List, Dict, Set, Optional
from .data_models import (
    Directive, DirectiveType, FileAnalysisResult, 
    ValidationError, ErrorSeverity
)


class DirectiveValidator:
    """
    Validates preprocessor directives for syntax errors, nesting issues, and semantic problems.
    """
    
    def __init__(self):
        self.strict_mode = False
        self.check_balance = True
        
    def validate(self, 
                 file_result: FileAnalysisResult, 
                 strict: bool = False, 
                 check_balance: bool = True) -> List[ValidationError]:
        """
        Perform comprehensive validation of preprocessor directives in a file.
        
        Args:
            file_result: File analysis result to validate
            strict: Enable strict validation rules
            check_balance: Check directive nesting balance
        
        Returns:
            List of validation errors found
        """
        self.strict_mode = strict
        self.check_balance = check_balance
        
        errors = []
        
        # Basic syntax validation for each directive
        for directive in file_result.directives:
            errors.extend(self._validate_directive_syntax(directive))
        
        # Check directive nesting and balance
        if check_balance:
            errors.extend(self._validate_directive_balance(file_result.directives))
        
        # Semantic validation
        errors.extend(self._validate_semantic_rules(file_result))
        
        # Strict mode additional checks
        if strict:
            errors.extend(self._validate_strict_rules(file_result))
        
        return errors
    
    def _validate_directive_syntax(self, directive: Directive) -> List[ValidationError]:
        """
        Validate the syntax of a single directive.
        
        Args:
            directive: Directive to validate
        
        Returns:
            List of validation errors
        """
        errors = []
        
        if directive.type == DirectiveType.DEFINE:
            errors.extend(self._validate_define_directive(directive))
        elif directive.type == DirectiveType.IFDEF:
            errors.extend(self._validate_ifdef_directive(directive))
        elif directive.type == DirectiveType.IFNDEF:
            errors.extend(self._validate_ifndef_directive(directive))
        elif directive.type == DirectiveType.IF:
            errors.extend(self._validate_if_directive(directive))
        elif directive.type == DirectiveType.ELIF:
            errors.extend(self._validate_elif_directive(directive))
        elif directive.type == DirectiveType.UNDEF:
            errors.extend(self._validate_undef_directive(directive))
        elif directive.type == DirectiveType.INCLUDE:
            errors.extend(self._validate_include_directive(directive))
        elif directive.type == DirectiveType.UNKNOWN:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message=f"Unknown preprocessor directive: {directive.content}",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_define_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #define directive."""
        errors = []
        
        if not directive.symbol_name:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Define directive missing symbol name",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a valid symbol name after #define"
            ))
        else:
            # Check symbol name validity
            if not self._is_valid_identifier(directive.symbol_name):
                errors.append(ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message=f"Invalid symbol name '{directive.symbol_name}'",
                    file_path=directive.file_path,
                    line_number=directive.line_number,
                    directive_content=directive.content,
                    suggestion="Symbol names must start with letter or underscore, followed by letters, digits, or underscores"
                ))
            
            # Check for reserved identifiers in strict mode
            if self.strict_mode and self._is_reserved_identifier(directive.symbol_name):
                errors.append(ValidationError(
                    severity=ErrorSeverity.WARNING,
                    message=f"Symbol name '{directive.symbol_name}' may conflict with reserved identifiers",
                    file_path=directive.file_path,
                    line_number=directive.line_number,
                    directive_content=directive.content,
                    suggestion="Avoid using identifiers that start with underscore or contain double underscores"
                ))
        
        return errors
    
    def _validate_ifdef_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #ifdef directive."""
        errors = []
        
        if not directive.symbol_name:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="ifdef directive missing symbol name",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a symbol name after #ifdef"
            ))
        elif not self._is_valid_identifier(directive.symbol_name):
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Invalid symbol name '{directive.symbol_name}' in ifdef",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_ifndef_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #ifndef directive."""
        errors = []
        
        if not directive.symbol_name:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="ifndef directive missing symbol name",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a symbol name after #ifndef"
            ))
        elif not self._is_valid_identifier(directive.symbol_name):
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Invalid symbol name '{directive.symbol_name}' in ifndef",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_if_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #if directive."""
        errors = []
        
        if not directive.condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="if directive missing condition expression",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a condition expression after #if"
            ))
        else:
            # Validate condition syntax
            errors.extend(self._validate_condition_expression(directive))
        
        return errors
    
    def _validate_elif_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #elif directive."""
        errors = []
        
        if not directive.condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="elif directive missing condition expression",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a condition expression after #elif"
            ))
        else:
            # Validate condition syntax
            errors.extend(self._validate_condition_expression(directive))
        
        return errors
    
    def _validate_undef_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #undef directive."""
        errors = []
        
        if not directive.symbol_name:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="undef directive missing symbol name",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a symbol name after #undef"
            ))
        elif not self._is_valid_identifier(directive.symbol_name):
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Invalid symbol name '{directive.symbol_name}' in undef",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_include_directive(self, directive: Directive) -> List[ValidationError]:
        """Validate #include directive."""
        errors = []
        
        if not directive.condition:  # condition field stores the include path
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="include directive missing file path",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Add a file path in quotes or angle brackets after #include"
            ))
        
        return errors
    
    def _validate_condition_expression(self, directive: Directive) -> List[ValidationError]:
        """Validate a conditional expression."""
        errors = []
        condition = directive.condition
        
        # Check for balanced parentheses
        if not self._check_balanced_parentheses(condition):
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Unbalanced parentheses in condition expression",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Check that all opening parentheses have matching closing parentheses"
            ))
        
        # Check for empty condition
        if not condition.strip():
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Empty condition expression",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        # Check for suspicious patterns in strict mode
        if self.strict_mode:
            errors.extend(self._validate_condition_patterns(directive))
        
        return errors
    
    def _validate_condition_patterns(self, directive: Directive) -> List[ValidationError]:
        """Validate condition patterns in strict mode."""
        errors = []
        condition = directive.condition
        
        # Check for potential assignment vs comparison
        if '=' in condition and '==' not in condition and '!=' not in condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message="Possible assignment operator in condition (use == for comparison)",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content,
                suggestion="Use == for comparison or != for inequality"
            ))
        
        # Check for bitwise vs logical operators
        if '&' in condition and '&&' not in condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message="Bitwise AND (&) found in condition, did you mean logical AND (&&)?",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        if '|' in condition and '||' not in condition:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message="Bitwise OR (|) found in condition, did you mean logical OR (||)?",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            ))
        
        return errors
    
    def _validate_directive_balance(self, directives: List[Directive]) -> List[ValidationError]:
        """Validate that conditional directives are properly balanced."""
        errors = []
        stack = []
        
        for directive in directives:
            if directive.type in [DirectiveType.IF, DirectiveType.IFDEF, DirectiveType.IFNDEF]:
                stack.append(directive)
            elif directive.type == DirectiveType.ENDIF:
                if not stack:
                    errors.append(ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message="Orphaned #endif without matching conditional directive",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion="Remove this #endif or add a matching conditional directive"
                    ))
                else:
                    stack.pop()
            elif directive.type in [DirectiveType.ELSE, DirectiveType.ELIF]:
                if not stack:
                    errors.append(ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message=f"Orphaned #{directive.type.value} without matching conditional directive",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion="Add a matching conditional directive"
                    ))
        
        # Check for unmatched opening conditionals
        for unmatched in stack:
            errors.append(ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Unmatched #{unmatched.type.value} directive missing #endif",
                file_path=unmatched.file_path,
                line_number=unmatched.line_number,
                directive_content=unmatched.content,
                suggestion="Add a matching #endif directive"
            ))
        
        return errors
    
    def _validate_semantic_rules(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Validate semantic rules and best practices."""
        errors = []
        
        # Check for duplicate defines
        errors.extend(self._check_duplicate_defines(file_result))
        
        # Check for undefined symbols in conditions
        errors.extend(self._check_undefined_symbols(file_result))
        
        # Check for include guard patterns
        if self.strict_mode:
            errors.extend(self._check_include_guards(file_result))
        
        return errors
    
    def _validate_strict_rules(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Additional validation rules for strict mode."""
        errors = []
        
        # Check for consistent naming conventions
        errors.extend(self._check_naming_conventions(file_result))
        
        # Check for potentially problematic macro definitions
        errors.extend(self._check_macro_definitions(file_result))
        
        return errors
    
    def _check_duplicate_defines(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Check for duplicate #define directives."""
        errors = []
        defined_symbols = {}
        
        for directive in file_result.directives:
            if directive.type == DirectiveType.DEFINE and directive.symbol_name:
                if directive.symbol_name in defined_symbols:
                    first_def = defined_symbols[directive.symbol_name]
                    errors.append(ValidationError(
                        severity=ErrorSeverity.WARNING,
                        message=f"Symbol '{directive.symbol_name}' redefined",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion=f"First defined at line {first_def.line_number}"
                    ))
                else:
                    defined_symbols[directive.symbol_name] = directive
        
        return errors
    
    def _check_undefined_symbols(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Check for references to potentially undefined symbols."""
        errors = []
        defined_symbols = set()
        
        # Collect all defined symbols
        for directive in file_result.directives:
            if directive.type == DirectiveType.DEFINE and directive.symbol_name:
                defined_symbols.add(directive.symbol_name)
        
        # Check references in conditions
        for directive in file_result.directives:
            if directive.type in [DirectiveType.IFDEF, DirectiveType.IFNDEF] and directive.symbol_name:
                if directive.symbol_name not in defined_symbols:
                    errors.append(ValidationError(
                        severity=ErrorSeverity.WARNING,
                        message=f"Reference to potentially undefined symbol '{directive.symbol_name}'",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion="Ensure the symbol is defined before use"
                    ))
        
        return errors
    
    def _check_include_guards(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Check for proper include guard patterns in header files."""
        errors = []
        
        # Only check header files
        if not file_result.file_path.endswith(('.h', '.hpp', '.hxx')):
            return errors
        
        directives = file_result.directives
        if len(directives) < 3:
            return errors
        
        # Check for include guard pattern: #ifndef, #define, ... #endif
        if (directives[0].type == DirectiveType.IFNDEF and
            len(directives) > 1 and
            directives[1].type == DirectiveType.DEFINE and
            directives[-1].type == DirectiveType.ENDIF):
            
            guard_symbol = directives[0].symbol_name
            define_symbol = directives[1].symbol_name
            
            if guard_symbol != define_symbol:
                errors.append(ValidationError(
                    severity=ErrorSeverity.WARNING,
                    message=f"Include guard mismatch: {guard_symbol} vs {define_symbol}",
                    file_path=file_result.file_path,
                    line_number=directives[1].line_number,
                    directive_content=directives[1].content,
                    suggestion="Ensure #ifndef and #define use the same symbol"
                ))
        else:
            errors.append(ValidationError(
                severity=ErrorSeverity.WARNING,
                message="Header file missing proper include guards",
                file_path=file_result.file_path,
                line_number=1,
                suggestion="Add #ifndef/#define guard at the beginning and #endif at the end"
            ))
        
        return errors
    
    def _check_naming_conventions(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Check naming convention compliance."""
        errors = []
        
        for directive in file_result.directives:
            if directive.type == DirectiveType.DEFINE and directive.symbol_name:
                symbol = directive.symbol_name
                
                # Check for all uppercase convention for macros
                if not symbol.isupper() and '_' in symbol:
                    errors.append(ValidationError(
                        severity=ErrorSeverity.WARNING,
                        message=f"Macro '{symbol}' should be in UPPER_CASE by convention",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion="Use UPPER_CASE for macro names"
                    ))
        
        return errors
    
    def _check_macro_definitions(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """Check for potentially problematic macro definitions."""
        errors = []
        
        for directive in file_result.directives:
            if directive.type == DirectiveType.DEFINE:
                # Check for function-like macros without parentheses
                content = directive.content
                if '(' in content and ')' in content:
                    # This might be a function-like macro
                    errors.append(ValidationError(
                        severity=ErrorSeverity.WARNING,
                        message="Function-like macro detected - consider using inline functions",
                        file_path=directive.file_path,
                        line_number=directive.line_number,
                        directive_content=directive.content,
                        suggestion="Consider using constexpr functions instead of function-like macros"
                    ))
        
        return errors
    
    def _is_valid_identifier(self, identifier: str) -> bool:
        """Check if a string is a valid C++ identifier."""
        import re
        return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', identifier))
    
    def _is_reserved_identifier(self, identifier: str) -> bool:
        """Check if an identifier might be reserved."""
        # Check for leading underscore patterns that are reserved
        if identifier.startswith('_'):
            return True
        if '__' in identifier:
            return True
        return False
    
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