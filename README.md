# C++ Preprocessor Directive Analysis Tool

A comprehensive Python-based command-line utility designed to parse C++ source files and analyze preprocessor directive usage patterns. The tool identifies all preprocessor directives (#define, #ifdef, #ifndef, #else, #elif, #endif) and determines the conditional compilation contexts under which each #define statement is declared.

## Features

- **Comprehensive Analysis**: Parse and analyze all types of preprocessor directives
- **Context Tracking**: Track conditional compilation contexts for each directive
- **Multiple Output Formats**: Generate reports in text, HTML, markdown, and JSON formats
- **Validation**: Comprehensive syntax validation and error detection
- **Recursive Scanning**: Support for analyzing entire directory trees
- **Filtering**: Exclude files/directories using glob patterns
- **Dependency Analysis**: Track symbol dependencies and detect circular references

## Installation

1. Clone or download this repository
2. Install Python 3.7 or later
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Analysis
```bash
# Analyze a single file
python main.py analyze src/main.cpp

# Analyze a directory (C++ source files only)
python main.py analyze src/

# Analyze a directory including headers recursively
python main.py analyze src/ --recursive --include-headers
```

### Generate Reports
```bash
# Save analysis to JSON file
python main.py analyze src/ --output analysis.json

# Generate HTML report
python main.py report --input analysis.json --format html --output report.html

# Generate markdown report with dependencies
python main.py report --input analysis.json --format markdown --show-dependencies
```

### Validation
```bash
# Validate syntax and nesting
python main.py validate src/config.h

# Strict validation with additional checks
python main.py validate src/ --strict --check-balance
```

## Command Reference

### `analyze` Command

Analyze preprocessor directives in C++ files and directories.

```bash
python main.py analyze <path> [options]
```

**Arguments:**
- `path`: File or directory path to analyze

**Options:**
- `--recursive, -r`: Recursively scan directories
- `--include-headers`: Include header files (.h, .hpp, .hxx)
- `--output, -o FILE`: Save results to file (JSON format)
- `--format FORMAT`: Output format (json, xml, yaml)
- `--exclude PATTERN`: Exclude files matching pattern (can be used multiple times)
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Basic directory analysis
python main.py analyze src/

# Include headers and save results
python main.py analyze project/ -r --include-headers -o analysis.json

# Exclude test files
python main.py analyze src/ --exclude "*test*" --exclude "*Test*"
```

### `report` Command

Generate formatted reports from analysis data.

```bash
python main.py report --input <file> [options]
```

**Required:**
- `--input, -i FILE`: Input analysis data file (JSON)

**Options:**
- `--format FORMAT`: Report format (text, html, markdown)
- `--output, -o FILE`: Output file for the report
- `--show-dependencies`: Include dependency analysis
- `--filter-defines PATTERN`: Filter defines by regex pattern
- `--group-by-context`: Group defines by conditional contexts

**Examples:**
```bash
# Generate text report to console
python main.py report -i analysis.json

# Generate HTML report with dependencies
python main.py report -i analysis.json --format html --show-dependencies -o report.html

# Filter and group defines
python main.py report -i analysis.json --filter-defines "LOG_.*" --group-by-context
```

### `validate` Command

Validate preprocessor directive syntax and structure.

```bash
python main.py validate <files...> [options]
```

**Arguments:**
- `files`: One or more C++ files to validate

**Options:**
- `--strict`: Enable strict validation rules
- `--check-balance`: Verify directive nesting balance
- `--output, -o FILE`: Save validation results to file

**Examples:**
```bash
# Basic validation
python main.py validate src/config.h

# Strict validation of multiple files
python main.py validate src/*.cpp --strict

# Save validation results
python main.py validate src/ --output validation.json
```

## Output Formats

### Text Report
Human-readable tabular format with:
- Summary statistics
- File breakdown
- Define analysis with contexts
- Condition usage frequency
- Validation errors

### HTML Report
Interactive web-based report with:
- Styled tables and statistics
- Color-coded error severity
- Expandable sections
- Professional styling

### Markdown Report
Documentation-friendly format with:
- GitHub-flavored markdown
- Tables and code blocks
- Easy integration with documentation

### JSON Data
Structured data format for:
- Programmatic processing
- Integration with other tools
- Custom analysis scripts

## Analysis Features

### Context Tracking
The tool tracks the conditional compilation context for each directive:

```cpp
#ifdef DEBUG
    #ifndef RELEASE
        #define LOG_LEVEL 3  // Context: [DEBUG, !RELEASE]
    #endif
#endif
```

### Dependency Analysis
Detects symbol dependencies and relationships:
- Tracks which symbols are referenced in conditions
- Identifies circular dependencies
- Maps symbol usage across files

### Validation Rules
Comprehensive validation including:
- Syntax errors in directives
- Unmatched conditional blocks
- Missing #endif directives
- Invalid identifier names
- Reserved identifier usage (strict mode)
- Naming convention compliance

## Sample Output

```
=== Analysis Summary ===
Files processed: 5
Total directives: 434
Define directives: 155
Validation errors: 4

Most used conditions:
  DEBUG: 7 times
  ENABLE_NETWORKING: 5 times
  WINDOWS: 4 times
  ENABLE_SSL: 4 times

Validation errors:
  main.cpp:86: Unmatched conditional directive(s): 2 unclosed block(s)
  network.cpp:192: Unmatched conditional directive(s): 1 unclosed block(s)
```

## Error Detection

The tool detects various types of errors:

- **Syntax Errors**: Invalid directive syntax, malformed conditions
- **Balance Errors**: Unmatched #ifdef/#endif pairs
- **Semantic Errors**: Duplicate definitions, undefined symbols
- **Style Warnings**: Naming conventions, reserved identifiers

## Project Structure

```
Project12/
├── main.py                 # Main entry point
├── src/                    # Source code
│   ├── cli.py             # Command-line interface
│   ├── file_scanner.py    # File discovery
│   ├── preprocessor_parser.py  # Directive parsing
│   ├── context_analyzer.py     # Context tracking
│   ├── validation.py      # Validation engine
│   ├── report_generator.py     # Report generation
│   └── data_models.py     # Data structures
├── tests/                  # Unit tests
├── samples/               # Sample C++ files
└── requirements.txt       # Dependencies
```

## Testing

Run the test suite:

```bash
cd tests
python test_runner.py
```

Test with sample files:

```bash
# Test analysis
python main.py analyze samples/ --include-headers --verbose

# Test validation
python main.py validate samples/test_errors.cpp

# Test reporting
python main.py analyze samples/ -o test.json
python main.py report -i test.json --format html -o test.html
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or feature requests, please create an issue in the project repository.