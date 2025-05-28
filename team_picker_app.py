#!/usr/bin/env python3
"""
Main Team Picker Application class.
Coordinates all services following dependency injection and SRP.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from models import TeamAssignmentResult
from services import (
    StudentRepository,
    TeamAssignmentService,
    JsonExportService,
    ImageExportService,
    OutputFormatter
)


class TeamPickerApp:
    """Main application class coordinating all services."""
    
    def __init__(self, student_file: str = "student_list.txt"):
        """Initialize the application with dependency injection."""
        self.student_repository = StudentRepository(student_file)
        self.assignment_service = TeamAssignmentService(self.student_repository)
        self.json_export_service = JsonExportService()
        self.image_export_service = ImageExportService()
        self.formatter = OutputFormatter()
        
        # Create output directories
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "json").mkdir(exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
    
    def get_students(self):
        """Get all students."""
        return self.student_repository.students
    
    def get_student_count(self) -> int:
        """Get the number of students."""
        return self.student_repository.count
    
    def create_teams_by_size(self, team_size: int, shuffle: bool = True) -> TeamAssignmentResult:
        """Create teams with specific size."""
        return self.assignment_service.assign_by_size(team_size, shuffle)
    
    def create_teams_by_count(self, num_teams: int, shuffle: bool = True) -> TeamAssignmentResult:
        """Create specific number of teams."""
        return self.assignment_service.assign_by_count(num_teams, shuffle)
    
    def export_result(self, result: TeamAssignmentResult, base_name: Optional[str] = None) -> dict:
        """Export result to both JSON and image formats."""
        if base_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"teams_{result.method.value}_{timestamp}"
        
        # Export paths
        json_path = self.output_dir / "json" / f"{base_name}.json"
        image_path = self.output_dir / "images" / f"{base_name}.png"
        
        # Export to JSON
        self.json_export_service.export_result(result, str(json_path))
        
        # Export to image
        self.image_export_service.export_teams_as_image(result, str(image_path))
        
        return {
            "json_file": str(json_path),
            "image_file": str(image_path)
        }
    
    def export_students(self, base_name: Optional[str] = None) -> dict:
        """Export student list to both JSON and image formats."""
        if base_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"students_{timestamp}"
        
        students = self.student_repository.students
        
        # Export paths
        json_path = self.output_dir / "json" / f"{base_name}.json"
        image_path = self.output_dir / "images" / f"{base_name}.png"
        
        # Export to JSON
        self.json_export_service.export_students(students, str(json_path))
        
        # Export to image
        self.image_export_service.export_students_as_image(students, str(image_path))
        
        return {
            "json_file": str(json_path),
            "image_file": str(image_path)
        }
    
    def format_result(self, result: TeamAssignmentResult, use_names: bool = True) -> str:
        """Format result for display."""
        return self.formatter.format_result(result, use_names)
    
    def format_students(self) -> str:
        """Format student list for display."""
        return self.formatter.format_students(self.student_repository.students)


def main():
    """Interactive main function."""
    app = TeamPickerApp()
    
    print("🎯 Team Picker Application (Enhanced)")
    print("=" * 50)
    print(f"Loaded {app.get_student_count()} students from file")
    print(f"Output directory: {app.output_dir}")
    print()
    
    while True:
        print("Choose an option:")
        print("1. Create teams by team size")
        print("2. Create teams by number of teams")
        print("3. View all students")
        print("4. Export student list")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice in ["1", "2"]:
            try:
                if choice == "1":
                    team_size = int(input("Enter desired team size: "))
                    result = app.create_teams_by_size(team_size)
                else:
                    num_teams = int(input("Enter number of teams: "))
                    result = app.create_teams_by_count(num_teams)
                
                # Display result
                use_names = input("Show formatted names? (y/n): ").lower().startswith('y')
                print("\n" + app.format_result(result, use_names))
                
                # Export options
                export_choice = input("\nExport results? (y/n): ").lower().startswith('y')
                if export_choice:
                    custom_name = input("Enter custom filename (or press Enter for auto): ").strip()
                    export_name = custom_name if custom_name else None
                    
                    exported = app.export_result(result, export_name)
                    print(f"\n✅ Exported to:")
                    print(f"   JSON: {exported['json_file']}")
                    print(f"   Image: {exported['image_file']}")
                
            except ValueError as e:
                print(f"❌ Error: {e}")
        
        elif choice == "3":
            print("\n" + app.format_students())
        
        elif choice == "4":
            custom_name = input("Enter custom filename (or press Enter for auto): ").strip()
            export_name = custom_name if custom_name else None
            
            exported = app.export_students(export_name)
            print(f"\n✅ Student list exported to:")
            print(f"   JSON: {exported['json_file']}")
            print(f"   Image: {exported['image_file']}")
        
        elif choice == "5":
            print("Goodbye! 👋")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main() 