"""Tests for the services module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from models import AssignmentMethod, Student, Team, TeamAssignmentResult
from services import (
    ImageExportService,
    JsonExportService,
    OutputFormatter,
    StudentRepository,
    TeamAssignmentService,
)


class TestStudentRepository:
    """Test cases for the StudentRepository service."""

    def test_init(self):
        """Test StudentRepository initialization."""
        repo = StudentRepository("test_file.txt")
        assert repo.file_path == Path("test_file.txt")

    def test_load_students_success(self):
        """Test loading students from a valid file."""
        test_content = "john.doe@test.com\njane.smith@test.com\n"

        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch.object(Path, "exists", return_value=True):
                repo = StudentRepository("test_file.txt")
                students = repo.load_students()

        assert len(students) == 2
        assert students[0].email == "john.doe@test.com"
        assert students[0].name == "John Doe"
        assert students[1].email == "jane.smith@test.com"
        assert students[1].name == "Jane Smith"

    def test_load_students_file_not_found(self):
        """Test loading students when file doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            repo = StudentRepository("nonexistent.txt")
            with pytest.raises(FileNotFoundError, match="Student file not found"):
                repo.load_students()

    def test_load_students_empty_file(self):
        """Test loading students from empty file."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch.object(Path, "exists", return_value=True):
                repo = StudentRepository("empty.txt")
                with pytest.raises(ValueError, match="No valid students found"):
                    repo.load_students()

    def test_load_students_invalid_emails(self):
        """Test loading students with invalid email formats."""
        test_content = "invalid-email\n\nvalid@test.com\nanother-invalid\n"

        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch.object(Path, "exists", return_value=True):
                repo = StudentRepository("test_file.txt")
                students = repo.load_students()

        # Should only load the valid email
        assert len(students) == 1
        assert students[0].email == "valid@test.com"

        # Note: The implementation silently skips invalid emails without warnings

    def test_load_students_mixed_content(self):
        """Test loading students with mixed valid/invalid content."""
        test_content = """
        # This is a comment
        user1@test.com

        user2@example.org
        not-an-email
        user3@domain.edu
        """

        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch.object(Path, "exists", return_value=True):
                repo = StudentRepository("test_file.txt")
                students = repo.load_students()

        assert len(students) == 3
        emails = [s.email for s in students]
        assert "user1@test.com" in emails
        assert "user2@example.org" in emails
        assert "user3@domain.edu" in emails


class TestTeamAssignmentService:
    """Test cases for the TeamAssignmentService."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.service = TeamAssignmentService()
        self.students = [Student(email=f"student{i}@test.com") for i in range(10)]

    def test_init(self):
        """Test TeamAssignmentService initialization."""
        service = TeamAssignmentService()
        assert service is not None

    def test_assign_by_team_count_valid(self):
        """Test assigning students by team count."""
        result = self.service.assign_by_team_count(self.students, 3)

        assert result.method == AssignmentMethod.BY_COUNT
        assert result.total_students == 10
        assert result.num_teams == 3
        assert len(result.teams) == 3

        # Check that all students are assigned
        total_assigned = sum(team.size for team in result.teams)
        assert total_assigned == 10

        # Check team numbers
        team_numbers = [team.team_number for team in result.teams]
        assert team_numbers == [1, 2, 3]

    def test_assign_by_team_count_equal_distribution(self):
        """Test equal distribution when possible."""
        students = [Student(email=f"student{i}@test.com") for i in range(6)]
        result = self.service.assign_by_team_count(students, 3)

        # Should create 3 teams of 2 students each
        team_sizes = [team.size for team in result.teams]
        assert team_sizes == [2, 2, 2]

    def test_assign_by_team_count_unequal_distribution(self):
        """Test unequal distribution when necessary."""
        result = self.service.assign_by_team_count(self.students, 3)

        # 10 students / 3 teams = 3 base + 1 remainder
        # So teams should be [4, 3, 3] or similar distribution
        team_sizes = sorted([team.size for team in result.teams], reverse=True)
        assert team_sizes[0] == 4  # One team gets extra student
        assert team_sizes[1] == 3
        assert team_sizes[2] == 3

    def test_assign_by_team_count_invalid_num_teams(self):
        """Test error handling for invalid team count."""
        with pytest.raises(ValueError, match="Number of teams must be positive"):
            self.service.assign_by_team_count(self.students, 0)

        with pytest.raises(ValueError, match="Number of teams must be positive"):
            self.service.assign_by_team_count(self.students, -1)

    def test_assign_by_team_count_too_many_teams(self):
        """Test error handling when requesting more teams than students."""
        with pytest.raises(
            ValueError, match="Cannot create .* teams with only .* students"
        ):
            self.service.assign_by_team_count(self.students, 15)

    def test_assign_by_team_size_valid(self):
        """Test assigning students by team size."""
        result = self.service.assign_by_team_size(self.students, 3)

        assert result.method == AssignmentMethod.BY_SIZE
        assert result.total_students == 10
        assert result.base_team_size == 3

        # 10 students / 3 per team = 3 complete teams + 1 remainder
        # Remainder should be distributed to existing teams
        assert len(result.teams) == 3

        # Check that all students are assigned
        total_assigned = sum(team.size for team in result.teams)
        assert total_assigned == 10

    def test_assign_by_team_size_perfect_division(self):
        """Test team size assignment with perfect division."""
        students = [Student(email=f"student{i}@test.com") for i in range(9)]
        result = self.service.assign_by_team_size(students, 3)

        # Should create exactly 3 teams of 3 students each
        assert len(result.teams) == 3
        team_sizes = [team.size for team in result.teams]
        assert team_sizes == [3, 3, 3]

    def test_assign_by_team_size_with_remainder(self):
        """Test team size assignment with remainder students."""
        result = self.service.assign_by_team_size(self.students, 4)

        # 10 students / 4 per team = 2 complete teams + 2 remainder
        # Remainder distributed: team 1 gets +1, team 2 gets +1
        assert len(result.teams) == 2
        team_sizes = sorted([team.size for team in result.teams])
        assert team_sizes == [5, 5]  # Each team gets 4 + 1 remainder

    def test_assign_by_team_size_invalid_size(self):
        """Test error handling for invalid team size."""
        with pytest.raises(ValueError, match="Team size must be positive"):
            self.service.assign_by_team_size(self.students, 0)

        with pytest.raises(ValueError, match="Team size must be positive"):
            self.service.assign_by_team_size(self.students, -1)

    def test_assign_by_team_size_too_large(self):
        """Test error handling when team size is larger than student count."""
        with pytest.raises(
            ValueError, match="Team size .* is larger than total students"
        ):
            self.service.assign_by_team_size(self.students, 15)

    @patch("random.shuffle")
    def test_randomization(self, mock_shuffle):
        """Test that students are shuffled for random assignment."""
        self.service.assign_by_team_count(self.students, 2)
        mock_shuffle.assert_called_once()

        mock_shuffle.reset_mock()
        self.service.assign_by_team_size(self.students, 3)
        mock_shuffle.assert_called_once()


