#!/usr/bin/env python3
"""
Service classes for the Team Picker application.
Each class has a single responsibility following SRP.
"""

import random
import json
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

from models import Student, Team, TeamAssignmentResult, AssignmentMethod


class StudentRepository:
    """Handles loading and managing student data."""
    
    def __init__(self, file_path: str = "student_list.txt"):
        self.file_path = Path(file_path)
        self._students: Optional[List[Student]] = None
    
    def load_students(self) -> List[Student]:
        """Load students from text file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Student file not found: {self.file_path}")
        
        students = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    students.append(Student(email=email))
        
        self._students = students
        return students
    
    @property
    def students(self) -> List[Student]:
        """Get cached students or load them."""
        if self._students is None:
            return self.load_students()
        return self._students
    
    @property
    def count(self) -> int:
        """Get the number of students."""
        return len(self.students)


class TeamAssignmentService:
    """Handles team assignment logic."""
    
    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository
    
    def assign_by_size(self, team_size: int, shuffle: bool = True) -> TeamAssignmentResult:
        """Assign students to teams of specific size."""
        if team_size <= 0:
            raise ValueError("Team size must be greater than 0")
        
        students = self.student_repository.students.copy()
        if team_size > len(students):
            raise ValueError(f"Team size ({team_size}) cannot be larger than total students ({len(students)})")
        
        if shuffle:
            random.shuffle(students)
        
        teams = []
        current_index = 0
        team_number = 1
        
        while current_index < len(students):
            team_members = students[current_index:current_index + team_size]
            team = Team(members=team_members, team_number=team_number)
            teams.append(team)
            current_index += team_size
            team_number += 1
        
        return TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=len(students),
            requested_value=team_size
        )
    
    def assign_by_count(self, num_teams: int, shuffle: bool = True) -> TeamAssignmentResult:
        """Assign students to a specific number of teams."""
        if num_teams <= 0:
            raise ValueError("Number of teams must be greater than 0")
        
        students = self.student_repository.students.copy()
        if num_teams > len(students):
            raise ValueError(f"Number of teams ({num_teams}) cannot be larger than total students ({len(students)})")
        
        if shuffle:
            random.shuffle(students)
        
        # Calculate team sizes
        base_size = len(students) // num_teams
        remainder = len(students) % num_teams
        
        teams = []
        current_index = 0
        
        for i in range(num_teams):
            # Some teams get one extra member
            team_size = base_size + (1 if i < remainder else 0)
            team_members = students[current_index:current_index + team_size]
            team = Team(members=team_members, team_number=i + 1)
            teams.append(team)
            current_index += team_size
        
        return TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=len(students),
            requested_value=num_teams
        )


class JsonExportService:
    """Handles JSON export functionality."""
    
    @staticmethod
    def export_result(result: TeamAssignmentResult, file_path: str) -> None:
        """Export team assignment result to JSON file."""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_students(students: List[Student], file_path: str) -> None:
        """Export student list to JSON file."""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        student_data = {
            "students": [
                {
                    "name": student.name,
                    "email": student.email
                }
                for student in students
            ],
            "total_count": len(students)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, indent=2, ensure_ascii=False)


class ImageExportService:
    """Handles image export functionality."""
    
    def __init__(self, font_size: int = 12):
        self.font_size = font_size
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
    
    def export_teams_as_image(self, result: TeamAssignmentResult, file_path: str) -> None:
        """Export team assignment result as an image using matplotlib."""
        # Calculate figure size based on number of teams and max team size
        max_team_size = max(team.size for team in result.teams)
        teams_per_row = min(3, result.num_teams)
        rows = (result.num_teams + teams_per_row - 1) // teams_per_row
        
        # Dynamic figure sizing
        fig_width = max(12, teams_per_row * 4)
        fig_height = max(8, 3 + rows * (2 + max_team_size * 0.3))
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, teams_per_row * 4)
        ax.set_ylim(0, fig_height)
        ax.axis('off')
        
        # Title
        title = f"Team Assignment Results - {result.method.value.replace('_', ' ').title()}"
        ax.text(teams_per_row * 2, fig_height - 0.5, title, fontsize=16, fontweight='bold', ha='center')
        
        # Metadata
        metadata_text = (f"Total Students: {result.total_students} | "
                        f"Teams: {result.num_teams} | "
                        f"Base Size: {result.base_team_size}")
        ax.text(teams_per_row * 2, fig_height - 1, metadata_text, fontsize=10, ha='center')
        
        # Calculate layout
        y_start = fig_height - 2
        team_height = (fig_height - 3) / rows
        
        for i, team in enumerate(result.teams):
            row = i // teams_per_row
            col = i % teams_per_row
            
            x = 0.5 + (col * 4)
            y = y_start - (row * team_height)
            
            # Team box - dynamic height based on team size
            box_height = min(team_height - 0.2, 0.5 + team.size * 0.25)
            color = self.colors[i % len(self.colors)]
            rect = patches.Rectangle((x-0.4, y - box_height), 3.8, box_height, 
                                   linewidth=2, edgecolor='black', 
                                   facecolor=color, alpha=0.3)
            ax.add_patch(rect)
            
            # Team title
            ax.text(x + 1.5, y - 0.2, f"Team {team.team_number}", 
                   fontsize=12, fontweight='bold', ha='center')
            
            # Team members count
            member_text = f"({team.size} members)"
            ax.text(x + 1.5, y - 0.4, member_text, fontsize=10, ha='center')
            
            # All member names - no truncation
            for j, member in enumerate(team.members):
                # Use first name and last initial for space efficiency
                name_parts = member.name.split()
                if len(name_parts) > 1:
                    display_name = f"{name_parts[0]} {name_parts[-1][0]}."
                else:
                    display_name = name_parts[0]
                
                ax.text(x + 1.5, y - 0.6 - j * 0.2, display_name, 
                       fontsize=8, ha='center')
        
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def export_students_as_image(self, students: List[Student], file_path: str) -> None:
        """Export student list as an image."""
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Title
        ax.text(5, 11.5, f"Student List ({len(students)} students)", 
               fontsize=16, fontweight='bold', ha='center')
        
        # Students in columns
        students_per_col = 15
        cols = (len(students) + students_per_col - 1) // students_per_col
        
        for i, student in enumerate(students):
            col = i // students_per_col
            row = i % students_per_col
            
            x = 1 + (col * 4)
            y = 10.5 - (row * 0.6)
            
            ax.text(x, y, f"{i+1:2d}. {student.name}", fontsize=10, ha='left')
        
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()


class OutputFormatter:
    """Handles text output formatting."""
    
    @staticmethod
    def format_result(result: TeamAssignmentResult, use_names: bool = True) -> str:
        """Format team assignment result for display."""
        lines = []
        lines.append("=" * 60)
        lines.append("TEAM ASSIGNMENT RESULTS")
        lines.append("=" * 60)
        
        if result.method == AssignmentMethod.BY_SIZE:
            lines.append(f"Target team size: {result.requested_value}")
            lines.append(f"Complete teams: {result.complete_teams}")
            if result.remaining_students > 0:
                lines.append(f"Remaining students: {result.remaining_students}")
        else:
            lines.append(f"Number of teams: {result.num_teams}")
            lines.append(f"Base team size: {result.base_team_size}")
            if result.teams_with_extra > 0:
                lines.append(f"Teams with extra member: {result.teams_with_extra}")
        
        lines.append(f"Total students: {result.total_students}")
        lines.append("-" * 60)
        
        for team in result.teams:
            lines.append(f"\n{team}:")
            for i, student in enumerate(team.members, 1):
                if use_names:
                    lines.append(f"  {i}. {student}")
                else:
                    lines.append(f"  {i}. {student.email}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_students(students: List[Student]) -> str:
        """Format student list for display."""
        lines = []
        lines.append(f"Student List ({len(students)} students)")
        lines.append("-" * 40)
        
        for i, student in enumerate(students, 1):
            lines.append(f"{i:2d}. {student}")
        
        return "\n".join(lines) 