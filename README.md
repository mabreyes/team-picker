# 🎯 Team Picker

A Pythonic team assignment application following **Single Responsibility Principle (SRP)** with JSON and image export capabilities. Available as both **command-line application** and **web interface**.

## ✨ Features

### **Core Functionality**
- **Two Assignment Methods:**
  - Create teams by specifying team size (e.g., teams of 4 people each)
  - Create teams by specifying number of teams (e.g., create 6 teams total)

### **Multiple Interfaces**
- **🌐 Web Application:** Modern, minimalist interface with drag-and-drop file upload
- **💻 Command Line:** Python scripts for automation and batch processing

### **Enhanced Export Options**
- **JSON Export:** Structured data with metadata for integration
- **Image Export:** Visual team assignments as PNG images showing **all student names**
- **Text Display:** Formatted console output with readable names
- **File Management:** Organized output directory structure

### **Architecture Benefits**
- **Single Responsibility Principle:** Each class handles one specific concern
- **Dependency Injection:** Loose coupling between components
- **Type Hints:** Full typing support for better IDE experience
- **Dataclasses:** Clean, immutable data structures
- **Modern Design:** Host Grotesk typography with professional styling

## 📁 Project Structure

```
team-picker/
├── models.py              # Data classes (Student, Team, TeamAssignmentResult)
├── services.py            # Service classes following SRP
├── team_picker_app.py     # Main application coordinator
├── app.py                 # Flask web application
├── templates/             # Web interface templates
│   └── index.html        # Main web interface
├── example.py             # Complete CLI usage examples
├── student_list.txt       # Your student data (create this file)
├── requirements.txt       # Dependencies
├── README.md             # This documentation
└── output/               # Generated exports (auto-created)
    ├── json/            # JSON export files
    └── images/          # PNG image files
```

## 🌐 Web Application

### Quick Start (Web)
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py

# Open browser to http://localhost:5000
```

### Features
- **🎨 Modern Design:** Minimalist interface with Host Grotesk font
- **📁 Drag & Drop:** Easy file upload for student lists (.txt and .rtf files)
- **👀 Live Preview:** See students before creating teams
- **📊 Visual Results:** Teams displayed in cards and professional images
- **⬇️ Downloads:** Direct download of JSON and PNG exports
- **📱 Responsive:** Works on desktop, tablet, and mobile

### Web Interface Flow
1. **Upload student list** (.txt or .rtf file with emails) or use sample data
2. **Preview students** with automatic name formatting
3. **Configure teams** (by count or size)
4. **View results** in interactive cards
5. **Download exports** (JSON data + PNG visualization)

## 💻 Command Line Interface

### Quick Start (CLI)
```bash
# Install dependencies
pip install -r requirements.txt

# Create your student list
echo "john.doe@university.edu" > student_list.txt
echo "jane.smith@university.edu" >> student_list.txt

# Run example
python example.py
```

If no `student_list.txt` exists, the example will create a sample file for you!

## 🎯 Student Data Format

The application reads from `student_list.txt` with one email per line:

```
john.doe@university.edu
jane.smith@university.edu
alex.johnson@university.edu
maria.garcia@university.edu
```

Names are automatically formatted from emails:
- `john.doe@university.edu` → `John Doe`
- `samantha.michaela.bautista@university.edu` → `Samantha Michaela Bautista`

**Supported formats:**
- Any email address with @ symbol
- Names extracted from the part before @
- Underscores converted to spaces
- Automatic title case formatting

## 📄 Supported File Formats

### Text Files (.txt)
Plain text files with one email per line:
```txt
john.doe@university.edu
jane.smith@university.edu
alex.johnson@university.edu
```

### Rich Text Format (.rtf)
RTF files created by word processors like Microsoft Word, Google Docs, or Apple Pages:
- Automatically extracts plain text from RTF formatting
- Ignores formatting codes and focuses on email content
- Supports standard RTF files from any word processor

**Note:** RTF support requires the `striprtf` library (automatically installed with requirements.txt)

## 🔧 Customization

### **Add New Export Format**
```python
# In services.py
class NewExportService:
    @staticmethod
    def export_result(result: TeamAssignmentResult, file_path: str):
        # Your export logic here
        pass

# In team_picker_app.py
class TeamPickerApp:
    def __init__(self, student_file: str = "student_list.txt"):
        # ... existing code ...
        self.new_export_service = NewExportService()
```

### **Custom Student Data Source**
```python
# Extend StudentRepository in services.py
class DatabaseStudentRepository(StudentRepository):
    def load_students(self) -> List[Student]:
        # Load from database instead of file
        pass
```

## 🧪 Error Handling

The application includes comprehensive validation:
- File existence checks
- Team size validation
- Student count validation
- Type checking with hints
- Graceful error messages

## 📈 Performance

- **Lazy Loading:** Students loaded only when needed
- **Efficient Algorithms:** O(n) team assignment
- **Memory Conscious:** Generators where appropriate
- **Path Handling:** Modern pathlib usage

## 🎨 Code Quality

- **Type Hints:** Full typing support
- **Docstrings:** Comprehensive documentation
- **SRP:** Single responsibility per class
- **DRY:** No code duplication
- **SOLID:** Following SOLID principles

## 🔄 Migration from Old Version

If you're using the old `team_picker.py`:

```python
# Old way
from team_picker import TeamPicker
picker = TeamPicker()
result = picker.create_teams_by_size(4)

# New way
from team_picker_app import TeamPickerApp
app = TeamPickerApp()
result = app.create_teams_by_size(4)
exported = app.export_result(result)
```

## 📝 License

Educational use. Feel free to modify and extend.

---

**Happy team building with enhanced exports! 🎯📊🖼️** 