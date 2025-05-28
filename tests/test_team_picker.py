"""Tests for the team_picker module (legacy interface)."""

import json
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import mock_open, patch

import pytest

from team_picker import StudentDict, TeamDict, TeamPicker


class TestStudentDict:
    """Test cases for StudentDict TypedDict."""

    def test_student_dict_structure(self):
        """Test StudentDict type structure."""
        student: StudentDict = {"name": "John Doe", "email": "john@test.com"}

        assert student["name"] == "John Doe"
        assert student["email"] == "john@test.com"


class TestTeamDict:
    """Test cases for TeamDict TypedDict."""

    def test_team_dict_structure(self):
        """Test TeamDict type structure."""
        students: List[StudentDict] = [
            {"name": "John Doe", "email": "john@test.com"},
            {"name": "Jane Smith", "email": "jane@test.com"},
        ]
        team: TeamDict = {"team_number": 1, "members": students}

        assert team["team_number"] == 1
        assert len(team["members"]) == 2
        assert team["members"][0]["name"] == "John Doe"


class TestTeamPicker:
    """Test cases for the TeamPicker class."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.test_content = (
            "john.doe@test.com\njane.smith@test.com\n"
            "alice.johnson@test.com\nbob.wilson@test.com\n"
        )

    def test_init_default_file(self):
        """Test TeamPicker initialization with default file."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

        assert picker.student_file == Path("student_list.txt")
        assert len(picker.students) == 4

    def test_init_custom_file(self):
        """Test TeamPicker initialization with custom file."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker("custom.txt")

        assert picker.student_file == Path("custom.txt")
        assert len(picker.students) == 4

    def test_load_students_success(self):
        """Test successful student loading."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

        assert len(picker.students) == 4
        assert picker.students[0]["name"] == "John Doe"
        assert picker.students[0]["email"] == "john.doe@test.com"
        assert picker.students[1]["name"] == "Jane Smith"
        assert picker.students[1]["email"] == "jane.smith@test.com"

    def test_load_students_file_not_found(self):
        """Test loading students when file doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Student file not found"):
                TeamPicker("nonexistent.txt")

    def test_load_students_empty_file(self):
        """Test loading students from empty file."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch.object(Path, "exists", return_value=True):
                with pytest.raises(ValueError, match="No valid students found"):
                    TeamPicker()

    def test_load_students_no_valid_emails(self):
        """Test loading students with no valid emails."""
        invalid_content = "not-an-email\nanother-invalid\n"
        with patch("builtins.open", mock_open(read_data=invalid_content)):
            with patch.object(Path, "exists", return_value=True):
                with pytest.raises(ValueError, match="No valid students found"):
                    TeamPicker()

    def test_load_students_mixed_content(self):
        """Test loading students with mixed valid/invalid content."""
        mixed_content = "valid@test.com\ninvalid-email\nanother@test.com\n\n"
        with patch("builtins.open", mock_open(read_data=mixed_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

        assert len(picker.students) == 2
        assert picker.students[0]["email"] == "valid@test.com"
        assert picker.students[1]["email"] == "another@test.com"

    def test_name_extraction_various_formats(self):
        """Test name extraction from various email formats."""
        test_emails = """
        first.last@test.com
        user_name@test.com
        simple@test.com
        complex.name.here@test.com
        """

        with patch("builtins.open", mock_open(read_data=test_emails)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

        names = [student["name"] for student in picker.students]
        assert "First Last" in names
        assert "User Name" in names
        assert "Simple" in names
        assert "Complex Name Here" in names

    def test_create_teams_by_size_valid(self):
        """Test creating teams by size with valid parameters."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        assert result["method"] == "by_size"
        assert result["total_students"] == 4
        assert result["base_team_size"] == 2
        assert len(result["teams"]) == 2

        # Check that all students are assigned
        total_assigned = sum(len(team["members"]) for team in result["teams"])
        assert total_assigned == 4

    def test_create_teams_by_size_with_remainder(self):
        """Test creating teams by size with remainder students."""
        # 5 students, team size 2 = 2 complete teams + 1 remainder
        content_5_students = self.test_content + "extra@test.com\n"

        with patch("builtins.open", mock_open(read_data=content_5_students)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        assert len(result["teams"]) == 2  # 2 complete teams
        team_sizes = [len(team["members"]) for team in result["teams"]]
        assert sorted(team_sizes) == [2, 3]  # One team gets the remainder

    def test_create_teams_by_size_perfect_division(self):
        """Test creating teams by size with perfect division."""
        # 6 students, team size 2 = 3 complete teams
        content_6_students = self.test_content + "extra1@test.com\nextra2@test.com\n"

        with patch("builtins.open", mock_open(read_data=content_6_students)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        assert len(result["teams"]) == 3
        team_sizes = [len(team["members"]) for team in result["teams"]]
        assert team_sizes == [2, 2, 2]

    def test_create_teams_by_size_invalid_size(self):
        """Test creating teams with invalid size."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with pytest.raises(ValueError, match="Team size must be positive"):
                    picker.create_teams_by_size(0)

                with pytest.raises(ValueError, match="Team size must be positive"):
                    picker.create_teams_by_size(-1)

    def test_create_teams_by_size_too_large(self):
        """Test creating teams with size larger than student count."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with pytest.raises(
                    ValueError, match="Team size .* is larger than total students"
                ):
                    picker.create_teams_by_size(10)

    def test_create_teams_by_size_no_shuffle(self):
        """Test creating teams by size without shuffling."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with patch("random.shuffle") as mock_shuffle:
                    result = picker.create_teams_by_size(2, shuffle=False)
                    mock_shuffle.assert_not_called()

                # First team should have first two students in order
                first_team = result["teams"][0]
                assert first_team["members"][0]["email"] == "john.doe@test.com"
                assert first_team["members"][1]["email"] == "jane.smith@test.com"

    def test_create_teams_by_count_valid(self):
        """Test creating teams by count with valid parameters."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(2)

        assert result["method"] == "by_count"
        assert result["total_students"] == 4
        assert result["num_teams"] == 2
        assert len(result["teams"]) == 2

        # Check that all students are assigned
        total_assigned = sum(len(team["members"]) for team in result["teams"])
        assert total_assigned == 4

    def test_create_teams_by_count_equal_distribution(self):
        """Test creating teams by count with equal distribution."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(2)

        # 4 students / 2 teams = 2 students per team
        team_sizes = [len(team["members"]) for team in result["teams"]]
        assert team_sizes == [2, 2]

    def test_create_teams_by_count_unequal_distribution(self):
        """Test creating teams by count with unequal distribution."""
        # 5 students, 2 teams = base size 2, one team gets extra
        content_5_students = self.test_content + "extra@test.com\n"

        with patch("builtins.open", mock_open(read_data=content_5_students)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(2)

        team_sizes = sorted([len(team["members"]) for team in result["teams"]])
        assert team_sizes == [2, 3]  # One team gets extra student

    def test_create_teams_by_count_invalid_count(self):
        """Test creating teams with invalid count."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with pytest.raises(
                    ValueError, match="Number of teams must be positive"
                ):
                    picker.create_teams_by_count(0)

                with pytest.raises(
                    ValueError, match="Number of teams must be positive"
                ):
                    picker.create_teams_by_count(-1)

    def test_create_teams_by_count_too_many_teams(self):
        """Test creating more teams than students."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with pytest.raises(
                    ValueError, match="Cannot create .* teams with only .* students"
                ):
                    picker.create_teams_by_count(10)

    def test_create_teams_by_count_no_shuffle(self):
        """Test creating teams by count without shuffling."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                with patch("random.shuffle") as mock_shuffle:
                    result = picker.create_teams_by_count(2, shuffle=False)
                    mock_shuffle.assert_not_called()

                # Teams should be assigned in order
                team1 = result["teams"][0]
                team2 = result["teams"][1]
                assert team1["members"][0]["email"] == "john.doe@test.com"
                assert team2["members"][0]["email"] == "alice.johnson@test.com"

    @patch("random.shuffle")
    def test_shuffling_behavior(self, mock_shuffle):
        """Test that shuffling is called when enabled."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                # Test with shuffle=True (default)
                picker.create_teams_by_size(2, shuffle=True)
                mock_shuffle.assert_called_once()

                mock_shuffle.reset_mock()
                picker.create_teams_by_count(2, shuffle=True)
                mock_shuffle.assert_called_once()

    def test_format_teams_output(self):
        """Test formatting teams output."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)
                formatted = picker.format_teams_output(result)

        assert "TEAM ASSIGNMENT RESULTS" in formatted
        assert "Method: By Size" in formatted
        assert "Total Students: 4" in formatted
        assert "Team 1" in formatted
        assert "Team 2" in formatted
        assert "John Doe" in formatted
        assert "Jane Smith" in formatted

    def test_format_teams_output_by_count(self):
        """Test formatting teams output for by_count method."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(2)
                formatted = picker.format_teams_output(result)

        assert "Method: By Count" in formatted

    def test_save_teams_to_json(self):
        """Test saving teams to JSON file."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "teams.json"
            picker.save_teams_to_json(result, str(json_file))

            assert json_file.exists()

            # Verify JSON content
            with open(json_file, "r") as f:
                data = json.load(f)

            assert data["method"] == "by_size"
            assert data["total_students"] == 4
            assert len(data["teams"]) == 2

    def test_save_teams_to_json_auto_extension(self):
        """Test saving teams to JSON with automatic .json extension."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file_base = Path(temp_dir) / "teams"
            picker.save_teams_to_json(result, str(json_file_base))

            json_file = Path(temp_dir) / "teams.json"
            assert json_file.exists()

    def test_save_teams_to_json_creates_directory(self):
        """Test that save_teams_to_json creates parent directories."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_size(2)

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "dir" / "teams.json"
            picker.save_teams_to_json(result, str(nested_path))

            assert nested_path.exists()

    def test_get_student_count(self):
        """Test getting student count."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                count = picker.get_student_count()

        assert count == 4

    def test_get_students(self):
        """Test getting students list."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                students = picker.get_students()

        assert len(students) == 4
        assert students[0]["name"] == "John Doe"
        assert students[0]["email"] == "john.doe@test.com"

        # Verify it returns a copy (not the original)
        students.append({"name": "Test", "email": "test@test.com"})
        assert len(picker.students) == 4  # Original unchanged

    def test_team_numbers_sequential(self):
        """Test that team numbers are sequential starting from 1."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(3)

        team_numbers = [team["team_number"] for team in result["teams"]]
        assert team_numbers == [1, 2, 3]

    def test_edge_case_single_student(self):
        """Test edge case with single student."""
        single_student = "lonely@test.com\n"

        with patch("builtins.open", mock_open(read_data=single_student)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(1)

        assert len(result["teams"]) == 1
        assert len(result["teams"][0]["members"]) == 1
        assert result["teams"][0]["members"][0]["email"] == "lonely@test.com"

    def test_edge_case_many_teams_one_student_each(self):
        """Test edge case with many teams, one student each."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()
                result = picker.create_teams_by_count(4)  # 4 teams for 4 students

        assert len(result["teams"]) == 4
        for team in result["teams"]:
            assert len(team["members"]) == 1

    def test_integration_full_workflow(self):
        """Test complete workflow integration."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                # Initialize picker
                picker = TeamPicker("test.txt")

                # Verify students loaded
                assert picker.get_student_count() == 4

                # Create teams by size
                result_by_size = picker.create_teams_by_size(2)
                assert len(result_by_size["teams"]) == 2

                # Create teams by count
                result_by_count = picker.create_teams_by_count(3)
                assert len(result_by_count["teams"]) == 3

                # Format output
                formatted = picker.format_teams_output(result_by_size)
                assert "TEAM ASSIGNMENT RESULTS" in formatted

                # Save to JSON
                with tempfile.TemporaryDirectory() as temp_dir:
                    json_file = Path(temp_dir) / "test_teams.json"
                    picker.save_teams_to_json(result_by_size, str(json_file))
                    assert json_file.exists()

    def test_result_structure_consistency(self):
        """Test that result structure is consistent across methods."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                picker = TeamPicker()

                result_by_size = picker.create_teams_by_size(2)
                result_by_count = picker.create_teams_by_count(2)

                # Both should have same structure
                for result in [result_by_size, result_by_count]:
                    assert "teams" in result
                    assert "method" in result
                    assert "total_students" in result
                    assert "num_teams" in result
                    assert "base_team_size" in result

                    # Each team should have proper structure
                    for team in result["teams"]:
                        assert "team_number" in team
                        assert "members" in team
                        assert isinstance(team["members"], list)

                        # Each member should have proper structure
                        for member in team["members"]:
                            assert "name" in member
                            assert "email" in member
