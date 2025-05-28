"""
Tests for the models module.
"""

from datetime import datetime

import pytest

from models import AssignmentMethod, Student, Team, TeamAssignmentResult


class TestStudent:
    """Test cases for the Student model."""

    def test_student_creation_with_email(self):
        """Test creating a student with an email address."""
        email = "john.doe@dlsu.edu.ph"
        student = Student(email=email)

        assert student.email == email
        assert student.name == "John Doe"

    def test_student_name_extraction(self):
        """Test name extraction from various email formats."""
        test_cases = [
            ("john.doe@dlsu.edu.ph", "John Doe"),
            ("maria.garcia@university.edu", "Maria Garcia"),
            ("alex.johnson123@school.org", "Alex Johnson123"),
            ("simple@test.com", "Simple"),
            ("test_user@example.com", "Test User"),
            ("first.middle.last@domain.org", "First Middle Last"),
            ("user_name_123@test.edu", "User Name 123"),
        ]

        for email, expected_name in test_cases:
            student = Student(email=email)
            assert student.name == expected_name

    def test_student_invalid_email(self):
        """Test creating student with invalid email raises ValueError."""
        invalid_emails = [
            "",
            "invalid-email",
            "no-at-symbol",
            "   ",
            None,
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Student(email=invalid_email)

    def test_student_string_representation(self):
        """Test student string representation."""
        student = Student(email="test@example.com")
        assert str(student) == "Test (test@example.com)"

    def test_student_post_init(self):
        """Test that __post_init__ is called correctly."""
        student = Student(email="complex.email_address@domain.co.uk")
        assert student.name == "Complex Email Address"


class TestTeam:
    """Test cases for the Team model."""

    def test_team_creation(self):
        """Test creating a team with members."""
        students = [
            Student(email="student1@test.com"),
            Student(email="student2@test.com"),
        ]
        team = Team(team_number=1, members=students)

        assert team.team_number == 1
        assert len(team.members) == 2
        assert team.size == 2

    def test_empty_team(self):
        """Test creating an empty team."""
        team = Team(team_number=1, members=[])

        assert team.team_number == 1
        assert len(team.members) == 0
        assert team.size == 0

    def test_team_size_property(self):
        """Test that team size property returns correct count."""
        students = [Student(email=f"student{i}@test.com") for i in range(5)]
        team = Team(team_number=1, members=students)

        assert team.size == 5

        # Test that size updates when members are modified
        team.members.append(Student(email="new@test.com"))
        assert team.size == 6

    def test_team_string_representation(self):
        """Test team string representation."""
        team = Team(team_number=5, members=[])
        assert str(team) == "Team 5"

    def test_team_with_large_number(self):
        """Test team with large team number."""
        team = Team(team_number=999, members=[])
        assert team.team_number == 999
        assert str(team) == "Team 999"


class TestAssignmentMethod:
    """Test cases for the AssignmentMethod enum."""

    def test_assignment_method_values(self):
        """Test that assignment method enum has correct values."""
        assert AssignmentMethod.BY_COUNT.value == "by_count"
        assert AssignmentMethod.BY_SIZE.value == "by_size"

    def test_assignment_method_from_string(self):
        """Test creating assignment method from string."""
        assert AssignmentMethod("by_count") == AssignmentMethod.BY_COUNT
        assert AssignmentMethod("by_size") == AssignmentMethod.BY_SIZE

    def test_assignment_method_enum_members(self):
        """Test that enum has exactly the expected members."""
        methods = list(AssignmentMethod)
        assert len(methods) == 2
        assert AssignmentMethod.BY_COUNT in methods
        assert AssignmentMethod.BY_SIZE in methods


class TestTeamAssignmentResult:
    """Test cases for the TeamAssignmentResult model."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.students = [Student(email=f"student{i}@test.com") for i in range(10)]
        self.teams = [
            Team(team_number=1, members=self.students[:3]),
            Team(team_number=2, members=self.students[3:6]),
            Team(team_number=3, members=self.students[6:8]),
            Team(team_number=4, members=self.students[8:]),
        ]

    def test_team_assignment_result_creation(self):
        """Test creating a TeamAssignmentResult."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=10,
            num_teams=4,
            base_team_size=2,
        )

        assert len(result.teams) == 4
        assert result.method == AssignmentMethod.BY_COUNT
        assert result.total_students == 10
        assert result.num_teams == 4
        assert result.base_team_size == 2
        assert isinstance(result.timestamp, datetime)

    def test_teams_with_extra_property(self):
        """Test teams_with_extra property calculation."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=10,
            num_teams=4,
            base_team_size=2,
        )

        # Teams 1 and 2 have 3 members (base_size=2, so +1 extra)
        # Teams 3 and 4 have 2 members (base_size=2, so no extra)
        assert result.teams_with_extra == 2

    def test_complete_teams_property(self):
        """Test complete_teams property calculation."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=10,
            num_teams=4,
            base_team_size=2,
        )

        # Teams 3 and 4 have exactly base_size (2) members
        assert result.complete_teams == 2

    def test_remaining_students_property(self):
        """Test remaining_students property calculation."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=10,
            num_teams=4,
            base_team_size=2,
        )

        # Teams 1 and 2 each have 1 extra student (3-2=1)
        assert result.remaining_students == 2

    def test_to_dict_method(self):
        """Test converting TeamAssignmentResult to dictionary."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=10,
            num_teams=4,
            base_team_size=3,
        )

        result_dict = result.to_dict()

        assert "teams" in result_dict
        assert "metadata" in result_dict

        metadata = result_dict["metadata"]
        assert metadata["method"] == "by_size"
        assert metadata["total_students"] == 10
        assert metadata["num_teams"] == 4
        assert metadata["base_team_size"] == 3
        assert metadata["complete_teams"] == result.complete_teams
        assert metadata["remaining_students"] == result.remaining_students
        assert metadata["teams_with_extra"] == result.teams_with_extra
        assert "timestamp" in metadata

        teams_data = result_dict["teams"]
        assert len(teams_data) == 4

        # Check first team structure
        team_data = teams_data[0]
        assert team_data["team_number"] == 1
        assert team_data["size"] == 3
        assert len(team_data["members"]) == 3

        # Check member structure
        member_data = team_data["members"][0]
        assert "name" in member_data
        assert "email" in member_data

    def test_default_timestamp(self):
        """Test that timestamp is automatically set."""
        before = datetime.now()
        result = TeamAssignmentResult(
            teams=[],
            method=AssignmentMethod.BY_COUNT,
            total_students=0,
            num_teams=0,
            base_team_size=0,
        )
        after = datetime.now()

        assert before <= result.timestamp <= after

    def test_custom_timestamp(self):
        """Test setting custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        result = TeamAssignmentResult(
            teams=[],
            method=AssignmentMethod.BY_COUNT,
            total_students=0,
            num_teams=0,
            base_team_size=0,
            timestamp=custom_time,
        )

        assert result.timestamp == custom_time

    def test_edge_case_all_teams_same_size(self):
        """Test edge case where all teams have the same size."""
        equal_teams = [
            Team(team_number=1, members=self.students[:2]),
            Team(team_number=2, members=self.students[2:4]),
            Team(team_number=3, members=self.students[4:6]),
        ]

        result = TeamAssignmentResult(
            teams=equal_teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=6,
            num_teams=3,
            base_team_size=2,
        )

        assert result.teams_with_extra == 0
        assert result.complete_teams == 3
        assert result.remaining_students == 0

    def test_edge_case_single_team(self):
        """Test edge case with single team."""
        single_team = [Team(team_number=1, members=self.students)]

        result = TeamAssignmentResult(
            teams=single_team,
            method=AssignmentMethod.BY_SIZE,
            total_students=10,
            num_teams=1,
            base_team_size=10,
        )

        assert result.teams_with_extra == 0
        assert result.complete_teams == 1
        assert result.remaining_students == 0


# Integration test example
class TestModelIntegration:
    """Integration tests for models working together."""

    def test_team_with_students(self):
        """Test creating a team with multiple students."""
        students = [
            Student(email="alice@test.com"),
            Student(email="bob@test.com"),
            Student(email="charlie@test.com"),
        ]

        team = Team(team_number=1, members=students)

        assert team.size == 3
        assert all(isinstance(member, Student) for member in team.members)
        assert team.members[0].name == "Alice"
        assert team.members[1].name == "Bob"
        assert team.members[2].name == "Charlie"

    def test_full_assignment_result_workflow(self):
        """Test complete workflow with all models."""
        # Create students
        students = [Student(email=f"user{i}@example.com") for i in range(7)]

        # Create teams
        teams = [
            Team(team_number=1, members=students[:3]),
            Team(team_number=2, members=students[3:6]),
            Team(team_number=3, members=students[6:]),
        ]

        # Create assignment result
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=7,
            num_teams=3,
            base_team_size=2,
        )

        # Verify the complete structure
        assert len(result.teams) == 3
        assert result.total_students == 7
        assert result.teams_with_extra == 2  # Teams 1 and 2 have 3 members
        assert result.complete_teams == 0  # No teams have exactly 2 members
        assert (
            result.remaining_students == 2
        )  # Team 1 has 1 extra (3-2), Team 2 has 1 extra (3-2), Team 3 has 0 extra

        # Test dictionary conversion
        result_dict = result.to_dict()
        assert len(result_dict["teams"]) == 3
        assert result_dict["metadata"]["total_students"] == 7
