"""
Context analyzer module for tracking conditional compilation contexts.
Analyzes the conditional compilation hierarchy and determines the context
under which each #define directive is declared.
"""

from typing import List, Dict, Optional, Set
from .data_models import (
    Directive, DirectiveType, FileAnalysisResult, 
    ContextStack, ValidationError, ErrorSeverity
)


class ContextAnalyzer:
    """
    Analyzes conditional compilation contexts in C++ preprocessor directives.
    Tracks the nested conditional blocks and determines the context for each directive.
    """
    
    def __init__(self):
        self.context_stack = ContextStack()
        self.dependency_graph: Dict[str, Set[str]] = {}
        
    def analyze(self, file_result: FileAnalysisResult) -> None:
        """
        Analyze the conditional compilation contexts for all directives in a file.
        
        Args:
            file_result: FileAnalysisResult to analyze and update with context information
        """
        self.context_stack = ContextStack()
        self.context_stack.file_context = file_result.file_path
        
        # Process directives in order to maintain proper context tracking
        for directive in file_result.directives:
            try:
                self._process_directive(directive, file_result)
            except Exception as e:
                error = ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message=f"Context analysis error: {str(e)}",
                    file_path=directive.file_path,
                    line_number=directive.line_number,
                    directive_content=directive.content
                )
                file_result.add_error(error)
        
        # Check for unmatched conditional blocks
        if self.context_stack.depth > 0:
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message=f"Unmatched conditional directive(s): {self.context_stack.depth} unclosed block(s)",
                file_path=file_result.file_path,
                line_number=file_result.line_count,
                suggestion="Add missing #endif directive(s)"
            )
            file_result.add_error(error)
    
    def _process_directive(self, directive: Directive, file_result: FileAnalysisResult) -> None:
        """
        Process a single directive and update the context accordingly.
        
        Args:
            directive: Directive to process
            file_result: Current file analysis result for error reporting
        """
        if directive.type == DirectiveType.IFDEF:
            self._handle_ifdef(directive)
        elif directive.type == DirectiveType.IFNDEF:
            self._handle_ifndef(directive)
        elif directive.type == DirectiveType.IF:
            self._handle_if(directive)
        elif directive.type == DirectiveType.ELSE:
            self._handle_else(directive, file_result)
        elif directive.type == DirectiveType.ELIF:
            self._handle_elif(directive, file_result)
        elif directive.type == DirectiveType.ENDIF:
            self._handle_endif(directive, file_result)
        elif directive.type == DirectiveType.DEFINE:
            self._handle_define(directive)
        elif directive.type == DirectiveType.UNDEF:
            self._handle_undef(directive)
    
    def _handle_ifdef(self, directive: Directive) -> None:
        """Handle #ifdef directive."""
        if directive.symbol_name:
            self.context_stack.push_condition(directive.symbol_name, negated=False)
            directive.context = self.context_stack.get_current_context()
    
    def _handle_ifndef(self, directive: Directive) -> None:
        """Handle #ifndef directive."""
        if directive.symbol_name:
            self.context_stack.push_condition(directive.symbol_name, negated=True)
            directive.context = self.context_stack.get_current_context()
    
    def _handle_if(self, directive: Directive) -> None:
        """Handle #if directive."""
        if directive.condition:
            # Parse the condition to extract dependencies
            dependencies = self._extract_dependencies_from_condition(directive.condition)
            for dep in dependencies:
                self._add_dependency(directive.condition, dep)
            
            self.context_stack.push_condition(directive.condition, negated=False)
            directive.context = self.context_stack.get_current_context()
    
    def _handle_else(self, directive: Directive, file_result: FileAnalysisResult) -> None:
        """Handle #else directive."""
        if self.context_stack.depth == 0:
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Orphaned #else directive without matching conditional",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            )
            file_result.add_error(error)
            return
        
        # Negate the top condition
        if self.context_stack.conditions:
            self.context_stack.negations[-1] = not self.context_stack.negations[-1]
            directive.context = self.context_stack.get_current_context()
    
    def _handle_elif(self, directive: Directive, file_result: FileAnalysisResult) -> None:
        """Handle #elif directive."""
        if self.context_stack.depth == 0:
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Orphaned #elif directive without matching conditional",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            )
            file_result.add_error(error)
            return
        
        # Replace the top condition with the new elif condition
        if directive.condition and self.context_stack.conditions:
            dependencies = self._extract_dependencies_from_condition(directive.condition)
            for dep in dependencies:
                self._add_dependency(directive.condition, dep)
            
            self.context_stack.conditions[-1] = directive.condition
            self.context_stack.negations[-1] = False
            directive.context = self.context_stack.get_current_context()
    
    def _handle_endif(self, directive: Directive, file_result: FileAnalysisResult) -> None:
        """Handle #endif directive."""
        if self.context_stack.depth == 0:
            error = ValidationError(
                severity=ErrorSeverity.ERROR,
                message="Orphaned #endif directive without matching conditional",
                file_path=directive.file_path,
                line_number=directive.line_number,
                directive_content=directive.content
            )
            file_result.add_error(error)
            return
        
        self.context_stack.pop_condition()
        directive.context = self.context_stack.get_current_context()
    
    def _handle_define(self, directive: Directive) -> None:
        """Handle #define directive."""
        # Assign current context to the define
        directive.context = self.context_stack.get_current_context()
        
        # Track dependencies if the define has a value that references other symbols
        if directive.symbol_name and directive.content:
            # Extract potential symbol references from the define value
            define_value = self._extract_define_value(directive.content)
            if define_value:
                dependencies = self._extract_symbol_references(define_value)
                for dep in dependencies:
                    self._add_dependency(directive.symbol_name, dep)
    
    def _handle_undef(self, directive: Directive) -> None:
        """Handle #undef directive."""
        directive.context = self.context_stack.get_current_context()
    
    def _extract_dependencies_from_condition(self, condition: str) -> Set[str]:
        """
        Extract symbol dependencies from a conditional expression.
        
        Args:
            condition: Conditional expression to analyze
        
        Returns:
            Set of symbol names referenced in the condition
        """
        import re
        
        # Remove common operators and whitespace to find symbol names
        # This is a simplified approach - a full C preprocessor would need more complex parsing
        symbols = set()
        
        # Remove operators, numbers, and common keywords
        cleaned = re.sub(r'[()&|!<>=+\-*/\s]', ' ', condition)
        cleaned = re.sub(r'\b\d+\b', ' ', cleaned)  # Remove numbers
        cleaned = re.sub(r'\bdefined\b', ' ', cleaned)  # Remove 'defined' keyword
        
        # Extract potential symbol names
        potential_symbols = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', cleaned)
        
        for symbol in potential_symbols:
            if symbol and not symbol.isdigit():
                symbols.add(symbol)
        
        return symbols
    
    def _extract_define_value(self, define_content: str) -> str:
        """
        Extract the value part of a #define directive.
        
        Args:
            define_content: Full #define directive content
        
        Returns:
            The value part of the define, or empty string if none
        """
        import re
        
        # Match #define SYMBOL VALUE
        match = re.match(r'^\s*#\s*define\s+[A-Za-z_][A-Za-z0-9_]*\s+(.*?)(?://.*)?$', define_content)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_symbol_references(self, text: str) -> Set[str]:
        """
        Extract symbol references from text (like macro values).
        
        Args:
            text: Text to analyze for symbol references
        
        Returns:
            Set of symbol names found
        """
        import re
        
        symbols = set()
        # Find potential symbol names in the text
        potential_symbols = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', text)
        
        for symbol in potential_symbols:
            if symbol and not symbol.isdigit():
                symbols.add(symbol)
        
        return symbols
    
    def _add_dependency(self, symbol: str, dependency: str) -> None:
        """
        Add a dependency relationship between symbols.
        
        Args:
            symbol: Symbol that depends on another
            dependency: Symbol that is depended upon
        """
        if symbol not in self.dependency_graph:
            self.dependency_graph[symbol] = set()
        self.dependency_graph[symbol].add(dependency)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the complete dependency graph as a dictionary.
        
        Returns:
            Dictionary mapping symbols to their dependencies
        """
        return {symbol: list(deps) for symbol, deps in self.dependency_graph.items()}
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the symbol dependency graph.
        
        Returns:
            List of circular dependency chains
        """
        cycles = []
        visited = set()
        path = []
        
        def dfs(symbol: str) -> None:
            if symbol in path:
                # Found a cycle
                cycle_start = path.index(symbol)
                cycle = path[cycle_start:] + [symbol]
                cycles.append(cycle)
                return
            
            if symbol in visited:
                return
            
            visited.add(symbol)
            path.append(symbol)
            
            if symbol in self.dependency_graph:
                for dependency in self.dependency_graph[symbol]:
                    dfs(dependency)
            
            path.pop()
        
        for symbol in self.dependency_graph:
            if symbol not in visited:
                dfs(symbol)
        
        return cycles
    
    def get_context_hierarchy(self, file_result: FileAnalysisResult) -> Dict[str, List[Directive]]:
        """
        Group directives by their context hierarchy.
        
        Args:
            file_result: File analysis result to process
        
        Returns:
            Dictionary mapping context expressions to lists of directives
        """
        hierarchy = {}
        
        for directive in file_result.directives:
            context_key = " && ".join(directive.context) if directive.context else "global"
            
            if context_key not in hierarchy:
                hierarchy[context_key] = []
            hierarchy[context_key].append(directive)
        
        return hierarchy
    
    def analyze_unreachable_code(self, file_result: FileAnalysisResult) -> List[ValidationError]:
        """
        Identify potentially unreachable code blocks.
        
        Args:
            file_result: File analysis result to analyze
        
        Returns:
            List of validation errors for unreachable code
        """
        errors = []
        context_usage = {}
        
        # Track which contexts are used
        for directive in file_result.directives:
            context_key = " && ".join(directive.context) if directive.context else "global"
            context_usage[context_key] = context_usage.get(context_key, 0) + 1
        
        # Look for contradictory conditions that might indicate unreachable code
        for context, count in context_usage.items():
            if "&&" in context:
                conditions = context.split(" && ")
                # Check for obvious contradictions like "A && !A"
                symbols = set()
                negated_symbols = set()
                
                for condition in conditions:
                    if condition.startswith("!"):
                        negated_symbols.add(condition[1:])
                    else:
                        symbols.add(condition)
                
                # Find contradictions
                contradictions = symbols.intersection(negated_symbols)
                if contradictions:
                    # Find a directive with this context to report the error
                    for directive in file_result.directives:
                        directive_context = " && ".join(directive.context) if directive.context else "global"
                        if directive_context == context:
                            errors.append(ValidationError(
                                severity=ErrorSeverity.WARNING,
                                message=f"Potentially unreachable code: contradictory conditions {', '.join(contradictions)}",
                                file_path=directive.file_path,
                                line_number=directive.line_number,
                                directive_content=directive.content
                            ))
                            break
        
        return errors
    
    def get_context_statistics(self, file_result: FileAnalysisResult) -> Dict[str, any]:
        """
        Get statistics about context usage in the file.
        
        Args:
            file_result: File analysis result to analyze
        
        Returns:
            Dictionary containing context statistics
        """
        stats = {
            'total_contexts': 0,
            'max_nesting_depth': 0,
            'context_usage': {},
            'defines_by_context': {},
            'most_used_conditions': {}
        }
        
        # Analyze contexts
        for directive in file_result.directives:
            context_key = " && ".join(directive.context) if directive.context else "global"
            
            # Update context usage
            stats['context_usage'][context_key] = stats['context_usage'].get(context_key, 0) + 1
            
            # Track max nesting depth
            nesting_depth = len(directive.context)
            stats['max_nesting_depth'] = max(stats['max_nesting_depth'], nesting_depth)
            
            # Track defines by context
            if directive.type == DirectiveType.DEFINE:
                if context_key not in stats['defines_by_context']:
                    stats['defines_by_context'][context_key] = []
                stats['defines_by_context'][context_key].append(directive.symbol_name)
        
        stats['total_contexts'] = len(stats['context_usage'])
        
        # Find most used conditions
        condition_counts = {}
        for directive in file_result.directives:
            if directive.condition and directive.type in [DirectiveType.IF, DirectiveType.IFDEF, DirectiveType.IFNDEF]:
                condition_counts[directive.condition] = condition_counts.get(directive.condition, 0) + 1
        
        stats['most_used_conditions'] = dict(sorted(condition_counts.items(), key=lambda x: x[1], reverse=True))
        
        return stats