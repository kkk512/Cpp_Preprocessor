"""
Command-line interface for the C++ Preprocessor Directive Analysis Tool.
Provides argument parsing and command routing for analyze, report, and validate commands.
"""

import argparse
import sys
import os
import json
from typing import List, Optional

from .file_scanner import FileScanner
from .preprocessor_parser import PreprocessorParser
from .context_analyzer import ContextAnalyzer
from .report_generator import ReportGenerator
from .validation import DirectiveValidator
from .data_models import AnalysisResult


class CLI:
    """Main CLI class for handling command-line operations."""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.file_scanner = FileScanner()
        self.preprocessor_parser = PreprocessorParser()
        self.context_analyzer = ContextAnalyzer()
        self.report_generator = ReportGenerator()
        self.validator = DirectiveValidator()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with subcommands."""
        parser = argparse.ArgumentParser(
            prog="cpp-preprocessor-analyzer",
            description="Analyze C++ preprocessor directives and their contexts",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s analyze src/
  %(prog)s analyze file.cpp --output analysis.json
  %(prog)s report --input analysis.json --format html
  %(prog)s validate src/ --strict
            """
        )
        
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands",
            metavar="COMMAND"
        )
        
        # Analyze command
        analyze_parser = subparsers.add_parser(
            "analyze",
            help="Analyze preprocessor directives in C++ files",
            description="Parse C++ files and analyze preprocessor directive usage patterns"
        )
        self._add_analyze_arguments(analyze_parser)
        
        # Report command
        report_parser = subparsers.add_parser(
            "report",
            help="Generate reports from analysis results",
            description="Generate formatted reports from previously saved analysis data"
        )
        self._add_report_arguments(report_parser)
        
        # Validate command
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate preprocessor directive syntax",
            description="Check for syntax errors and nesting issues in preprocessor directives"
        )
        self._add_validate_arguments(validate_parser)
        
        return parser

    def _add_analyze_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments for the analyze command."""
        parser.add_argument(
            "path",
            help="Path to C++ file or directory to analyze"
        )
        parser.add_argument(
            "--recursive", "-r",
            action="store_true",
            help="Recursively scan directories for C++ files"
        )
        parser.add_argument(
            "--include-headers",
            action="store_true",
            help="Include header files (.h, .hpp, .hxx) in analysis"
        )
        parser.add_argument(
            "--output", "-o",
            help="Output file for analysis results (JSON format)"
        )
        parser.add_argument(
            "--format",
            choices=["json", "xml", "yaml"],
            default="json",
            help="Output format for results (default: json)"
        )
        parser.add_argument(
            "--exclude",
            action="append",
            help="Patterns to exclude from analysis (can be used multiple times)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )

    def _add_report_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments for the report command."""
        parser.add_argument(
            "--input", "-i",
            required=True,
            help="Input analysis data file (JSON format)"
        )
        parser.add_argument(
            "--format",
            choices=["text", "html", "markdown"],
            default="text",
            help="Report format (default: text)"
        )
        parser.add_argument(
            "--output", "-o",
            help="Output file for the report"
        )
        parser.add_argument(
            "--show-dependencies",
            action="store_true",
            help="Include dependency analysis in the report"
        )
        parser.add_argument(
            "--filter-defines",
            help="Filter defines by pattern (regex supported)"
        )
        parser.add_argument(
            "--group-by-context",
            action="store_true",
            help="Group defines by their conditional contexts"
        )

    def _add_validate_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments for the validate command."""
        parser.add_argument(
            "files",
            nargs="+",
            help="C++ files to validate"
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict validation rules"
        )
        parser.add_argument(
            "--check-balance",
            action="store_true",
            help="Verify directive nesting balance"
        )
        parser.add_argument(
            "--output", "-o",
            help="Output file for validation results"
        )

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        try:
            parsed_args = self.parser.parse_args(args)
            
            if not parsed_args.command:
                self.parser.print_help()
                return 1
            
            if parsed_args.command == "analyze":
                return self._handle_analyze(parsed_args)
            elif parsed_args.command == "report":
                return self._handle_report(parsed_args)
            elif parsed_args.command == "validate":
                return self._handle_validate(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def _handle_analyze(self, args) -> int:
        """Handle the analyze command."""
        if args.verbose:
            print(f"Analyzing path: {args.path}")
        
        # Check if path exists
        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1
        
        try:
            # Scan for C++ files
            files = self.file_scanner.scan(
                path=args.path,
                recursive=args.recursive,
                include_headers=args.include_headers,
                exclude_patterns=args.exclude or []
            )
            
            if not files:
                print("No C++ files found to analyze")
                return 0
            
            if args.verbose:
                print(f"Found {len(files)} files to analyze")
            
            # Perform analysis
            analysis_result = AnalysisResult()
            
            for file_path in files:
                if args.verbose:
                    print(f"Processing: {file_path}")
                
                try:
                    # Parse directives
                    file_result = self.preprocessor_parser.parse_file(file_path)
                    
                    # Analyze contexts
                    self.context_analyzer.analyze(file_result)
                    
                    # Add to overall results
                    analysis_result.add_file_result(file_result)
                    
                except Exception as e:
                    print(f"Warning: Failed to process {file_path}: {e}")
            
            # Output results
            if args.output:
                self._save_results(analysis_result, args.output, args.format)
                if args.verbose:
                    print(f"Results saved to: {args.output}")
            else:
                # Print summary to stdout
                self._print_analysis_summary(analysis_result)
            
            return 0
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            return 1

    def _handle_report(self, args) -> int:
        """Handle the report command."""
        try:
            # Load analysis data
            if not os.path.exists(args.input):
                print(f"Error: Input file '{args.input}' does not exist")
                return 1
            
            with open(args.input, 'r') as f:
                data = json.load(f)
            
            # Generate report
            report = self.report_generator.generate_report(
                data=data,
                format_type=args.format,
                show_dependencies=args.show_dependencies,
                filter_defines=args.filter_defines,
                group_by_context=args.group_by_context
            )
            
            # Output report
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Report generated: {args.output}")
            else:
                print(report)
            
            return 0
            
        except Exception as e:
            print(f"Report generation failed: {e}")
            return 1

    def _handle_validate(self, args) -> int:
        """Handle the validate command."""
        try:
            errors_found = False
            all_errors = []
            
            for file_path in args.files:
                if not os.path.exists(file_path):
                    print(f"Warning: File '{file_path}' does not exist")
                    continue
                
                # Parse and validate
                file_result = self.preprocessor_parser.parse_file(file_path)
                errors = self.validator.validate(
                    file_result,
                    strict=args.strict,
                    check_balance=args.check_balance
                )
                
                if errors:
                    errors_found = True
                    all_errors.extend(errors)
                    for error in errors:
                        print(f"{error.file_path}:{error.line_number}: "
                              f"{error.severity.value}: {error.message}")
            
            # Save validation results if requested
            if args.output:
                validation_data = {
                    "files_validated": len(args.files),
                    "errors_found": len(all_errors),
                    "errors": [error.to_dict() for error in all_errors]
                }
                with open(args.output, 'w') as f:
                    json.dump(validation_data, f, indent=2)
            
            return 1 if errors_found else 0
            
        except Exception as e:
            print(f"Validation failed: {e}")
            return 1

    def _save_results(self, result: AnalysisResult, output_path: str, format_type: str) -> None:
        """Save analysis results to file."""
        data = result.to_dict()
        
        if format_type == "json":
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format_type == "xml":
            # TODO: Implement XML output
            raise NotImplementedError("XML output not yet implemented")
        elif format_type == "yaml":
            # TODO: Implement YAML output
            raise NotImplementedError("YAML output not yet implemented")
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _print_analysis_summary(self, result: AnalysisResult) -> None:
        """Print a summary of analysis results to stdout."""
        print("\n=== Analysis Summary ===")
        print(f"Files processed: {result.total_files}")
        print(f"Total directives: {result.total_directives}")
        print(f"Define directives: {result.total_defines}")
        print(f"Validation errors: {len(result.validation_errors)}")
        
        if result.conditions_usage:
            print("\nMost used conditions:")
            sorted_conditions = sorted(
                result.conditions_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for condition, count in sorted_conditions[:5]:
                print(f"  {condition}: {count} times")
        
        if result.validation_errors:
            print("\nValidation errors:")
            for error in result.validation_errors[:5]:  # Show first 5 errors
                print(f"  {error.file_path}:{error.line_number}: {error.message}")
            if len(result.validation_errors) > 5:
                print(f"  ... and {len(result.validation_errors) - 5} more errors")


def main():
    """Main entry point for the CLI."""
    cli = CLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()