class TestJsonExportService:
    """Test cases for the JsonExportService."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.service = JsonExportService()
        self.students = [Student(email=f"student{i}@test.com") for i in range(4)]
        self.teams = [
            Team(team_number=1, members=self.students[:2]),
            Team(team_number=2, members=self.students[2:]),
        ]
        self.result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=4,
            num_teams=2,
            base_team_size=2,
        )

    def test_init(self):
        """Test JsonExportService initialization."""
        service = JsonExportService()
        assert service is not None

    def test_export_result(self):
        """Test exporting team assignment result to JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            json_file = self.service.export_result(
                self.result, "test_teams", output_dir
            )

            assert json_file.exists()
            assert json_file.name == "test_teams.json"

            # Verify JSON content
            with open(json_file, "r") as f:
                data = json.load(f)

            assert "metadata" in data
            assert "teams" in data

            metadata = data["metadata"]
            assert metadata["method"] == "by_count"
            assert metadata["total_students"] == 4
            assert metadata["num_teams"] == 2
            assert metadata["base_team_size"] == 2

            teams_data = data["teams"]
            assert len(teams_data) == 2
            assert teams_data[0]["team_number"] == 1
            assert len(teams_data[0]["members"]) == 2

    def test_export_student_list(self):
        """Test exporting student list to JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            json_file = self.service.export_student_list(
                self.students, "students", output_dir
            )

            assert json_file.exists()
            assert json_file.name == "students.json"

            # Verify JSON content
            with open(json_file, "r") as f:
                data = json.load(f)

            assert "metadata" in data
            assert "students" in data

            metadata = data["metadata"]
            assert metadata["total_students"] == 4
            assert metadata["export_type"] == "student_list"

            students_data = data["students"]
            assert len(students_data) == 4
            assert students_data[0]["email"] == "student0@test.com"

    def test_export_creates_directory(self):
        """Test that export creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "new_dir" / "nested"
            json_file = self.service.export_result(self.result, "test", output_dir)

            assert output_dir.exists()
            assert json_file.exists()


