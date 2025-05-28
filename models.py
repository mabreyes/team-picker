#!/usr/bin/env python3
"""Team Picker Data Models.

Data classes and enums for representing students, teams,
and team assignment results using dataclasses for clean structure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class AssignmentMethod(Enum):
    """Enumeration of team assignment methods."""

    BY_SIZE = "by_size"
    BY_COUNT = "by_count"


@dataclass
class Student:
    """Represents a student with email and derived name."""

    email: str
    name: str = field(init=False)

    def __post_init__(self):
        """Initialize name from email after object creation."""
        if not self.email or "@" not in self.email:
            raise ValueError(f"Invalid email format: {self.email}")

        # Extract name from email (part before @)
        username = self.email.split("@")[0]
        # Convert to readable name (replace dots/underscores with spaces, title case)
        self.name = username.replace(".", " ").replace("_", " ").title()

    def __str__(self) -> str:
        """Return string representation of the student."""
        return f"{self.name} ({self.email})"


@dataclass
class Team:
    """Represents a team with members and team number."""

    team_number: int
    members: List[Student]

    @property
    def size(self) -> int:
        """Get the number of members in the team."""
        return len(self.members)

    def __str__(self) -> str:
        """Return string representation of the team."""
        return f"Team {self.team_number}"


@dataclass
class TeamAssignmentResult:
    """Represents the result of a team assignment operation."""

    teams: List[Team]
    method: AssignmentMethod
    total_students: int
    num_teams: int
    base_team_size: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def teams_with_extra(self) -> int:
        """Get the number of teams with extra members."""
        return sum(1 for team in self.teams if team.size > self.base_team_size)

    @property
    def complete_teams(self) -> int:
        """Get the number of complete teams (with base size)."""
        return sum(1 for team in self.teams if team.size == self.base_team_size)

    @property
    def remaining_students(self) -> int:
        """Get the number of students in incomplete teams."""
        return sum(
            team.size - self.base_team_size
            for team in self.teams
            if team.size > self.base_team_size
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "teams": [
                {
                    "team_number": team.team_number,
                    "members": [
                        {"name": student.name, "email": student.email}
                        for student in team.members
                    ],
                    "size": team.size,
                }
                for team in self.teams
            ],
            "metadata": {
                "method": self.method.value,
                "total_students": self.total_students,
                "num_teams": self.num_teams,
                "base_team_size": self.base_team_size,
                "complete_teams": self.complete_teams,
                "remaining_students": self.remaining_students,
                "teams_with_extra": self.teams_with_extra,
                "timestamp": self.timestamp.isoformat(),
            },
        }
