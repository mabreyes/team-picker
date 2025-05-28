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
from matplotlib.patches import FancyBboxPatch
import numpy as np
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
            raise FileNotFoundError(
                f"Student file not found: {self.file_path}\n\n"
                f"Please create a '{self.file_path}' file with one email per line.\n"
                f"Example format:\n"
                f"  john.doe@university.edu\n"
                f"  jane.smith@university.edu\n"
                f"  alex.johnson@university.edu\n"
            )
        
        students = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                email = line.strip()
                if email and '@' in email:
                    students.append(Student(email=email))
                elif email:  # Non-empty line without @
                    print(f"Warning: Line {line_num} doesn't look like an email: {email}")
        
        if not students:
            raise ValueError(
                f"No valid email addresses found in {self.file_path}\n"
                f"Please ensure the file contains email addresses, one per line."
            )
        
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
    """Handles professional image export functionality."""
    
    def __init__(self, font_size: int = 12):
        self.font_size = font_size
        # Professional color palette
        self.colors = [
            '#3498DB',  # Beautiful Blue
            '#E74C3C',  # Vibrant Red
            '#2ECC71',  # Emerald Green
            '#F39C12',  # Orange
            '#9B59B6',  # Purple
            '#1ABC9C',  # Turquoise
            '#E67E22',  # Carrot
            '#34495E',  # Dark Blue-Gray
            '#F1C40F',  # Golden Yellow
            '#E91E63',  # Pink
            '#8E44AD',  # Violet
            '#27AE60',  # Nephritis Green
        ]
        
        # Set professional style with macOS system fonts
        plt.style.use('default')
        
        # Use macOS native fonts with fallbacks
        font_family = [
            'Helvetica Neue',  # Classic macOS font
            'Helvetica',       # macOS fallback
            'Arial',           # Cross-platform fallback
            'DejaVu Sans',     # Linux fallback
            'sans-serif'       # Final fallback
        ]
        
        plt.rcParams.update({
            'font.family': font_family,
            'font.size': 10,
            'font.weight': 'normal',
            'axes.linewidth': 0,
            'figure.facecolor': '#FAFAFA',
            'axes.facecolor': '#FFFFFF'
        })
    
    def export_teams_as_image(self, result: TeamAssignmentResult, file_path: str) -> None:
        """Export team assignment result as a professional image."""
        # Calculate optimal layout
        max_team_size = max(team.size for team in result.teams)
        
        # Determine grid layout for teams
        if result.num_teams <= 3:
            cols = result.num_teams
            rows = 1
        elif result.num_teams <= 6:
            cols = 3
            rows = 2
        elif result.num_teams <= 9:
            cols = 3
            rows = 3
        else:
            cols = 4
            rows = (result.num_teams + 3) // 4
        
        # Calculate figure size based on content
        fig_width = max(16, cols * 5)
        fig_height = max(10, 4 + rows * (3 + max_team_size * 0.4))
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, cols * 5)
        ax.set_ylim(0, fig_height)
        ax.axis('off')
        
        # Beautiful gradient background
        gradient = np.linspace(0, 1, 256).reshape(256, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, extent=[0, cols * 5, 0, fig_height], 
                 aspect='auto', cmap='Blues', alpha=0.1)
        
        # Professional header with shadow effect
        header_y = fig_height - 1.5
        
        # Title shadow
        title = f"Team Assignment Results"
        ax.text(cols * 2.5 + 0.02, header_y - 0.02, title, 
               fontsize=24, fontweight='bold', ha='center', va='center',
               color='gray', alpha=0.5)
        
        # Main title
        ax.text(cols * 2.5, header_y, title, 
               fontsize=24, fontweight='bold', ha='center', va='center',
               color='#2C3E50')
        
        # Subtitle with method info
        method_text = f"{result.method.value.replace('_', ' ').title()}"
        ax.text(cols * 2.5, header_y - 0.6, method_text, 
               fontsize=16, ha='center', va='center',
               color='#34495E', style='italic')
        
        # Professional metadata panel
        metadata_y = header_y - 1.2
        metadata_text = (f"Students: {result.total_students}  •  "
                        f"Teams: {result.num_teams}  •  "
                        f"Base Size: {result.base_team_size}")
        
        # Metadata background
        metadata_bg = FancyBboxPatch((0.5, metadata_y - 0.25), cols * 5 - 1, 0.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor='white', edgecolor='#BDC3C7',
                                   linewidth=1, alpha=0.9)
        ax.add_patch(metadata_bg)
        
        ax.text(cols * 2.5, metadata_y, metadata_text, 
               fontsize=14, ha='center', va='center',
               color='#2C3E50', weight='medium')
        
        # Calculate team positioning
        start_y = fig_height - 3.5
        team_spacing_x = 5
        team_spacing_y = 3 + max_team_size * 0.4
        
        for i, team in enumerate(result.teams):
            row = i // cols
            col = i % cols
            
            # Center teams in the last row if incomplete
            if row == rows - 1:
                teams_in_last_row = result.num_teams - (rows - 1) * cols
                offset = (cols - teams_in_last_row) * team_spacing_x / 2
                x = offset + col * team_spacing_x + 2.5
            else:
                x = col * team_spacing_x + 2.5
            
            y = start_y - row * team_spacing_y
            
            # Team card dimensions
            card_width = 4
            card_height = min(2.5 + team.size * 0.35, team_spacing_y - 0.5)
            
            # Professional team card with shadow
            shadow = FancyBboxPatch((x - card_width/2 + 0.05, y - card_height + 0.05), 
                                  card_width, card_height,
                                  boxstyle="round,pad=0.15",
                                  facecolor='gray', alpha=0.2)
            ax.add_patch(shadow)
            
            # Main team card
            color = self.colors[i % len(self.colors)]
            team_card = FancyBboxPatch((x - card_width/2, y - card_height), 
                                     card_width, card_height,
                                     boxstyle="round,pad=0.15",
                                     facecolor=color, alpha=0.2,
                                     edgecolor=color, linewidth=2)
            ax.add_patch(team_card)
            
            # Team header background
            header_height = 0.6
            team_header = FancyBboxPatch((x - card_width/2, y - header_height), 
                                       card_width, header_height,
                                       boxstyle="round,pad=0.15",
                                       facecolor=color, alpha=0.8)
            ax.add_patch(team_header)
            
            # Team number and title
            ax.text(x, y - 0.3, f"Team {team.team_number}", 
                   fontsize=16, fontweight='bold', ha='center', va='center',
                   color='white')
            
            # Member count badge
            ax.text(x, y - 0.9, f"{team.size} members", 
                   fontsize=12, ha='center', va='center',
                   color=color, weight='medium',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                           edgecolor=color, alpha=0.9))
            
            # All team members with full names
            for j, member in enumerate(team.members):
                member_y = y - 1.4 - j * 0.28
                
                # Alternate background for readability
                if j % 2 == 0:
                    member_bg = FancyBboxPatch((x - card_width/2 + 0.1, member_y - 0.12), 
                                             card_width - 0.2, 0.24,
                                             boxstyle="round,pad=0.05",
                                             facecolor='white', alpha=0.6)
                    ax.add_patch(member_bg)
                
                # Full name without truncation
                ax.text(x, member_y, f"• {member.name}", 
                       fontsize=10, ha='center', va='center',
                       color='#2C3E50', weight='medium')
        
        # Professional footer
        footer_y = 0.5
        footer_text = "Generated by Team Picker • github.com/mabreyes/team-picker"
        ax.text(cols * 2.5, footer_y, footer_text, 
               fontsize=10, ha='center', va='center',
               color='#7F8C8D', style='italic')
        
        # Save with high quality
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight', 
                   facecolor='#FAFAFA', edgecolor='none',
                   pad_inches=0.2)
        plt.close()
    
    def export_students_as_image(self, students: List[Student], file_path: str) -> None:
        """Export student list as a professional image."""
        # Calculate layout
        students_per_col = 20
        cols = (len(students) + students_per_col - 1) // students_per_col
        
        fig_width = max(12, cols * 6)
        fig_height = max(14, students_per_col * 0.6 + 4)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, cols * 6)
        ax.set_ylim(0, fig_height)
        ax.axis('off')
        
        # Gradient background
        gradient = np.linspace(0, 1, 256).reshape(256, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, extent=[0, cols * 6, 0, fig_height], 
                 aspect='auto', cmap='Greens', alpha=0.1)
        
        # Professional header
        header_y = fig_height - 2
        ax.text(cols * 3, header_y, f"Student Directory", 
               fontsize=26, fontweight='bold', ha='center',
               color='#2C3E50')
        
        ax.text(cols * 3, header_y - 0.7, f"{len(students)} DLSU Students", 
               fontsize=16, ha='center',
               color='#34495E', style='italic')
        
        # Students in professional columns
        start_y = fig_height - 3.5
        
        for i, student in enumerate(students):
            col = i // students_per_col
            row = i % students_per_col
            
            x = col * 6 + 3
            y = start_y - row * 0.55
            
            # Alternating row backgrounds
            if row % 2 == 0:
                row_bg = FancyBboxPatch((col * 6 + 0.2, y - 0.2), 5.6, 0.4,
                                      boxstyle="round,pad=0.05",
                                      facecolor='white', alpha=0.6)
                ax.add_patch(row_bg)
            
            # Student number and name
            ax.text(x, y, f"{i+1:2d}. {student.name}", 
                   fontsize=11, ha='center', va='center',
                   color='#2C3E50', weight='medium')
        
        # Footer
        footer_y = 0.5
        ax.text(cols * 3, footer_y, "DLSU Student Directory • github.com/mabreyes/team-picker", 
               fontsize=12, ha='center',
               color='#7F8C8D', style='italic')
        
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight',
                   facecolor='#FAFAFA', edgecolor='none',
                   pad_inches=0.2)
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