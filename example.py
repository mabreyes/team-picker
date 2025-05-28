#!/usr/bin/env python3
"""
Complete example of the Team Picker application.
This demonstrates all major features in a single script.
"""

import os
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
        "kimberly.mitchell@university.edu"
    ]
    
    with open("student_list.txt", "w", encoding="utf-8") as f:
        for email in sample_emails:
            f.write(f"{email}\n")
    
    print(f"📝 Created sample student_list.txt with {len(sample_emails)} students")


def main():
    print("🎯 Team Picker - Complete Example")
    print("=" * 60)
    
    # Check if student list exists, create sample if not
    if not Path("student_list.txt").exists():
        print("❗ No student_list.txt found. Creating sample file...")
        create_sample_student_list()
        print()
    
    try:
        # Initialize the team picker
        app = TeamPickerApp()
        
        print(f"📚 Loaded {app.get_student_count()} students from student_list.txt")
        print(f"📁 Output directory: {app.output_dir}")
        print()
        
        # Example 1: Create teams by count
        print("Example 1: Creating exactly 6 teams")
        print("-" * 60)
        
        result = app.create_teams_by_count(6)
        print(app.format_result(result))
        
        exports = app.export_result(result, "teams_by_count")
        print(f"✅ Exported:")
        print(f"   📄 JSON: {exports['json_file']}")
        print(f"   🖼️  Image: {exports['image_file']}")
        
        print("\n" + "=" * 60)
        
        # Show generated files summary
        print("\nGenerated files:")
        print("-" * 60)
        
        if Path("output").exists():
            for root, dirs, files in os.walk("output"):
                for file in files:
                    file_path = Path(root) / file
                    size = file_path.stat().st_size
                    print(f"   {file_path} ({size:,} bytes)")
        
        print(f"\n🎉 Example complete!")
        print(f"📊 Created {result.num_teams} teams with equal distribution")
        print(f"📄 Generated JSON files with structured data")
        print(f"🖼️  Generated PNG images with visual layouts")
        print(f"📁 All files organized in output/ directory")
        
        print(f"\n💻 Quick API Usage:")
        print(f"   from team_picker_app import TeamPickerApp")
        print(f"   app = TeamPickerApp()")
        print(f"   result = app.create_teams_by_count(6)")
        print(f"   exports = app.export_result(result, 'my_teams')")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n💡 To get started:")
        print("   1. Create a 'student_list.txt' file")
        print("   2. Add one email address per line")
        print("   3. Run this example again")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()