#!/usr/bin/env python3
"""Team Picker Example Usage.

This example demonstrates how to use the Team Picker application
to load students from a file and create teams using different methods.
"""

from pathlib import Path

from team_picker_app import TeamPickerApp


def create_sample_student_list():
    """Create a sample student list file for demonstration."""
    sample_emails = [
        "john.doe@university.edu",
        "jane.smith@university.edu",
        "alex.johnson@university.edu",
        "maria.garcia@university.edu",
        "david.brown@university.edu",
        "sarah.wilson@university.edu",
        "michael.davis@university.edu",
        "emily.taylor@university.edu",
        "james.anderson@university.edu",
        "lisa.thomas@university.edu",
        "robert.jackson@university.edu",
        "jennifer.white@university.edu",
        "william.harris@university.edu",
        "amanda.martin@university.edu",
        "christopher.lee@university.edu",
        "melissa.clark@university.edu",
        "matthew.lewis@university.edu",
        "ashley.walker@university.edu",
        "daniel.hall@university.edu",
        "stephanie.young@university.edu",
        "joseph.king@university.edu",
        "nicole.wright@university.edu",
        "anthony.lopez@university.edu",
        "rachel.hill@university.edu",
        "mark.green@university.edu",
        "laura.adams@university.edu",
        "steven.baker@university.edu",
        "michelle.nelson@university.edu",
        "kevin.carter@university.edu",
        "kimberly.mitchell@university.edu",
    ]

    with open("student_list.txt", "w", encoding="utf-8") as f:
        for email in sample_emails:
            f.write(f"{email}\n")

    print(f"📝 Created sample student_list.txt with {len(sample_emails)} students")


def main():
    """Run the team picker example with sample data."""
    # Create sample student list if it doesn't exist
    student_file = "student_list.txt"

    if not Path(student_file).exists():
        print("Creating sample student list...")
        sample_students = [
            "john.doe@dlsu.edu.ph",
            "jane.smith@dlsu.edu.ph",
            "alex.johnson@dlsu.edu.ph",
            "maria.garcia@dlsu.edu.ph",
            "david.brown@dlsu.edu.ph",
            "sarah.wilson@dlsu.edu.ph",
            "michael.davis@dlsu.edu.ph",
            "emily.taylor@dlsu.edu.ph",
            "james.anderson@dlsu.edu.ph",
            "lisa.thomas@dlsu.edu.ph",
            "robert.jackson@dlsu.edu.ph",
            "jennifer.white@dlsu.edu.ph",
            "christopher.martin@dlsu.edu.ph",
            "amanda.thompson@dlsu.edu.ph",
            "daniel.rodriguez@dlsu.edu.ph",
            "michelle.lee@dlsu.edu.ph",
            "kevin.clark@dlsu.edu.ph",
            "stephanie.lewis@dlsu.edu.ph",
            "brian.walker@dlsu.edu.ph",
            "nicole.hall@dlsu.edu.ph",
            "ryan.allen@dlsu.edu.ph",
            "jessica.young@dlsu.edu.ph",
            "matthew.king@dlsu.edu.ph",
            "ashley.wright@dlsu.edu.ph",
            "joshua.lopez@dlsu.edu.ph",
            "megan.hill@dlsu.edu.ph",
            "andrew.scott@dlsu.edu.ph",
            "rachel.green@dlsu.edu.ph",
            "tyler.adams@dlsu.edu.ph",
            "lauren.baker@dlsu.edu.ph",
        ]

        with open(student_file, "w", encoding="utf-8") as f:
            for email in sample_students:
                f.write(f"{email}\n")

        print(f"Created {student_file} with {len(sample_students)} students")

    # Initialize the team picker app
    app = TeamPickerApp(student_file)

    print("\n" + "=" * 60)
    print("TEAM PICKER EXAMPLE")
    print("=" * 60)

    # Load and display students
    students = app.load_students()
    print(f"\nLoaded {len(students)} students from {student_file}")

    # Example 1: Create teams by count (4 teams)
    print("\n" + "-" * 40)
    print("Example 1: Create 4 teams")
    print("-" * 40)

    result1 = app.create_teams_by_count(4)
    print(app.format_result(result1))

    # Export results
    exports1 = app.export_result(result1, "example_4_teams")
    print("\nExported files:")
    print(f"  JSON: {exports1['json_file']}")
    print(f"  Image: {exports1['image_file']}")

    # Example 2: Create teams by size (teams of 5)
    print("\n" + "-" * 40)
    print("Example 2: Create teams of 5 students each")
    print("-" * 40)

    result2 = app.create_teams_by_size(5)
    print(app.format_result(result2))

    # Export results
    exports2 = app.export_result(result2, "example_teams_of_5")
    print("\nExported files:")
    print(f"  JSON: {exports2['json_file']}")
    print(f"  Image: {exports2['image_file']}")

    # Example 3: Create student list visualization
    print("\n" + "-" * 40)
    print("Example 3: Create student list visualization")
    print("-" * 40)

    exports3 = app.export_student_list("example_student_list")
    print("Student list exported:")
    print(f"  Image: {exports3['image_file']}")

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)
    print("Check the 'output/' directory for generated files:")
    print("  - JSON files with team assignments")
    print("  - PNG images with visual team layouts")
    print("  - Student list visualization")


if __name__ == "__main__":
    main()
