# 🎯 Team Picker

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-160%20passed-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](#testing)

A professional team assignment application with modern web interface and
comprehensive export capabilities. Built with **Single Responsibility Principle
(SRP)** architecture, featuring both web and command-line interfaces for maximum
flexibility.

## 📚 Table of Contents

-   [🆕 What's New](#-whats-new)
-   [🎯 Design Philosophy](#-design-philosophy)
-   [✨ Features](#-features)
-   [🚀 Quick Start](#-quick-start)
-   [📁 Project Architecture](#-project-architecture)
-   [🌐 Web Application](#-web-application)
-   [💻 Command Line Interface](#-command-line-interface)
-   [📄 Student Data Format](#-student-data-format)
-   [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
-   [🛠️ Development Workflow](#️-development-workflow)
-   [🔧 Configuration & Customization](#-configuration--customization)
-   [🚀 Deployment](#-deployment)
-   [🔒 Security Features](#-security-features)
-   [📈 Performance](#-performance)
-   [🔄 Migration Guide](#-migration-guide)
-   [🤝 Contributing](#-contributing)
-   [🔧 Troubleshooting](#-troubleshooting)
-   [📋 Requirements](#-requirements)
-   [📝 License](#-license)
-   [🆘 Support](#-support)

## 🆕 What's New

### Version 2.0 Highlights

-   **🧪 Comprehensive Testing:** 160 test cases with 99% code coverage
-   **🔧 Development Workflow:** Complete Makefile with pre-commit hooks
-   **🏗️ Modern Architecture:** Single Responsibility Principle with type safety
-   **🌐 Enhanced Web Interface:** Improved UI/UX with drag-and-drop file upload
-   **📊 Professional Exports:** High-quality PNG visualizations with all
    student names
-   **🔒 Security Hardening:** Bandit security scanning and input validation
-   **📱 Mobile Responsive:** Works seamlessly on all device sizes
-   **🚀 Performance Optimized:** Efficient algorithms and memory management

### Recent Improvements

-   Added RTF file format support for Word documents
-   Implemented comprehensive error handling and validation
-   Enhanced team distribution algorithms for better balance
-   Added sample data generation for quick testing
-   Improved documentation with troubleshooting guide

## 🎯 Design Philosophy

### Core Principles

**🏗️ Single Responsibility Principle (SRP)** Each class and module has one clear
purpose, making the codebase maintainable and testable.

**🔒 Type Safety First** Comprehensive type hints and TypedDict usage ensure
reliability and excellent IDE support.

**🧪 Test-Driven Quality** 99% test coverage with 160 test cases ensures robust,
reliable functionality.

**🌐 Interface Flexibility** Multiple interfaces (web, CLI, API) serve different
use cases without code duplication.

**📊 Professional Output** High-quality exports suitable for academic and
professional environments.

### Architecture Highlights

-   **Dependency Injection:** Loose coupling between components
-   **Modern Python:** Dataclasses, pathlib, and contemporary patterns
-   **Clean Code:** Readable, documented, and maintainable codebase
-   **Security Conscious:** Input validation, file security, and vulnerability
    scanning
-   **Performance Optimized:** Efficient algorithms with O(n) complexity

### Why This Approach?

1. **Maintainability:** Clear separation of concerns makes updates easy
2. **Reliability:** Comprehensive testing catches issues before deployment
3. **Flexibility:** Multiple interfaces serve different user needs
4. **Professional:** Production-ready code with proper documentation
5. **Educational:** Clean architecture serves as a learning example

## ✨ Features

### 🎯 **Core Functionality**

-   **Dual Assignment Methods:**
    -   **By Team Size:** Create teams with specific number of members (e.g.,
        teams of 4)
    -   **By Team Count:** Create specific number of teams (e.g., create 6 teams
        total)
-   **Smart Distribution:** Automatic handling of remainder students with
    balanced allocation
-   **Randomization Control:** Optional shuffling for fair team assignment

### 🌐 **Multiple Interfaces**

-   **Modern Web Application:** Drag-and-drop file upload with responsive design
-   **Command Line Interface:** Python scripts for automation and batch
    processing
-   **RESTful API:** JSON endpoints for integration with other systems

### 📊 **Export & Visualization**

-   **JSON Export:** Structured data with metadata for system integration
-   **Image Export:** Professional PNG visualizations with all student names
-   **Text Display:** Formatted console output with readable team assignments
-   **File Management:** Organized output directory structure

### 🏗️ **Architecture Benefits**

-   **Single Responsibility Principle:** Each class handles one specific concern
-   **Type Safety:** Full typing support with TypedDict and type hints
-   **Dependency Injection:** Loose coupling between components
-   **Modern Python:** Dataclasses, pathlib, and contemporary patterns
-   **Comprehensive Testing:** 160 test cases with 99% code coverage

## 🚀 Quick Start

### Prerequisites

-   **Python 3.8+** (recommended: Python 3.11+)
-   **Git** (for cloning the repository)
-   **Modern web browser** (for web interface)

### Web Application (Recommended)

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd team-picker

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies with development tools
make install-dev

# 4. Setup code quality tools (optional but recommended)
make setup-pre-commit

# 5. Start web server
make run

# 6. Open browser to http://localhost:5000
# 7. Upload a student file or use sample data to get started!
```

### Command Line Interface

```bash
# 1. Install production dependencies only
make install

# 2. Create your student list file
echo "john.doe@university.edu" > student_list.txt
echo "jane.smith@university.edu" >> student_list.txt
echo "alex.johnson@university.edu" >> student_list.txt
echo "maria.garcia@university.edu" >> student_list.txt

# 3. Run the example script
python example.py

# 4. Check the output/ directory for generated files
ls output/json/    # JSON exports
ls output/images/  # PNG visualizations
```

### Verify Installation

```bash
# Run tests to verify everything works
make test

# Check code quality
make check

# View available commands
make help
```

## 📁 Project Architecture

```
team-picker/
├── 🏗️ Core Architecture
│   ├── models.py              # Data classes (Student, Team, Results)
│   ├── services.py            # Service layer (Repository, Export, Formatting)
│   ├── team_picker_app.py     # Application coordinator
│   └── team_picker.py         # Legacy interface (maintained for compatibility)
│
├── 🌐 Web Interface
│   ├── app.py                 # Flask application with RESTful API
│   ├── templates/             # Jinja2 templates
│   │   └── index.html        # Modern responsive interface
│   └── static/               # CSS, JavaScript, assets
│
├── 💻 Command Line
│   └── example.py             # CLI usage examples and workflows
│
├── 🧪 Testing & Quality
│   ├── tests/                # Comprehensive test suite (160 tests)
│   ├── .pre-commit-config.yaml # Code quality automation
│   ├── pyproject.toml        # Project configuration
│   └── Makefile              # Development workflow commands
│
├── 📊 Output & Data
│   ├── output/               # Generated exports (auto-created)
│   │   ├── json/            # JSON export files
│   │   └── images/          # PNG visualization files
│   ├── uploads/             # Temporary file uploads
│   └── student_list.txt     # Your student data
│
└── 📋 Configuration
    ├── requirements.txt      # Production dependencies
    ├── .gitignore           # Git ignore patterns
    └── README.md            # This documentation
```

## 🌐 Web Application

### Features

-   **🎨 Modern Design:** Clean, responsive interface with professional styling
-   **📁 File Upload:** Drag & drop support for .txt and .rtf files
-   **👀 Live Preview:** See parsed students before creating teams
-   **📊 Visual Results:** Interactive team cards with member details
-   **⬇️ Export Options:** Direct download of JSON data and PNG images
-   **📱 Mobile Friendly:** Responsive design for all devices

### API Endpoints

| Endpoint                   | Method | Description                    |
| -------------------------- | ------ | ------------------------------ |
| `/`                        | GET    | Main web interface             |
| `/api/upload`              | POST   | Upload and parse student files |
| `/api/create-teams`        | POST   | Create team assignments        |
| `/api/download/json/{id}`  | GET    | Download JSON export           |
| `/api/download/image/{id}` | GET    | Download PNG visualization     |
| `/api/sample-data`         | GET    | Get sample student data        |

### Usage Flow

1. **Upload student list** (.txt or .rtf file with email addresses)
2. **Preview students** with automatic name formatting
3. **Configure teams** (by count or size with optional parameters)
4. **View results** in interactive team cards
5. **Download exports** (JSON data + PNG visualization)

## 💻 Command Line Interface

### Basic Usage

```python
from team_picker_app import TeamPickerApp

# Initialize with student file
app = TeamPickerApp("student_list.txt")

# Load students
students = app.load_students()
print(f"Loaded {len(students)} students")

# Create teams by size (e.g., teams of 4)
result = app.create_teams_by_size(4)
print(app.format_result(result))

# Create teams by count (e.g., 6 teams total)
result = app.create_teams_by_count(6)
exports = app.export_result(result)
print(f"Exported to: {exports['json_file']}")
```

### Advanced Features

```python
# Export student list visualization
student_exports = app.export_student_list()

# Custom output formatting
formatted_output = app.format_result(result)

# Access detailed team information
for team in result.teams:
    print(f"Team {team.number}: {len(team.members)} members")
    for student in team.members:
        print(f"  - {student.name} ({student.email})")
```

## 📄 Student Data Format

### Supported File Types

-   **Plain Text (.txt):** One email per line
-   **Rich Text Format (.rtf):** From Word, Google Docs, etc.

### Email Format Examples

```
john.doe@university.edu          → John Doe
jane.smith@university.edu        → Jane Smith
alex.johnson@university.edu      → Alex Johnson
maria.garcia@university.edu      → Maria Garcia
```

### Name Extraction Rules

-   Extracts name from email prefix (before @)
-   Converts dots/underscores to spaces
-   Applies title case formatting
-   Handles complex names: `first.middle.last@domain.edu` → `First Middle Last`

## 🧪 Testing & Quality Assurance

### Test Suite Overview

-   **📊 Coverage:** 99% code coverage (603/611 statements)
-   **🧪 Test Cases:** 160 comprehensive test functions
-   **📁 Test Files:** 6 specialized test modules
-   **🔧 Test Types:** Unit, integration, and edge case testing

### Test Modules

```
tests/
├── test_models.py         # Data class testing
├── test_services.py       # Service layer testing
├── test_team_picker_app.py # Application logic testing
├── test_team_picker.py    # Legacy interface testing
├── test_app.py           # Flask web application testing
└── test_example.py       # CLI workflow testing
```

### Quality Tools

-   **Black:** Code formatting
-   **isort:** Import sorting
-   **flake8:** Linting and style checking
-   **mypy:** Static type checking
-   **bandit:** Security vulnerability scanning
-   **pre-commit:** Automated quality checks

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage
make test-only

# Run tests in watch mode
make test-watch

# Generate coverage reports
make test-coverage

# Clean test artifacts
make test-clean
```

## 🛠️ Development Workflow

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Setup pre-commit hooks
make setup-pre-commit

# Verify setup
make check
```

### Available Commands

```bash
# Development
make run              # Start Flask development server
make format           # Format all code (black, isort, prettier)
make lint             # Run all linting checks
make check            # Run complete quality checks (lint + test)

# Testing
make test             # Run tests with coverage
make test-watch       # Run tests in watch mode
make test-coverage    # Generate detailed coverage reports

# Maintenance
make clean            # Clean generated files
make update-deps      # Update all dependencies
```

### Pre-commit Hooks

Automatically runs on every commit:

-   Code formatting (Black, isort, Prettier)
-   Linting (flake8, mypy)
-   Security scanning (bandit, detect-secrets)
-   File validation (trailing whitespace, file size, etc.)

## 🔧 Configuration & Customization

### Environment Variables

```bash
FLASK_ENV=development     # Flask environment
FLASK_DEBUG=1            # Enable debug mode
SECRET_KEY=your-key      # Flask secret key (auto-generated if not set)
```

### Adding New Export Formats

```python
# In services.py
class CustomExportService:
    @staticmethod
    def export_result(result: TeamAssignmentResult, file_path: str):
        # Your custom export logic
        pass

# In team_picker_app.py
class TeamPickerApp:
    def __init__(self, student_file: str = "student_list.txt"):
        # ... existing code ...
        self.custom_export = CustomExportService()
```

### Custom Student Data Sources

```python
# Extend StudentRepository
class DatabaseStudentRepository(StudentRepository):
    def load_students(self) -> List[Student]:
        # Load from database, API, etc.
        pass
```

## 🚀 Deployment

### Production Setup

```bash
# Install production dependencies only
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production
export SECRET_KEY="your-secure-secret-key"  # pragma: allowlist secret

# Run with production server
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 🔒 Security Features

-   **Input Validation:** Email format validation and sanitization
-   **File Upload Security:** Extension validation and size limits
-   **Secret Management:** Secure secret key generation
-   **Security Scanning:** Automated vulnerability detection with bandit
-   **CSRF Protection:** Flask built-in security features

## 📈 Performance

-   **Efficient Algorithms:** O(n) team assignment complexity
-   **Memory Optimization:** Lazy loading and generator usage
-   **File Handling:** Streaming for large files
-   **Caching:** Static file caching in production

## 🔄 Migration Guide

### From Legacy TeamPicker

```python
# Old way (still supported)
from team_picker import TeamPicker
picker = TeamPicker()
result = picker.create_teams_by_size(4)

# New way (recommended)
from team_picker_app import TeamPickerApp
app = TeamPickerApp()
result = app.create_teams_by_size(4)
exports = app.export_result(result)
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Install dev dependencies:** `make install-dev`
4. **Setup pre-commit:** `make setup-pre-commit`
5. **Make changes and test:** `make check`
6. **Commit changes:** `git commit -m 'Add amazing feature'`
7. **Push to branch:** `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Code Standards

-   Follow PEP 8 style guidelines
-   Maintain 95%+ test coverage
-   Add type hints for all functions
-   Write comprehensive docstrings
-   Update tests for new features

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**Issue:** `pip install` fails with dependency conflicts

```bash
# Solution: Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Issue:** `striprtf` not found error

```bash
# Solution: Install RTF support
pip install striprtf
```

#### File Upload Issues

**Issue:** "No valid students found" error

-   **Cause:** Email format not recognized
-   **Solution:** Ensure emails contain `@` symbol and proper format
-   **Example:** `john.doe@university.edu` ✅, `john.doe` ❌

**Issue:** RTF files not parsing correctly

-   **Cause:** Complex RTF formatting
-   **Solution:** Save as plain text (.txt) or copy-paste content

#### Web Application Issues

**Issue:** Flask app won't start

```bash
# Check if port 5000 is in use
lsof -i :5000

# Use different port
export FLASK_RUN_PORT=8000
python app.py
```

**Issue:** File upload size limit exceeded

-   **Cause:** File larger than 16MB
-   **Solution:** Split large files or increase limit in `app.py`

#### Team Assignment Issues

**Issue:** Teams are not balanced

-   **Cause:** Student count doesn't divide evenly
-   **Solution:** This is expected behavior - remainder students are distributed

**Issue:** Same teams generated repeatedly

-   **Cause:** Random seed not changing
-   **Solution:** Restart application or use shuffle=True parameter

#### Testing Issues

**Issue:** Tests fail with import errors

```bash
# Solution: Install in development mode
pip install -e ".[dev]"
```

**Issue:** Coverage reports not generating

```bash
# Solution: Install coverage dependencies
pip install pytest-cov
make test-coverage
```

#### Development Issues

**Issue:** Pre-commit hooks failing

```bash
# Solution: Fix formatting and run again
make format
make lint
git add .
git commit -m "Fix formatting"
```

**Issue:** MyPy type checking errors

-   **Cause:** Missing type hints or imports
-   **Solution:** Add proper type annotations and imports

### Performance Issues

**Issue:** Slow team generation with large student lists

-   **Cause:** Large dataset processing
-   **Solution:** Consider batch processing for 1000+ students

**Issue:** High memory usage during image export

-   **Cause:** Large matplotlib figures
-   **Solution:** Reduce image size or use text-only export

### Getting Help

1. **Check the logs:** Look for error messages in console output
2. **Verify file format:** Ensure student files follow expected format
3. **Test with sample data:** Use `python example.py` to verify setup
4. **Check dependencies:** Run `pip list` to verify installations
5. **Clear cache:** Run `make clean` to remove temporary files

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
python app.py
```

### Reporting Issues

When reporting issues, please include:

-   Python version (`python --version`)
-   Operating system
-   Error messages (full traceback)
-   Steps to reproduce
-   Sample data (if applicable)

## 📋 Requirements

-   **Python:** 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
-   **Dependencies:** Flask, matplotlib, Pillow, numpy, striprtf
-   **Development:** pytest, black, mypy, pre-commit (see pyproject.toml)

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

-   **Issues:** [GitHub Issues](https://github.com/mabreyes/team-picker/issues)
-   **Documentation:** This README and inline code documentation
-   **Examples:** See `example.py` for comprehensive usage examples

---

**🎯 Happy team building with professional-grade team assignments! 🚀**
