#!/usr/bin/env python3
"""Team Picker Legacy Module.

Legacy team assignment functionality maintained for backward compatibility.
This module provides the original TeamPicker class interface.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, TypedDict


class StudentDict(TypedDict):
    """Type definition for student dictionary."""

    name: str
    email: str


class TeamDict(TypedDict):
    """Type definition for team dictionary."""

    team_number: int
    members: List[StudentDict]


class TeamPicker:
    """Legacy team picker class for backward compatibility.

    This class provides the original interface for team assignment
    while maintaining compatibility with existing code.
    """

    def __init__(self, student_file: str = "student_list.txt"):
        """Initialize the team picker with a student file.

        Args:
            student_file: Path to the file containing student emails
        """
        self.student_file = Path(student_file)
        self.students: List[StudentDict] = []
        self.load_students()

    def load_students(self) -> None:
        """Load students from the specified file."""
        if not self.student_file.exists():
            raise FileNotFoundError(f"Student file not found: {self.student_file}")

        self.students = []
        with open(self.student_file, "r", encoding="utf-8") as f:
            for line in f:
                email = line.strip()
                if email and "@" in email:
                    # Extract name from email
                    name = (
                        email.split("@")[0].replace(".", " ").replace("_", " ").title()
                    )
                    self.students.append({"name": name, "email": email})

        if not self.students:
            raise ValueError(f"No valid students found in {self.student_file}")

    def create_teams_by_size(
        self, team_size: int, shuffle: bool = True
    ) -> Dict[str, Any]:
        """Create teams with a specific size.

        Args:
            team_size: Desired size for each team
            shuffle: Whether to shuffle students before assignment

        Returns:
            Dictionary containing team assignment results

        Raises:
            ValueError: If team_size is invalid
        """
        if team_size <= 0:
            raise ValueError("Team size must be positive")
        if team_size > len(self.students):
            raise ValueError(
                f"Team size {team_size} is larger than total students "
                f"{len(self.students)}"
            )

        students = self.students.copy()
        if shuffle:
            random.shuffle(students)

        teams: List[TeamDict] = []
        num_complete_teams = len(students) // team_size
        remaining_students = len(students) % team_size

        # Create complete teams
        for i in range(num_complete_teams):
            start_idx = i * team_size
            end_idx = start_idx + team_size
            team_members = students[start_idx:end_idx]
            teams.append({"team_number": i + 1, "members": team_members})

        # Distribute remaining students to existing teams
        if remaining_students > 0 and teams:
            remaining = students[num_complete_teams * team_size :]
            for i, student in enumerate(remaining):
                teams[i % len(teams)]["members"].append(student)

        return {
            "teams": teams,
            "method": "by_size",
            "total_students": len(self.students),
            "num_teams": len(teams),
            "base_team_size": team_size,
        }

    def create_teams_by_count(
        self, num_teams: int, shuffle: bool = True
    ) -> Dict[str, Any]:
        """Create a specific number of teams.

        Args:
            num_teams: Number of teams to create
            shuffle: Whether to shuffle students before assignment

        Returns:
            Dictionary containing team assignment results

        Raises:
            ValueError: If num_teams is invalid
        """
        if num_teams <= 0:
            raise ValueError("Number of teams must be positive")
        if num_teams > len(self.students):
            raise ValueError(
                f"Cannot create {num_teams} teams with only "
                f"{len(self.students)} students"
            )

        students = self.students.copy()
        if shuffle:
            random.shuffle(students)

        # Calculate team sizes
        base_size = len(students) // num_teams
        extra_students = len(students) % num_teams

        teams: List[TeamDict] = []
        student_index = 0

        for team_num in range(1, num_teams + 1):
            # Some teams get an extra student if there's a remainder
            team_size = base_size + (1 if team_num <= extra_students else 0)
            team_members = students[student_index : student_index + team_size]
            teams.append({"team_number": team_num, "members": team_members})
            student_index += team_size

        return {
            "teams": teams,
            "method": "by_count",
            "total_students": len(self.students),
            "num_teams": num_teams,
            "base_team_size": base_size,
        }

    def format_teams_output(self, result: Dict[str, Any]) -> str:
        """Format team assignment results for display.

        Args:
            result: Team assignment result dictionary

        Returns:
            Formatted string representation of the teams
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TEAM ASSIGNMENT RESULTS")
        lines.append("=" * 60)
        lines.append(f"Method: {result['method'].replace('_', ' ').title()}")
        lines.append(f"Total Students: {result['total_students']}")
        lines.append(f"Number of Teams: {result['num_teams']}")
        lines.append(f"Base Team Size: {result['base_team_size']}")
        lines.append("")

        for team in result["teams"]:
            lines.append(
                f"Team {team['team_number']} ({len(team['members'])} members):"
            )
            lines.append("-" * 30)
            for i, member in enumerate(team["members"], 1):
                lines.append(f"  {i:2d}. {member['name']}")
            lines.append("")

        return "\n".join(lines)

    def save_teams_to_json(self, result: Dict[str, Any], filename: str) -> None:
        """Save team assignment results to a JSON file.

        Args:
            result: Team assignment result dictionary
            filename: Output filename (with or without .json extension)
        """
        if not filename.endswith(".json"):
            filename += ".json"

        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    def get_student_count(self) -> int:
        """Get the number of loaded students.

        Returns:
            Number of students
        """
        return len(self.students)

    def get_students(self) -> List[StudentDict]:
        """Get the list of loaded students.

        Returns:
            List of student dictionaries
        """
        return self.students.copy()
