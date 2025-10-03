"""
Report generator module for creating formatted output reports.
Supports multiple output formats: JSON, text, HTML, and markdown.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .data_models import AnalysisResult, Directive, DirectiveType


class ReportGenerator:
    """
    Generates formatted reports from analysis results in various formats.
    """
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_report(self, 
                       data: Dict[str, Any], 
                       format_type: str = "text",
                       show_dependencies: bool = False,
                       filter_defines: Optional[str] = None,
                       group_by_context: bool = False) -> str:
        """
        Generate a report from analysis data.
        
        Args:
            data: Analysis result data dictionary
            format_type: Output format (text, html, markdown)
            show_dependencies: Include dependency analysis
            filter_defines: Filter defines by pattern
            group_by_context: Group defines by context
        
        Returns:
            Formatted report string
        """
        if format_type == "text":
            return self._generate_text_report(data, show_dependencies, filter_defines, group_by_context)
        elif format_type == "html":
            return self._generate_html_report(data, show_dependencies, filter_defines, group_by_context)
        elif format_type == "markdown":
            return self._generate_markdown_report(data, show_dependencies, filter_defines, group_by_context)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _generate_text_report(self, 
                             data: Dict[str, Any], 
                             show_dependencies: bool,
                             filter_defines: Optional[str],
                             group_by_context: bool) -> str:
        """Generate a plain text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("C++ PREPROCESSOR DIRECTIVE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {self.timestamp}")
        lines.append("")
        
        # Summary section
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Files processed: {data.get('total_files', 0)}")
        lines.append(f"Total directives: {data.get('total_directives', 0)}")
        lines.append(f"Define directives: {data.get('total_defines', 0)}")
        lines.append(f"Validation errors: {len(data.get('validation_errors', []))}")
        lines.append("")
        
        # File breakdown
        lines.append("FILES ANALYZED")
        lines.append("-" * 40)
        file_results = data.get('file_results', {})
        for file_path, result in file_results.items():
            lines.append(f"File: {file_path}")
            lines.append(f"  Lines: {result.get('line_count', 0)}")
            lines.append(f"  Directives: {result.get('directive_count', 0)}")
            lines.append(f"  Defines: {len(result.get('defines', []))}")
            lines.append(f"  Errors: {len(result.get('errors', []))}")
            lines.append("")
        
        # Define analysis
        lines.append("DEFINE ANALYSIS")
        lines.append("-" * 40)
        
        all_defines = []
        for result in file_results.values():
            all_defines.extend(result.get('defines', []))
        
        # Apply filter if specified
        if filter_defines:
            filtered_defines = []
            pattern = re.compile(filter_defines, re.IGNORECASE)
            for define in all_defines:
                if pattern.search(define.get('symbol_name', '')):
                    filtered_defines.append(define)
            all_defines = filtered_defines
            lines.append(f"Filtered by pattern: {filter_defines}")
            lines.append("")
        
        if group_by_context:
            # Group defines by context
            context_groups = {}
            for define in all_defines:
                context = " && ".join(define.get('context', [])) or "global"
                if context not in context_groups:
                    context_groups[context] = []
                context_groups[context].append(define)
            
            for context, defines in sorted(context_groups.items()):
                lines.append(f"Context: {context}")
                lines.append(f"  Count: {len(defines)}")
                for define in defines[:10]:  # Show first 10
                    symbol = define.get('symbol_name', 'unknown')
                    file_path = define.get('file_path', '')
                    line_num = define.get('line_number', 0)
                    lines.append(f"    {symbol} ({file_path}:{line_num})")
                if len(defines) > 10:
                    lines.append(f"    ... and {len(defines) - 10} more")
                lines.append("")
        else:
            # List all defines
            for define in all_defines:
                symbol = define.get('symbol_name', 'unknown')
                file_path = define.get('file_path', '')
                line_num = define.get('line_number', 0)
                context = " && ".join(define.get('context', [])) or "global"
                lines.append(f"{symbol:30} {file_path}:{line_num:4} [{context}]")
        
        lines.append("")
        
        # Condition usage
        conditions_usage = data.get('conditions_usage', {})
        if conditions_usage:
            lines.append("CONDITION USAGE")
            lines.append("-" * 40)
            sorted_conditions = sorted(conditions_usage.items(), key=lambda x: x[1], reverse=True)
            for condition, count in sorted_conditions:
                lines.append(f"{condition:50} {count:4} times")
            lines.append("")
        
        # Dependencies
        if show_dependencies:
            dependency_graph = data.get('dependency_graph', {})
            if dependency_graph:
                lines.append("DEPENDENCY GRAPH")
                lines.append("-" * 40)
                for symbol, deps in dependency_graph.items():
                    if deps:
                        lines.append(f"{symbol} depends on: {', '.join(deps)}")
                lines.append("")
        
        # Validation errors
        validation_errors = data.get('validation_errors', [])
        if validation_errors:
            lines.append("VALIDATION ERRORS")
            lines.append("-" * 40)
            for error in validation_errors:
                severity = error.get('severity', 'unknown')
                message = error.get('message', '')
                file_path = error.get('file_path', '')
                line_num = error.get('line_number', 0)
                lines.append(f"{severity.upper()}: {file_path}:{line_num}")
                lines.append(f"  {message}")
                if error.get('suggestion'):
                    lines.append(f"  Suggestion: {error['suggestion']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, 
                             data: Dict[str, Any], 
                             show_dependencies: bool,
                             filter_defines: Optional[str],
                             group_by_context: bool) -> str:
        """Generate an HTML report."""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='en'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("    <title>C++ Preprocessor Analysis Report</title>")
        html.append("    <style>")
        html.append(self._get_html_styles())
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        
        # Header
        html.append("    <div class='header'>")
        html.append("        <h1>C++ Preprocessor Directive Analysis Report</h1>")
        html.append(f"        <p class='timestamp'>Generated: {self.timestamp}</p>")
        html.append("    </div>")
        
        # Summary
        html.append("    <div class='section'>")
        html.append("        <h2>Summary</h2>")
        html.append("        <div class='summary-grid'>")
        html.append(f"            <div class='stat-box'><span class='stat-value'>{data.get('total_files', 0)}</span><span class='stat-label'>Files</span></div>")
        html.append(f"            <div class='stat-box'><span class='stat-value'>{data.get('total_directives', 0)}</span><span class='stat-label'>Directives</span></div>")
        html.append(f"            <div class='stat-box'><span class='stat-value'>{data.get('total_defines', 0)}</span><span class='stat-label'>Defines</span></div>")
        html.append(f"            <div class='stat-box'><span class='stat-value'>{len(data.get('validation_errors', []))}</span><span class='stat-label'>Errors</span></div>")
        html.append("        </div>")
        html.append("    </div>")
        
        # Files section
        html.append("    <div class='section'>")
        html.append("        <h2>Files Analyzed</h2>")
        html.append("        <table class='file-table'>")
        html.append("            <thead>")
        html.append("                <tr><th>File</th><th>Lines</th><th>Directives</th><th>Defines</th><th>Errors</th></tr>")
        html.append("            </thead>")
        html.append("            <tbody>")
        
        file_results = data.get('file_results', {})
        for file_path, result in file_results.items():
            html.append(f"                <tr>")
            html.append(f"                    <td>{self._html_escape(file_path)}</td>")
            html.append(f"                    <td>{result.get('line_count', 0)}</td>")
            html.append(f"                    <td>{result.get('directive_count', 0)}</td>")
            html.append(f"                    <td>{len(result.get('defines', []))}</td>")
            html.append(f"                    <td>{len(result.get('errors', []))}</td>")
            html.append(f"                </tr>")
        
        html.append("            </tbody>")
        html.append("        </table>")
        html.append("    </div>")
        
        # Defines section
        html.append("    <div class='section'>")
        html.append("        <h2>Define Analysis</h2>")
        
        all_defines = []
        for result in file_results.values():
            all_defines.extend(result.get('defines', []))
        
        if filter_defines:
            html.append(f"        <p class='filter-info'>Filtered by pattern: <code>{self._html_escape(filter_defines)}</code></p>")
        
        html.append("        <table class='define-table'>")
        html.append("            <thead>")
        html.append("                <tr><th>Symbol</th><th>File</th><th>Line</th><th>Context</th></tr>")
        html.append("            </thead>")
        html.append("            <tbody>")
        
        for define in all_defines:
            symbol = define.get('symbol_name', 'unknown')
            file_path = define.get('file_path', '')
            line_num = define.get('line_number', 0)
            context = " && ".join(define.get('context', [])) or "global"
            
            html.append(f"                <tr>")
            html.append(f"                    <td><code>{self._html_escape(symbol)}</code></td>")
            html.append(f"                    <td>{self._html_escape(file_path)}</td>")
            html.append(f"                    <td>{line_num}</td>")
            html.append(f"                    <td><code>{self._html_escape(context)}</code></td>")
            html.append(f"                </tr>")
        
        html.append("            </tbody>")
        html.append("        </table>")
        html.append("    </div>")
        
        # Validation errors
        validation_errors = data.get('validation_errors', [])
        if validation_errors:
            html.append("    <div class='section'>")
            html.append("        <h2>Validation Errors</h2>")
            html.append("        <div class='errors'>")
            
            for error in validation_errors:
                severity = error.get('severity', 'unknown')
                message = error.get('message', '')
                file_path = error.get('file_path', '')
                line_num = error.get('line_number', 0)
                
                html.append(f"            <div class='error-item {severity}'>")
                html.append(f"                <div class='error-header'>{severity.upper()}: {self._html_escape(file_path)}:{line_num}</div>")
                html.append(f"                <div class='error-message'>{self._html_escape(message)}</div>")
                if error.get('suggestion'):
                    html.append(f"                <div class='error-suggestion'>Suggestion: {self._html_escape(error['suggestion'])}</div>")
                html.append(f"            </div>")
            
            html.append("        </div>")
            html.append("    </div>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def _generate_markdown_report(self, 
                                 data: Dict[str, Any], 
                                 show_dependencies: bool,
                                 filter_defines: Optional[str],
                                 group_by_context: bool) -> str:
        """Generate a markdown report."""
        lines = []
        lines.append("# C++ Preprocessor Directive Analysis Report")
        lines.append("")
        lines.append(f"**Generated:** {self.timestamp}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Files processed:** {data.get('total_files', 0)}")
        lines.append(f"- **Total directives:** {data.get('total_directives', 0)}")
        lines.append(f"- **Define directives:** {data.get('total_defines', 0)}")
        lines.append(f"- **Validation errors:** {len(data.get('validation_errors', []))}")
        lines.append("")
        
        # Files
        lines.append("## Files Analyzed")
        lines.append("")
        lines.append("| File | Lines | Directives | Defines | Errors |")
        lines.append("|------|-------|------------|---------|--------|")
        
        file_results = data.get('file_results', {})
        for file_path, result in file_results.items():
            lines.append(f"| `{file_path}` | {result.get('line_count', 0)} | {result.get('directive_count', 0)} | {len(result.get('defines', []))} | {len(result.get('errors', []))} |")
        
        lines.append("")
        
        # Defines
        lines.append("## Define Analysis")
        lines.append("")
        
        all_defines = []
        for result in file_results.values():
            all_defines.extend(result.get('defines', []))
        
        if filter_defines:
            lines.append(f"*Filtered by pattern: `{filter_defines}`*")
            lines.append("")
        
        lines.append("| Symbol | File | Line | Context |")
        lines.append("|--------|------|------|---------|")
        
        for define in all_defines:
            symbol = define.get('symbol_name', 'unknown')
            file_path = define.get('file_path', '')
            line_num = define.get('line_number', 0)
            context = " && ".join(define.get('context', [])) or "global"
            lines.append(f"| `{symbol}` | `{file_path}` | {line_num} | `{context}` |")
        
        lines.append("")
        
        # Conditions
        conditions_usage = data.get('conditions_usage', {})
        if conditions_usage:
            lines.append("## Condition Usage")
            lines.append("")
            lines.append("| Condition | Usage Count |")
            lines.append("|-----------|-------------|")
            
            sorted_conditions = sorted(conditions_usage.items(), key=lambda x: x[1], reverse=True)
            for condition, count in sorted_conditions:
                lines.append(f"| `{condition}` | {count} |")
            
            lines.append("")
        
        # Dependencies
        if show_dependencies:
            dependency_graph = data.get('dependency_graph', {})
            if dependency_graph:
                lines.append("## Dependency Graph")
                lines.append("")
                for symbol, deps in dependency_graph.items():
                    if deps:
                        lines.append(f"- `{symbol}` depends on: {', '.join(f'`{dep}`' for dep in deps)}")
                lines.append("")
        
        # Validation errors
        validation_errors = data.get('validation_errors', [])
        if validation_errors:
            lines.append("## Validation Errors")
            lines.append("")
            
            for error in validation_errors:
                severity = error.get('severity', 'unknown')
                message = error.get('message', '')
                file_path = error.get('file_path', '')
                line_num = error.get('line_number', 0)
                
                lines.append(f"### {severity.upper()}: `{file_path}:{line_num}`")
                lines.append("")
                lines.append(message)
                lines.append("")
                if error.get('suggestion'):
                    lines.append(f"**Suggestion:** {error['suggestion']}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML reports."""
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .timestamp { margin: 10px 0 0 0; opacity: 0.8; }
        .section { background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
        .stat-box { background-color: #3498db; color: white; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-value { display: block; font-size: 24px; font-weight: bold; }
        .stat-label { display: block; font-size: 12px; opacity: 0.8; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f8f9fa; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
        .filter-info { background-color: #e8f4f8; padding: 10px; border-radius: 5px; }
        .errors { margin-top: 10px; }
        .error-item { margin-bottom: 15px; padding: 15px; border-radius: 5px; border-left: 4px solid; }
        .error-item.error { background-color: #fdf2f2; border-left-color: #e53e3e; }
        .error-item.warning { background-color: #fffaf0; border-left-color: #dd6b20; }
        .error-item.critical { background-color: #fed7d7; border-left-color: #c53030; }
        .error-header { font-weight: bold; margin-bottom: 5px; }
        .error-message { margin-bottom: 5px; }
        .error-suggestion { font-style: italic; opacity: 0.8; }
        """
    
    def _html_escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def export_to_json(self, data: Dict[str, Any], indent: int = 2) -> str:
        """Export analysis data to formatted JSON."""
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    def create_summary_report(self, data: Dict[str, Any]) -> str:
        """Create a brief summary report."""
        lines = []
        lines.append("QUICK SUMMARY")
        lines.append("=" * 50)
        lines.append(f"Files: {data.get('total_files', 0)}")
        lines.append(f"Directives: {data.get('total_directives', 0)}")
        lines.append(f"Defines: {data.get('total_defines', 0)}")
        lines.append(f"Errors: {len(data.get('validation_errors', []))}")
        
        # Top conditions
        conditions_usage = data.get('conditions_usage', {})
        if conditions_usage:
            lines.append("\nTop conditions:")
            sorted_conditions = sorted(conditions_usage.items(), key=lambda x: x[1], reverse=True)
            for condition, count in sorted_conditions[:3]:
                lines.append(f"  {condition}: {count} times")
        
        return "\n".join(lines)