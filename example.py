#!/usr/bin/env python3
"""
Team Picker - Complete Example
Demonstrates all features: loading from file, creating teams, and exporting to JSON/images.
"""

from team_picker_app import TeamPickerApp
from pathlib import Path


def main():
    """Complete demonstration of the team picker functionality."""
    print("🎯 Team Picker - Complete Example")
    print("=" * 60)
    
    # Initialize the application (loads from student_list.txt)
    app = TeamPickerApp()
    
    print(f"📚 Loaded {app.get_student_count()} students from student_list.txt")
    print(f"📁 Output directory: {app.output_dir}")
    print()
    
    # Example 1: Create exactly 6 teams (equal distribution)
    print("Example 1: Creating exactly 6 teams")
    print("-" * 60)
    result1 = app.create_teams_by_count(6)
    print(app.format_result(result1, use_names=True))
    
    # Export with auto-generated filename
    exported1 = app.export_result(result1)
    print(f"\n✅ Exported:")
    print(f"   📄 JSON: {exported1['json_file']}")
    print(f"   🖼️  Image: {exported1['image_file']}")
    print("\n" + "=" * 60)
    
    # Show generated files
    print("\nGenerated files:")
    print("-" * 60)
    if Path("output").exists():
        for file_path in sorted(Path("output").rglob("*")):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"   {file_path.relative_to('.')} ({size:,} bytes)")
    
    # Summary
    print(f"\n🎉 Example complete!")
    print(f"📊 Created 6 teams with equal distribution")
    print(f"📄 Generated JSON files with structured data")
    print(f"🖼️  Generated PNG images with visual layouts")
    print(f"📁 All files organized in output/ directory")
    
    # Quick API usage examples
    print(f"\n💻 Quick API Usage:")
    print(f"   from team_picker_app import TeamPickerApp")
    print(f"   app = TeamPickerApp()")
    print(f"   result = app.create_teams_by_count(6)")
    print(f"   exports = app.export_result(result, 'my_teams')")


if __name__ == "__main__":
    main()