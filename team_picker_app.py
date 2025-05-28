#!/usr/bin/env python3
"""Team Picker Application.

Main application class that coordinates all services
and provides a clean API for team assignment operations.
"""

from pathlib import Path
from typing import Dict, List

from models import Student, TeamAssignmentResult
from services import (
    ImageExportService,
    JsonExportService,
    OutputFormatter,
    StudentRepository,
    TeamAssignmentService,
)


class TeamPickerApp:
    """Main application class coordinating all team picker functionality."""

    def __init__(
        self, student_file: str = "student_list.txt", output_dir: str = "output"
    ):
        """Initialize the team picker application.

        Args:
            student_file: Path to the student list file
            output_dir: Directory for output files
        """
        self.student_repository = StudentRepository(student_file)
        self.assignment_service = TeamAssignmentService()
        self.json_service = JsonExportService()
        self.image_service = ImageExportService()
        self.formatter = OutputFormatter()
        self.output_dir = Path(output_dir)

    def load_students(self) -> List[Student]:
        """Load students from the configured file.

        Returns:
            List of Student objects
        """
        return self.student_repository.load_students()

    def create_teams_by_count(self, num_teams: int) -> TeamAssignmentResult:
        """Create a specific number of teams.

        Args:
            num_teams: Number of teams to create

        Returns:
            TeamAssignmentResult with assignment details
        """
        students = self.load_students()
        return self.assignment_service.assign_by_team_count(students, num_teams)

    def create_teams_by_size(self, team_size: int) -> TeamAssignmentResult:
        """Create teams of a specific size.

        Args:
            team_size: Desired size for each team

        Returns:
            TeamAssignmentResult with assignment details
        """
        students = self.load_students()
        return self.assignment_service.assign_by_team_size(students, team_size)

    def format_result(self, result: TeamAssignmentResult) -> str:
        """Format team assignment result for display.

        Args:
            result: Team assignment result to format

        Returns:
            Formatted string representation
        """
        return self.formatter.format_result(result)

    def export_result(
        self, result: TeamAssignmentResult, filename: str
    ) -> Dict[str, str]:
        """Export team assignment result to JSON and image files.

        Args:
            result: Team assignment result to export
            filename: Base filename (without extension)

        Returns:
            Dictionary with paths to created files
        """
        # Create output directories
        json_dir = self.output_dir / "json"
        image_dir = self.output_dir / "images"

        # Export to JSON
        json_file = self.json_service.export_result(result, filename, json_dir)

        # Export to image
        image_file = self.image_service.export_result(result, filename, image_dir)

        return {
            "json_file": str(json_file),
            "image_file": str(image_file),
        }

    def export_student_list(self, filename: str) -> Dict[str, str]:
        """Export student list to JSON and image files.

        Args:
            filename: Base filename (without extension)

        Returns:
            Dictionary with paths to created files
        """
        students = self.load_students()

        # Create output directories
        json_dir = self.output_dir / "json"
        image_dir = self.output_dir / "images"

        # Export to JSON
        json_file = self.json_service.export_student_list(students, filename, json_dir)

        # Export to image
        image_file = self.image_service.export_student_list(
            students, filename, image_dir
        )

        return {
            "json_file": str(json_file),
            "image_file": str(image_file),
        }

    def get_student_count(self) -> int:
        """Get the number of students in the loaded file.

        Returns:
            Number of students
        """
        return len(self.load_students())

    def get_output_directory(self) -> str:
        """Get the output directory path.

        Returns:
            Output directory path as string
        """
        return str(self.output_dir)

    def create_sample_student_file(self, num_students: int = 30) -> None:
        """Create a sample student file for testing.

        Args:
            num_students: Number of sample students to create
        """
        sample_emails = [
            f"student{i:02d}@dlsu.edu.ph" for i in range(1, num_students + 1)
        ]

        student_file = Path(self.student_repository.file_path)
        with open(student_file, "w", encoding="utf-8") as f:
            for email in sample_emails:
                f.write(f"{email}\n")

        print(f"Created sample student file: {student_file}")
        print(f"Generated {num_students} sample students")


def main():
    """Interactive main function."""
    app = TeamPickerApp()

    print("🎯 Team Picker Application (Enhanced)")
    print("=" * 50)
    print(f"Loaded {app.get_student_count()} students from file")
    print(f"Output directory: {app.get_output_directory()}")
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
                print("\n" + app.format_result(result))

                # Export options
                export_choice = (
                    input("\nExport results? (y/n): ").lower().startswith("y")
                )
                if export_choice:
                    custom_name = input(
                        "Enter custom filename (or press Enter for auto): "
                    ).strip()
                    export_name = custom_name if custom_name else None

                    exported = app.export_result(result, export_name)
                    print("\n✅ Exported to:")
                    print(f"   JSON: {exported['json_file']}")
                    print(f"   Image: {exported['image_file']}")

            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            students = app.load_students()
            print(f"\nLoaded {len(students)} students:")
            print("-" * 40)
            for i, student in enumerate(students, 1):
                print(f"{i:2d}. {student.name}")

        elif choice == "4":
            custom_name = input(
                "Enter custom filename (or press Enter for auto): "
            ).strip()
            export_name = custom_name if custom_name else None

            exported = app.export_student_list(export_name)
            print("\n✅ Student list exported to:")
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
