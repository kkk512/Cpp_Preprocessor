"""
Data models for the C++ Preprocessor Directive Analysis Tool.
Defines the core data structures used throughout the application.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class DirectiveType(Enum):
    """Enumeration of preprocessor directive types."""
    DEFINE = "define"
    IFDEF = "ifdef"
    IFNDEF = "ifndef"
    IF = "if"
    ELSE = "else"
    ELIF = "elif"
    ENDIF = "endif"
    UNDEF = "undef"
    INCLUDE = "include"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Directive:
    """
    Represents a single preprocessor directive.
    
    Attributes:
        type: Type of the directive (define, ifdef, etc.)
        content: Full directive content as string
        line_number: Line number in source file (1-based)
        file_path: Path to the source file
        condition: Conditional expression (if applicable)
        context: Active context stack when directive was found
        symbol_name: Symbol name for define/ifdef directives
    """
    type: DirectiveType
    content: str
    line_number: int
    file_path: str
    condition: Optional[str] = None
    context: List[str] = field(default_factory=list)
    symbol_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert directive to dictionary for serialization."""
        return {
            "type": self.type.value,
            "content": self.content,
            "line_number": self.line_number,
            "file_path": self.file_path,
            "condition": self.condition,
            "context": self.context.copy(),
            "symbol_name": self.symbol_name
        }


@dataclass
class ContextStack:
    """
    Represents the current conditional compilation context.
    
    Attributes:
        conditions: Stack of active conditions
        negations: Whether each condition is negated
        depth: Current nesting depth
        file_context: Current file being processed
    """
    conditions: List[str] = field(default_factory=list)
    negations: List[bool] = field(default_factory=list)
    depth: int = 0
    file_context: str = ""

    def push_condition(self, condition: str, negated: bool = False) -> None:
        """Push a new condition onto the stack."""
        self.conditions.append(condition)
        self.negations.append(negated)
        self.depth += 1

    def pop_condition(self) -> Optional[str]:
        """Pop the top condition from the stack."""
        if self.depth > 0:
            condition = self.conditions.pop()
            self.negations.pop()
            self.depth -= 1
            return condition
        return None

    def get_current_context(self) -> List[str]:
        """Get the current context as a list of condition strings."""
        context = []
        for i, condition in enumerate(self.conditions):
            if self.negations[i]:
                context.append(f"!{condition}")
            else:
                context.append(condition)
        return context

    def get_context_expression(self) -> str:
        """Get the current context as a boolean expression string."""
        if not self.conditions:
            return ""
        
        expressions = []
        for i, condition in enumerate(self.conditions):
            if self.negations[i]:
                expressions.append(f"!{condition}")
            else:
                expressions.append(condition)
        
        return " && ".join(expressions)

    def copy(self) -> 'ContextStack':
        """Create a deep copy of the context stack."""
        return ContextStack(
            conditions=self.conditions.copy(),
            negations=self.negations.copy(),
            depth=self.depth,
            file_context=self.file_context
        )


@dataclass
class ValidationError:
    """
    Represents a validation error found during analysis.
    
    Attributes:
        severity: Error severity level
        message: Human-readable error message
        file_path: Path to the file containing the error
        line_number: Line number where error occurred
        directive_content: Content of the problematic directive
        suggestion: Suggested fix (if available)
    """
    severity: ErrorSeverity
    message: str
    file_path: str
    line_number: int
    directive_content: str = ""
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "directive_content": self.directive_content,
            "suggestion": self.suggestion
        }


@dataclass
class FileAnalysisResult:
    """
    Represents the analysis result for a single file.
    
    Attributes:
        file_path: Path to the analyzed file
        directives: List of all directives found in the file
        defines: List of define directives with their contexts
        errors: List of validation errors found
        line_count: Total number of lines in the file
        directive_count: Total number of directives found
    """
    file_path: str
    directives: List[Directive] = field(default_factory=list)
    defines: List[Directive] = field(default_factory=list)
    errors: List[ValidationError] = field(default_factory=list)
    line_count: int = 0
    directive_count: int = 0

    def add_directive(self, directive: Directive) -> None:
        """Add a directive to the results."""
        self.directives.append(directive)
        self.directive_count += 1
        
        if directive.type == DirectiveType.DEFINE:
            self.defines.append(directive)

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error to the results."""
        self.errors.append(error)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "file_path": self.file_path,
            "directives": [d.to_dict() for d in self.directives],
            "defines": [d.to_dict() for d in self.defines],
            "errors": [e.to_dict() for e in self.errors],
            "line_count": self.line_count,
            "directive_count": self.directive_count
        }


@dataclass
class AnalysisResult:
    """
    Represents the complete analysis result for all processed files.
    
    Attributes:
        file_results: Dictionary mapping file paths to their analysis results
        total_files: Total number of files processed
        total_directives: Total number of directives found
        total_defines: Total number of define directives found
        conditions_usage: Dictionary mapping conditions to usage count
        dependency_graph: Symbol dependency relationships
        validation_errors: All validation errors found
    """
    file_results: Dict[str, FileAnalysisResult] = field(default_factory=dict)
    total_files: int = 0
    total_directives: int = 0
    total_defines: int = 0
    conditions_usage: Dict[str, int] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    validation_errors: List[ValidationError] = field(default_factory=list)

    def add_file_result(self, result: FileAnalysisResult) -> None:
        """Add a file analysis result to the overall results."""
        self.file_results[result.file_path] = result
        self.total_files += 1
        self.total_directives += result.directive_count
        self.total_defines += len(result.defines)
        self.validation_errors.extend(result.errors)

        # Update conditions usage count
        for directive in result.directives:
            if directive.condition:
                self.conditions_usage[directive.condition] = \
                    self.conditions_usage.get(directive.condition, 0) + 1

    def get_all_defines(self) -> List[Directive]:
        """Get all define directives from all files."""
        all_defines = []
        for result in self.file_results.values():
            all_defines.extend(result.defines)
        return all_defines

    def get_defines_by_context(self) -> Dict[str, List[Directive]]:
        """Group define directives by their context expressions."""
        defines_by_context = {}
        for define in self.get_all_defines():
            context_expr = " && ".join(define.context) if define.context else "global"
            if context_expr not in defines_by_context:
                defines_by_context[context_expr] = []
            defines_by_context[context_expr].append(define)
        return defines_by_context

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "file_results": {path: result.to_dict() 
                           for path, result in self.file_results.items()},
            "total_files": self.total_files,
            "total_directives": self.total_directives,
            "total_defines": self.total_defines,
            "conditions_usage": self.conditions_usage,
            "dependency_graph": self.dependency_graph,
            "validation_errors": [e.to_dict() for e in self.validation_errors]
        }