#!/usr/bin/env python3
"""
Data models for the Team Picker application.
Following Single Responsibility Principle (SRP).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class AssignmentMethod(Enum):
    """Enumeration for team assignment methods."""
    BY_SIZE = "by_size"
    BY_COUNT = "by_count"


@dataclass
class Student:
    """Represents a student with email and formatted name."""
    email: str
    name: str = field(init=False)
    
    def __post_init__(self):
        """Generate formatted name from email."""
        name_part = self.email.replace("@dlsu.edu.ph", "")
        self.name = name_part.replace("_", " ").title()
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email})"


@dataclass
class Team:
    """Represents a team with members and metadata."""
    members: List[Student]
    team_number: int = 0
    
    @property
    def size(self) -> int:
        """Get the number of members in the team."""
        return len(self.members)
    
    def add_member(self, student: Student) -> None:
        """Add a student to the team."""
        self.members.append(student)
    
    def __str__(self) -> str:
        return f"Team {self.team_number} ({self.size} members)"


@dataclass
class TeamAssignmentResult:
    """Result of team assignment with metadata."""
    teams: List[Team]
    method: AssignmentMethod
    total_students: int
    requested_value: int  # Either team_size or num_teams
    
    # Computed properties
    num_teams: int = field(init=False)
    complete_teams: int = field(init=False)
    remaining_students: int = field(init=False)
    base_team_size: int = field(init=False)
    teams_with_extra: int = field(init=False)
    
    def __post_init__(self):
        """Calculate metadata after initialization."""
        self.num_teams = len(self.teams)
        
        if self.method == AssignmentMethod.BY_SIZE:
            self.complete_teams = self.total_students // self.requested_value
            self.remaining_students = self.total_students % self.requested_value
            self.base_team_size = self.requested_value
            self.teams_with_extra = 1 if self.remaining_students > 0 else 0
        else:  # BY_COUNT
            self.base_team_size = self.total_students // self.requested_value
            self.teams_with_extra = self.total_students % self.requested_value
            self.complete_teams = self.requested_value - self.teams_with_extra
            self.remaining_students = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "teams": [
                {
                    "team_number": team.team_number,
                    "members": [
                        {
                            "name": student.name,
                            "email": student.email
                        }
                        for student in team.members
                    ],
                    "size": team.size
                }
                for team in self.teams
            ],
            "metadata": {
                "method": self.method.value,
                "total_students": self.total_students,
                "num_teams": self.num_teams,
                "requested_value": self.requested_value,
                "base_team_size": self.base_team_size,
                "complete_teams": self.complete_teams,
                "remaining_students": self.remaining_students,
                "teams_with_extra": self.teams_with_extra
            }
        } 