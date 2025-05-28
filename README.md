# 🎯 Team Picker (Enhanced)

A Pythonic team assignment application following **Single Responsibility Principle (SRP)** with JSON and image export capabilities. Loads student data from a text file and provides flexible team assignment with multiple export formats.

## ✨ Features

### **Core Functionality**
- **Two Assignment Methods:**
  - Create teams by specifying team size (e.g., teams of 4 people each)
  - Create teams by specifying number of teams (e.g., create 6 teams total)

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
- **Pathlib:** Modern file path handling

## 📁 Project Structure

```
team-picker/
├── models.py              # Data classes (Student, Team, TeamAssignmentResult)
├── services.py            # Service classes following SRP
├── team_picker_app.py     # Main application coordinator
├── example.py             # Complete usage examples
├── student_list.txt       # Your student data (create this file)
├── requirements.txt       # Dependencies
├── README.md             # This documentation
└── output/               # Generated exports (auto-created)
    ├── json/            # JSON export files
    └── images/          # PNG image files
```

## 🏗️ Architecture (SRP)

### **Data Models** (`models.py`)
- `Student`: Represents a student with email and formatted name
- `Team`: Represents a team with members and metadata
- `TeamAssignmentResult`: Complete assignment result with statistics
- `AssignmentMethod`: Enumeration for assignment types

### **Services** (`services.py`)
- `StudentRepository`: Handles loading students from text file
- `TeamAssignmentService`: Core team assignment logic
- `JsonExportService`: JSON file export functionality
- `ImageExportService`: PNG image generation with **all names visible**
- `OutputFormatter`: Text formatting for console display

### **Application** (`team_picker_app.py`)
- `TeamPickerApp`: Main coordinator using dependency injection

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Your Student List
Create a `student_list.txt` file with one email per line:

```txt
john.doe@university.edu
jane.smith@university.edu
alex.johnson@university.edu
maria.garcia@university.edu
david.brown@university.edu
```

### 3. Run the Example
```bash
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