class TestImageExportService:
    """Test cases for the ImageExportService."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.service = ImageExportService()
        self.students = [Student(email=f"student{i}@test.com") for i in range(6)]
        self.teams = [
            Team(team_number=1, members=self.students[:3]),
            Team(team_number=2, members=self.students[3:]),
        ]
        self.result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=6,
            num_teams=2,
            base_team_size=3,
        )

    def test_init(self):
        """Test ImageExportService initialization."""
        service = ImageExportService()
        assert service is not None

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.subplots")
    def test_export_result(self, mock_subplots, mock_close, mock_savefig):
        """Test exporting team assignment result as image."""
        # Mock matplotlib objects
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            image_file = self.service.export_result(
                self.result, "test_teams", output_dir
            )

            assert image_file == output_dir / "test_teams.png"
            mock_subplots.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.subplots")
    def test_export_student_list(self, mock_subplots, mock_close, mock_savefig):
        """Test exporting student list as image."""
        # Mock matplotlib objects
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            image_file = self.service.export_student_list(
                self.students, "students", output_dir
            )

            assert image_file == output_dir / "students.png"
            mock_subplots.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.subplots")
    def test_export_creates_directory(self, mock_subplots, mock_close, mock_savefig):
        """Test that export creates output directory if it doesn't exist."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "new_dir"
            self.service.export_result(self.result, "test", output_dir)

            assert output_dir.exists()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.subplots")
    def test_export_large_team_count(self, mock_subplots, mock_close, mock_savefig):
        """Test exporting with many teams."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # Create many small teams
        students = [Student(email=f"student{i}@test.com") for i in range(20)]
        teams = [Team(team_number=i + 1, members=[students[i]]) for i in range(20)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=20,
            num_teams=20,
            base_team_size=1,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            self.service.export_result(result, "many_teams", output_dir)

            mock_subplots.assert_called_once()


class TestOutputFormatter:
    """Test cases for the OutputFormatter service."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.students = [Student(email=f"student{i}@test.com") for i in range(4)]
        self.teams = [
            Team(team_number=1, members=self.students[:2]),
            Team(team_number=2, members=self.students[2:]),
        ]
        self.result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=4,
            num_teams=2,
            base_team_size=2,
        )

    def test_format_result(self):
        """Test formatting team assignment result."""
        formatted = OutputFormatter.format_result(self.result)

        assert "TEAM ASSIGNMENT RESULTS" in formatted
        assert "Method: By Count" in formatted
        assert "Total Students: 4" in formatted
        assert "Number of Teams: 2" in formatted
        assert "Base Team Size: 2" in formatted
        assert "Team 1 (2 members):" in formatted
        assert "Team 2 (2 members):" in formatted
        assert "Student0" in formatted
        assert "Student1" in formatted

    def test_format_result_by_size_method(self):
        """Test formatting result with BY_SIZE method."""
        result = TeamAssignmentResult(
            teams=self.teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=4,
            num_teams=2,
            base_team_size=2,
        )

        formatted = OutputFormatter.format_result(result)
        assert "Method: By Size" in formatted

    def test_format_result_with_timestamp(self):
        """Test that formatted result includes timestamp."""
        formatted = OutputFormatter.format_result(self.result)
        assert "Timestamp:" in formatted

    def test_format_result_empty_teams(self):
        """Test formatting result with empty teams."""
        empty_result = TeamAssignmentResult(
            teams=[],
            method=AssignmentMethod.BY_COUNT,
            total_students=0,
            num_teams=0,
            base_team_size=0,
        )

        formatted = OutputFormatter.format_result(empty_result)
        assert "TEAM ASSIGNMENT RESULTS" in formatted
        assert "Total Students: 0" in formatted

    def test_format_result_single_team(self):
        """Test formatting result with single team."""
        single_team_result = TeamAssignmentResult(
            teams=[Team(team_number=1, members=self.students)],
            method=AssignmentMethod.BY_SIZE,
            total_students=4,
            num_teams=1,
            base_team_size=4,
        )

        formatted = OutputFormatter.format_result(single_team_result)
        assert "Team 1 (4 members):" in formatted
        assert formatted.count("Team") == 3


class TestServiceIntegration:
    """Integration tests for services working together."""

    def test_full_workflow(self):
        """Test complete workflow using all services."""
        # Create test file content
        test_content = (
            "user1@test.com\nuser2@test.com\nuser3@test.com\nuser4@test.com\n"
        )

        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch.object(Path, "exists", return_value=True):
                # Load students
                repo = StudentRepository("test.txt")
                students = repo.load_students()

                # Assign teams
                assignment_service = TeamAssignmentService()
                result = assignment_service.assign_by_team_count(students, 2)

                # Format output
                formatted = OutputFormatter.format_result(result)

                # Verify complete workflow
                assert len(students) == 4
                assert len(result.teams) == 2
                assert "TEAM ASSIGNMENT RESULTS" in formatted
                assert result.total_students == 4

    def test_export_workflow(self):
        """Test export workflow with both JSON and image services."""
        students = [Student(email=f"user{i}@test.com") for i in range(3)]
        teams = [Team(team_number=1, members=students)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_SIZE,
            total_students=3,
            num_teams=1,
            base_team_size=3,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Export JSON
            json_service = JsonExportService()
            json_file = json_service.export_result(result, "test", output_dir)

            # Export image (mocked)
            with patch("matplotlib.pyplot.savefig"), patch(
                "matplotlib.pyplot.close"
            ), patch("matplotlib.pyplot.subplots") as mock_subplots:
                mock_fig = Mock()
                mock_ax = Mock()
                mock_subplots.return_value = (mock_fig, mock_ax)

                image_service = ImageExportService()
                image_file = image_service.export_result(result, "test", output_dir)

                # Verify both exports
                assert json_file.exists()
                assert image_file == output_dir / "test.png"
