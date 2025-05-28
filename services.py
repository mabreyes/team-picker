#!/usr/bin/env python3
"""Team Picker Services.

Service classes implementing the Single Responsibility Principle
for team assignment, data export, and file management operations.
"""

import json
import math
import random
from pathlib import Path
from typing import List

import matplotlib.patches as patches
import matplotlib.pyplot as plt

from models import AssignmentMethod, Student, Team, TeamAssignmentResult


class StudentRepository:
    """Handles loading and managing student data from files."""

    def __init__(self, file_path: str):
        """Initialize the repository with a file path.

        Args:
            file_path: Path to the student list file
        """
        self.file_path = Path(file_path)

    def load_students(self) -> List[Student]:
        """Load students from the configured file.

        Returns:
            List of Student objects

        Raises:
            FileNotFoundError: If the student file doesn't exist
            ValueError: If no valid students found in file
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Student file not found: {self.file_path}")

        students = []
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                email = line.strip()
                if email and "@" in email:
                    try:
                        student = Student(email=email)
                        students.append(student)
                    except ValueError as e:
                        print(
                            f"Warning: Invalid email on line {line_num}: {email} - {e}"
                        )

        if not students:
            raise ValueError(f"No valid students found in {self.file_path}")

        return students


class TeamAssignmentService:
    """Handles team assignment logic and algorithms."""

    def __init__(self):
        """Initialize the team assignment service."""
        pass

    def assign_by_team_count(
        self, students: List[Student], num_teams: int
    ) -> TeamAssignmentResult:
        """Assign students to a specific number of teams.

        Args:
            students: List of students to assign
            num_teams: Number of teams to create

        Returns:
            TeamAssignmentResult with assignment details

        Raises:
            ValueError: If num_teams is invalid
        """
        if num_teams <= 0:
            raise ValueError("Number of teams must be positive")
        if num_teams > len(students):
            raise ValueError(
                f"Cannot create {num_teams} teams with only {len(students)} students"
            )

        # Shuffle students for random assignment
        shuffled_students = students.copy()
        random.shuffle(shuffled_students)

        # Calculate team sizes
        base_size = len(students) // num_teams
        extra_students = len(students) % num_teams

        teams = []
        student_index = 0

        for team_num in range(1, num_teams + 1):
            # Some teams get an extra student if there's a remainder
            team_size = base_size + (1 if team_num <= extra_students else 0)
            team_students = shuffled_students[student_index : student_index + team_size]

            team = Team(team_number=team_num, members=team_students)
            teams.append(team)
            student_index += team_size

        return TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=len(students),
            num_teams=num_teams,
            base_team_size=base_size,
        )

    def assign_by_team_size(
        self, students: List[Student], team_size: int
    ) -> TeamAssignmentResult:
        """Assign students to teams of a specific size.

        Args:
            students: List of students to assign
            team_size: Desired size for each team

        Returns:
            TeamAssignmentResult with assignment details

        Raises:
            ValueError: If team_size is invalid
        """
        if team_size <= 0:
            raise ValueError("Team size must be positive")
        if team_size > len(students):
            raise ValueError(
                f"Team size {team_size} is larger than total students {len(students)}"
            )

        # Shuffle students for random assignment
        shuffled_students = students.copy()
        random.shuffle(shuffled_students)

        teams = []
        num_complete_teams = len(students) // team_size
        remaining_students = len(students) % team_size

        # Create complete teams
        for team_num in range(1, num_complete_teams + 1):
            start_idx = (team_num - 1) * team_size
            end_idx = start_idx + team_size
            team_students = shuffled_students[start_idx:end_idx]

            team = Team(team_number=team_num, members=team_students)
            teams.append(team)

        # Handle remaining students
        if remaining_students > 0:
            remaining = shuffled_students[num_complete_teams * team_size :]

            # Distribute remaining students to existing teams
            for i, student in enumerate(remaining):
                teams[i % len(teams)].members.append(student)

        return TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=len(students),
            num_teams=len(teams),
            base_team_size=team_size,
        )


class JsonExportService:
    """Handles JSON export functionality."""

    def __init__(self):
        """Initialize the JSON export service."""
        pass

    def export_result(
        self, result: TeamAssignmentResult, filename: str, output_dir: Path
    ) -> Path:
        """Export team assignment result to JSON file.

        Args:
            result: Team assignment result to export
            filename: Base filename (without extension)
            output_dir: Directory to save the file

        Returns:
            Path to the created JSON file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert result to dictionary
        data = {
            "metadata": {
                "method": result.method.value,
                "total_students": result.total_students,
                "num_teams": result.num_teams,
                "base_team_size": result.base_team_size,
                "timestamp": result.timestamp.isoformat(),
            },
            "teams": [
                {
                    "team_number": team.team_number,
                    "size": team.size,
                    "members": [
                        {"name": member.name, "email": member.email}
                        for member in team.members
                    ],
                }
                for team in result.teams
            ],
        }

        json_file = output_dir / f"{filename}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return json_file

    def export_student_list(
        self, students: List[Student], filename: str, output_dir: Path
    ) -> Path:
        """Export student list to JSON file.

        Args:
            students: List of students to export
            filename: Base filename (without extension)
            output_dir: Directory to save the file

        Returns:
            Path to the created JSON file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": {
                "total_students": len(students),
                "export_type": "student_list",
            },
            "students": [
                {"name": student.name, "email": student.email} for student in students
            ],
        }

        json_file = output_dir / f"{filename}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return json_file


class ImageExportService:
    """Handles image export functionality with professional styling."""

    def __init__(self):
        """Initialize the image export service."""
        # Configure matplotlib for high-quality output
        plt.rcParams.update(
            {
                "font.family": [
                    "Helvetica Neue",
                    "Helvetica",
                    "Arial",
                    "DejaVu Sans",
                    "sans-serif",
                ],
                "font.size": 10,
                "figure.dpi": 300,
                "savefig.dpi": 300,
                "savefig.bbox": "tight",
                "savefig.facecolor": "white",
                "axes.facecolor": "white",
            }
        )

    def export_result(
        self, result: TeamAssignmentResult, filename: str, output_dir: Path
    ) -> Path:
        """Export team assignment result as a professional image.

        Args:
            result: Team assignment result to export
            filename: Base filename (without extension)
            output_dir: Directory to save the file

        Returns:
            Path to the created image file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Calculate dynamic sizing based on content
        max_team_size = max(team.size for team in result.teams)
        num_teams = len(result.teams)

        # Dynamic figure sizing
        base_width = 16
        base_height = max(12, num_teams * 2 + max_team_size * 0.5)

        fig, ax = plt.subplots(figsize=(base_width, base_height))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

        # Color palette for teams
        colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#98D8C8",
            "#F7DC6F",
            "#BB8FCE",
            "#85C1E9",
            "#F8C471",
            "#82E0AA",
            "#F1948A",
            "#85C1E9",
            "#D7BDE2",
        ]

        # Header
        header_text = (
            f"Team Assignment Results - {result.method.value.replace('_', ' ').title()}"
        )
        ax.text(
            5,
            9.5,
            header_text,
            fontsize=20,
            fontweight="bold",
            ha="center",
            va="center",
        )

        # Metadata
        metadata_text = (
            f"Total Students: {result.total_students} | "
            f"Teams: {result.num_teams} | "
            f"Base Size: {result.base_team_size}"
        )
        ax.text(5, 9, metadata_text, fontsize=12, ha="center", va="center", alpha=0.7)

        # Calculate layout
        cols = min(3, num_teams)

        card_width = 2.8
        card_height = max(2.5, max_team_size * 0.3 + 1.5)

        start_x = (10 - (cols * card_width + (cols - 1) * 0.3)) / 2
        start_y = 8 - card_height

        for i, team in enumerate(result.teams):
            row = i // cols
            col = i % cols

            x = start_x + col * (card_width + 0.3)
            y = start_y - row * (card_height + 0.4)

            # Team card with gradient effect
            color = colors[i % len(colors)]

            # Main card
            card = patches.FancyBboxPatch(
                (x, y),
                card_width,
                card_height,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor="white",
                linewidth=2,
                alpha=0.9,
            )
            ax.add_patch(card)

            # Shadow effect
            shadow = patches.FancyBboxPatch(
                (x + 0.05, y - 0.05),
                card_width,
                card_height,
                boxstyle="round,pad=0.05",
                facecolor="gray",
                alpha=0.3,
                zorder=0,
            )
            ax.add_patch(shadow)

            # Team header
            ax.text(
                x + card_width / 2,
                y + card_height - 0.3,
                f"Team {team.team_number}",
                fontsize=14,
                fontweight="bold",
                ha="center",
                va="center",
                color="white",
            )

            ax.text(
                x + card_width / 2,
                y + card_height - 0.6,
                f"({team.size} members)",
                fontsize=10,
                ha="center",
                va="center",
                color="white",
                alpha=0.9,
            )

            # Team members - show all names
            member_start_y = y + card_height - 1.0
            line_height = 0.25

            for j, member in enumerate(team.members):
                member_y = member_start_y - j * line_height
                ax.text(
                    x + 0.15,
                    member_y,
                    f"• {member.name}",
                    fontsize=9,
                    ha="left",
                    va="center",
                    color="white",
                    fontweight="500",
                )

        # Footer with GitHub link
        footer_text = "Generated by github.com/mabreyes/team-picker"
        ax.text(
            5,
            0.3,
            footer_text,
            fontsize=10,
            ha="center",
            va="center",
            alpha=0.6,
            style="italic",
        )

        # Save the image
        image_file = output_dir / f"{filename}.png"
        plt.savefig(image_file, bbox_inches="tight", pad_inches=0.2)
        plt.close()

        return image_file

    def export_student_list(
        self, students: List[Student], filename: str, output_dir: Path
    ) -> Path:
        """Export student list as a professional image.

        Args:
            students: List of students to export
            filename: Base filename (without extension)
            output_dir: Directory to save the file

        Returns:
            Path to the created image file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Dynamic sizing based on student count
        num_students = len(students)
        cols = 3
        rows = math.ceil(num_students / cols)

        fig_width = 16
        fig_height = max(12, rows * 0.4 + 4)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

        # Header
        ax.text(
            5,
            9.5,
            "Student List",
            fontsize=24,
            fontweight="bold",
            ha="center",
            va="center",
        )
        ax.text(
            5,
            9,
            f"Total Students: {num_students}",
            fontsize=14,
            ha="center",
            va="center",
            alpha=0.7,
        )

        # Student list in columns
        col_width = 3
        start_x = (10 - cols * col_width) / 2
        start_y = 8.2

        for i, student in enumerate(students):
            col = i % cols
            row = i // cols

            x = start_x + col * col_width
            y = start_y - row * 0.3

            # Alternate row colors for readability
            if row % 2 == 0:
                bg_color = "#F8F9FA"
            else:
                bg_color = "#FFFFFF"

            # Background for readability
            bg_rect = patches.Rectangle(
                (x - 0.1, y - 0.1),
                col_width - 0.2,
                0.25,
                facecolor=bg_color,
                alpha=0.8,
                zorder=0,
            )
            ax.add_patch(bg_rect)

            ax.text(
                x,
                y,
                f"{i+1:2d}. {student.name}",
                fontsize=10,
                ha="left",
                va="center",
                fontweight="500",
            )

        # Footer with GitHub link
        footer_text = "Generated by github.com/mabreyes/team-picker"
        ax.text(
            5,
            0.5,
            footer_text,
            fontsize=10,
            ha="center",
            va="center",
            alpha=0.6,
            style="italic",
        )

        # Save the image
        image_file = output_dir / f"{filename}.png"
        plt.savefig(image_file, bbox_inches="tight", pad_inches=0.2)
        plt.close()

        return image_file


class OutputFormatter:
    """Handles text output formatting for console display."""

    @staticmethod
    def format_result(result: TeamAssignmentResult) -> str:
        """Format team assignment result for console output.

        Args:
            result: Team assignment result to format

        Returns:
            Formatted string representation
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TEAM ASSIGNMENT RESULTS")
        lines.append("=" * 60)
        lines.append(f"Method: {result.method.value.replace('_', ' ').title()}")
        lines.append(f"Total Students: {result.total_students}")
        lines.append(f"Number of Teams: {result.num_teams}")
        lines.append(f"Base Team Size: {result.base_team_size}")
        lines.append(f"Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        for team in result.teams:
            lines.append(f"Team {team.team_number} ({team.size} members):")
            lines.append("-" * 30)
            for i, member in enumerate(team.members, 1):
                lines.append(f"  {i:2d}. {member.name}")
            lines.append("")

        return "\n".join(lines)
