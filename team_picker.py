#!/usr/bin/env python3
"""
Team Picker Application
Randomly assigns people from a list to teams with customizable team sizes.
"""

import random
import math
from typing import List, Dict, Any
import json


class TeamPicker:
    def __init__(self):
        """Initialize the TeamPicker with the provided student list."""
        self.students = [
            "sheenery_abendan@dlsu.edu.ph",
            "lorenzo_ambrosio@dlsu.edu.ph",
            "wray_andres@dlsu.edu.ph",
            "samantha_michaela_bautista@dlsu.edu.ph",
            "noah_h_bernardo@dlsu.edu.ph",
            "ron_william_m_cajumban@dlsu.edu.ph",
            "jay_carlos@dlsu.edu.ph",
            "jason_dayrit@dlsu.edu.ph",
            "frances_julianne_delacruz@dlsu.edu.ph",
            "rafael_diaz@dlsu.edu.ph",
            "mikkel_gamboa@dlsu.edu.ph",
            "letty_hong@dlsu.edu.ph",
            "brandon_jaramillo@dlsu.edu.ph",
            "reign_larraquel@dlsu.edu.ph",
            "pablo_lucas@dlsu.edu.ph",
            "rafael_magadia@dlsu.edu.ph",
            "bryce_andrei_c_miranda@dlsu.edu.ph",
            "graham_joshua_ogatia@dlsu.edu.ph",
            "gyan_pe@dlsu.edu.ph",
            "ethan_pimentel@dlsu.edu.ph",
            "janica_megan_reyes@dlsu.edu.ph",
            "jose_lorenzo_santos@dlsu.edu.ph",
            "kaci_santos@dlsu.edu.ph",
            "keith_singson@dlsu.edu.ph",
            "john_angelo_soriano@dlsu.edu.ph",
            "naman_srivastava@dlsu.edu.ph",
            "lance_wilem_tiu@dlsu.edu.ph",
            "denis_leeroi_villamiel@dlsu.edu.ph",
            "vince_wang@dlsu.edu.ph",
            "waynes_wu@dlsu.edu.ph"
        ]
        self.total_students = len(self.students)
    
    def get_student_names(self) -> List[str]:
        """Extract readable names from email addresses."""
        names = []
        for email in self.students:
            # Extract name part before @dlsu.edu.ph and format it
            name_part = email.replace("@dlsu.edu.ph", "")
            # Replace underscores with spaces and title case
            formatted_name = name_part.replace("_", " ").title()
            names.append(formatted_name)
        return names
    
    def create_teams_by_size(self, team_size: int, shuffle: bool = True) -> Dict[str, Any]:
        """
        Create teams with a specific team size.
        
        Args:
            team_size: Number of people per team
            shuffle: Whether to shuffle the list before creating teams
            
        Returns:
            Dictionary containing teams and metadata
        """
        if team_size <= 0:
            raise ValueError("Team size must be greater than 0")
        
        if team_size > self.total_students:
            raise ValueError(f"Team size ({team_size}) cannot be larger than total students ({self.total_students})")
        
        students_copy = self.students.copy()
        if shuffle:
            random.shuffle(students_copy)
        
        teams = []
        num_complete_teams = self.total_students // team_size
        remaining_students = self.total_students % team_size
        
        # Create complete teams
        for i in range(num_complete_teams):
            start_idx = i * team_size
            end_idx = start_idx + team_size
            teams.append(students_copy[start_idx:end_idx])
        
        # Handle remaining students
        if remaining_students > 0:
            remaining = students_copy[num_complete_teams * team_size:]
            teams.append(remaining)
        
        return {
            "teams": teams,
            "team_size": team_size,
            "total_students": self.total_students,
            "num_teams": len(teams),
            "complete_teams": num_complete_teams,
            "remaining_students": remaining_students
        }
    
    def create_teams_by_count(self, num_teams: int, shuffle: bool = True) -> Dict[str, Any]:
        """
        Create a specific number of teams with as equal distribution as possible.
        
        Args:
            num_teams: Number of teams to create
            shuffle: Whether to shuffle the list before creating teams
            
        Returns:
            Dictionary containing teams and metadata
        """
        if num_teams <= 0:
            raise ValueError("Number of teams must be greater than 0")
        
        if num_teams > self.total_students:
            raise ValueError(f"Number of teams ({num_teams}) cannot be larger than total students ({self.total_students})")
        
        students_copy = self.students.copy()
        if shuffle:
            random.shuffle(students_copy)
        
        # Calculate base team size and remainder
        base_team_size = self.total_students // num_teams
        remainder = self.total_students % num_teams
        
        teams = []
        current_index = 0
        
        for i in range(num_teams):
            # Some teams get one extra member if there's a remainder
            team_size = base_team_size + (1 if i < remainder else 0)
            teams.append(students_copy[current_index:current_index + team_size])
            current_index += team_size
        
        return {
            "teams": teams,
            "num_teams": num_teams,
            "total_students": self.total_students,
            "base_team_size": base_team_size,
            "teams_with_extra": remainder
        }
    
    def format_teams_output(self, result: Dict[str, Any], use_names: bool = False) -> str:
        """
        Format the teams for display.
        
        Args:
            result: Result from create_teams_by_size or create_teams_by_count
            use_names: Whether to use formatted names instead of emails
            
        Returns:
            Formatted string representation of teams
        """
        output = []
        output.append("=" * 60)
        output.append("TEAM ASSIGNMENT RESULTS")
        output.append("=" * 60)
        
        if "team_size" in result:
            output.append(f"Target team size: {result['team_size']}")
            output.append(f"Complete teams: {result['complete_teams']}")
            if result['remaining_students'] > 0:
                output.append(f"Remaining students: {result['remaining_students']}")
        else:
            output.append(f"Number of teams: {result['num_teams']}")
            output.append(f"Base team size: {result['base_team_size']}")
            if result['teams_with_extra'] > 0:
                output.append(f"Teams with extra member: {result['teams_with_extra']}")
        
        output.append(f"Total students: {result['total_students']}")
        output.append("-" * 60)
        
        names = self.get_student_names() if use_names else None
        
        for i, team in enumerate(result['teams'], 1):
            output.append(f"\nTEAM {i} ({len(team)} members):")
            for j, student in enumerate(team, 1):
                if use_names:
                    student_idx = self.students.index(student)
                    display_name = names[student_idx]
                    output.append(f"  {j}. {display_name} ({student})")
                else:
                    output.append(f"  {j}. {student}")
        
        return "\n".join(output)
    
    def save_teams_to_file(self, result: Dict[str, Any], filename: str = "teams.json"):
        """Save team assignments to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Teams saved to {filename}")


def main():
    """Main interactive function."""
    picker = TeamPicker()
    
    print("🎯 Team Picker Application")
    print("=" * 40)
    print(f"Total students available: {picker.total_students}")
    print()
    
    while True:
        print("Choose an option:")
        print("1. Create teams by team size")
        print("2. Create teams by number of teams")
        print("3. View all students")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            try:
                team_size = int(input("Enter desired team size: "))
                use_names = input("Use formatted names instead of emails? (y/n): ").lower().startswith('y')
                
                result = picker.create_teams_by_size(team_size)
                print("\n" + picker.format_teams_output(result, use_names))
                
                save = input("\nSave to file? (y/n): ").lower().startswith('y')
                if save:
                    filename = input("Enter filename (default: teams.json): ").strip()
                    if not filename:
                        filename = "teams.json"
                    picker.save_teams_to_file(result, filename)
                
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == "2":
            try:
                num_teams = int(input("Enter number of teams: "))
                use_names = input("Use formatted names instead of emails? (y/n): ").lower().startswith('y')
                
                result = picker.create_teams_by_count(num_teams)
                print("\n" + picker.format_teams_output(result, use_names))
                
                save = input("\nSave to file? (y/n): ").lower().startswith('y')
                if save:
                    filename = input("Enter filename (default: teams.json): ").strip()
                    if not filename:
                        filename = "teams.json"
                    picker.save_teams_to_file(result, filename)
                
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == "3":
            print("\nAll Students:")
            print("-" * 40)
            names = picker.get_student_names()
            for i, (email, name) in enumerate(zip(picker.students, names), 1):
                print(f"{i:2d}. {name} ({email})")
        
        elif choice == "4":
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "=" * 40)


if __name__ == "__main__":
    main() 