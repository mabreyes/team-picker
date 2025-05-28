"""Tests for the team_picker_app module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from models import AssignmentMethod, Student, Team, TeamAssignmentResult
from team_picker_app import TeamPickerApp


class TestTeamPickerApp:
    """Test cases for the TeamPickerApp class."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.test_content = (
            "user1@test.com\nuser2@test.com\nuser3@test.com\nuser4@test.com\n"
        )

    def test_init_default_params(self):
        """Test TeamPickerApp initialization with default parameters."""
        app = TeamPickerApp()

        assert app.student_repository.file_path == Path("student_list.txt")
        assert app.output_dir == Path("output")
        assert app.assignment_service is not None
        assert app.json_service is not None
        assert app.image_service is not None
        assert app.formatter is not None

    def test_init_custom_params(self):
        """Test TeamPickerApp initialization with custom parameters."""
        app = TeamPickerApp(student_file="custom.txt", output_dir="custom_output")

        assert app.student_repository.file_path == Path("custom.txt")
        assert app.output_dir == Path("custom_output")

    def test_load_students(self):
        """Test loading students through the app."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                students = app.load_students()

        assert len(students) == 4
        assert all(isinstance(s, Student) for s in students)
        assert students[0].email == "user1@test.com"

    def test_create_teams_by_count(self):
        """Test creating teams by count through the app."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                result = app.create_teams_by_count(2)

        assert isinstance(result, TeamAssignmentResult)
        assert result.method == AssignmentMethod.BY_COUNT
        assert result.total_students == 4
        assert result.num_teams == 2
        assert len(result.teams) == 2

    def test_create_teams_by_size(self):
        """Test creating teams by size through the app."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                result = app.create_teams_by_size(2)

        assert isinstance(result, TeamAssignmentResult)
        assert result.method == AssignmentMethod.BY_SIZE
        assert result.total_students == 4
        assert result.base_team_size == 2
        assert len(result.teams) == 2

    def test_format_result(self):
        """Test formatting result through the app."""
        students = [Student(email=f"user{i}@test.com") for i in range(2)]
        teams = [Team(team_number=1, members=students)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=2,
            num_teams=1,
            base_team_size=2,
        )

        app = TeamPickerApp()
        formatted = app.format_result(result)

        assert "TEAM ASSIGNMENT RESULTS" in formatted
        assert "Team 1" in formatted

    def test_export_result(self):
        """Test exporting result through the app."""
        students = [Student(email=f"user{i}@test.com") for i in range(2)]
        teams = [Team(team_number=1, members=students)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=2,
            num_teams=1,
            base_team_size=2,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            app = TeamPickerApp(output_dir=temp_dir)

            # Mock the image export to avoid matplotlib dependencies
            with patch.object(app.image_service, "export_result") as mock_image_export:
                mock_image_export.return_value = Path(temp_dir) / "images" / "test.png"

                exported = app.export_result(result, "test")

        assert "json_file" in exported
        assert "image_file" in exported
        assert "test.json" in exported["json_file"]
        assert "test.png" in exported["image_file"]

    def test_export_student_list(self):
        """Test exporting student list through the app."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    app = TeamPickerApp(output_dir=temp_dir)

                    # Mock the image export to avoid matplotlib dependencies
                    with patch.object(
                        app.image_service, "export_student_list"
                    ) as mock_image_export:
                        mock_image_export.return_value = (
                            Path(temp_dir) / "images" / "students.png"
                        )

                        exported = app.export_student_list("students")

        assert "json_file" in exported
        assert "image_file" in exported
        assert "students.json" in exported["json_file"]
        assert "students.png" in exported["image_file"]

    def test_get_student_count(self):
        """Test getting student count through the app."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                count = app.get_student_count()

        assert count == 4

    def test_get_output_directory(self):
        """Test getting output directory path."""
        app = TeamPickerApp(output_dir="custom_output")
        output_dir = app.get_output_directory()

        assert output_dir == "custom_output"

    def test_create_sample_student_file_default(self):
        """Test creating sample student file with default count."""
        with tempfile.TemporaryDirectory() as temp_dir:
            student_file = Path(temp_dir) / "test_students.txt"
            app = TeamPickerApp(student_file=str(student_file))

            app.create_sample_student_file()

            # Verify file was created
            assert student_file.exists()

            # Verify content
            with open(student_file, "r") as f:
                lines = f.readlines()

            assert len(lines) == 30  # Default count is 30, not 10
            assert "student01@dlsu.edu.ph" in lines[0]
            assert "student30@dlsu.edu.ph" in lines[-1]

    def test_create_sample_student_file_custom_count(self):
        """Test creating sample student file with custom count."""
        with tempfile.TemporaryDirectory() as temp_dir:
            student_file = Path(temp_dir) / "test_students.txt"
            app = TeamPickerApp(student_file=str(student_file))

            app.create_sample_student_file(5)

            # Verify file was created
            assert student_file.exists()

            # Verify content
            with open(student_file, "r") as f:
                lines = f.readlines()

            assert len(lines) == 5
            assert "student01@dlsu.edu.ph" in lines[0]
            assert "student05@dlsu.edu.ph" in lines[-1]

    def test_export_result_with_auto_filename(self):
        """Test exporting result with auto-generated filename."""
        students = [Student(email=f"user{i}@test.com") for i in range(2)]
        teams = [Team(team_number=1, members=students)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=2,
            num_teams=1,
            base_team_size=2,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            app = TeamPickerApp(output_dir=temp_dir)

            # Mock the image export
            with patch.object(app.image_service, "export_result") as mock_image_export:
                mock_image_export.return_value = Path(temp_dir) / "images" / "auto.png"

                # Test with None filename (should auto-generate)
                exported = app.export_result(result, None)

        assert "json_file" in exported
        assert "image_file" in exported

    def test_export_student_list_with_auto_filename(self):
        """Test exporting student list with auto-generated filename."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    app = TeamPickerApp(output_dir=temp_dir)

                    # Mock the image export
                    with patch.object(
                        app.image_service, "export_student_list"
                    ) as mock_image_export:
                        mock_image_export.return_value = (
                            Path(temp_dir) / "images" / "auto.png"
                        )

                        # Test with None filename (should auto-generate)
                        exported = app.export_student_list(None)

        assert "json_file" in exported
        assert "image_file" in exported

    def test_error_propagation_load_students(self):
        """Test that errors from student loading are propagated."""
        with patch.object(Path, "exists", return_value=False):
            app = TeamPickerApp()
            with pytest.raises(FileNotFoundError):
                app.load_students()

    def test_error_propagation_create_teams_by_count(self):
        """Test that errors from team creation are propagated."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                with pytest.raises(ValueError):
                    app.create_teams_by_count(0)  # Invalid team count

    def test_error_propagation_create_teams_by_size(self):
        """Test that errors from team creation are propagated."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                app = TeamPickerApp()
                with pytest.raises(ValueError):
                    app.create_teams_by_size(0)  # Invalid team size

    def test_integration_full_workflow(self):
        """Test complete workflow integration."""
        with patch("builtins.open", mock_open(read_data=self.test_content)):
            with patch.object(Path, "exists", return_value=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    app = TeamPickerApp(output_dir=temp_dir)

                    # Load students
                    students = app.load_students()
                    assert len(students) == 4

                    # Create teams
                    result = app.create_teams_by_count(2)
                    assert len(result.teams) == 2

                    # Format result
                    formatted = app.format_result(result)
                    assert "TEAM ASSIGNMENT RESULTS" in formatted

                    # Export result (mock image export)
                    with patch.object(
                        app.image_service, "export_result"
                    ) as mock_image_export:
                        mock_image_export.return_value = (
                            Path(temp_dir) / "images" / "test.png"
                        )
                        exported = app.export_result(result, "integration_test")

                    # Verify exports
                    assert Path(exported["json_file"]).exists()
                    assert "integration_test.json" in exported["json_file"]

    def test_directory_creation_on_export(self):
        """Test that output directories are created during export."""
        students = [Student(email=f"user{i}@test.com") for i in range(2)]
        teams = [Team(team_number=1, members=students)]
        result = TeamAssignmentResult(
            teams=teams,
            method=AssignmentMethod.BY_COUNT,
            total_students=2,
            num_teams=1,
            base_team_size=2,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            output_path = Path(temp_dir) / "nested" / "output"
            app = TeamPickerApp(output_dir=str(output_path))

            # Mock the image export
            with patch.object(app.image_service, "export_result") as mock_image_export:
                mock_image_export.return_value = output_path / "images" / "test.png"

                exported = app.export_result(result, "test")

            # Verify directories were created
            assert (output_path / "json").exists()
            assert Path(exported["json_file"]).exists()


class TestTeamPickerAppMain:
    """Test cases for the main function in team_picker_app module."""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_exit(self, mock_print, mock_input):
        """Test main function with immediate exit."""
        # Mock user choosing to exit immediately
        mock_input.side_effect = ["5"]  # Exit option

        with patch("builtins.open", mock_open(read_data="user@test.com\n")):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify exit message was printed
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Goodbye!" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_invalid_choice(self, mock_print, mock_input):
        """Test main function with invalid choice."""
        # Mock user entering invalid choice then exit
        mock_input.side_effect = ["9", "5"]  # Invalid choice, then exit

        with patch("builtins.open", mock_open(read_data="user@test.com\n")):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify error message was printed
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Invalid choice" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_create_teams_by_size(self, mock_print, mock_input):
        """Test main function creating teams by size."""
        # Mock user creating teams by size, no export, then exit
        mock_input.side_effect = [
            "1",
            "2",
            "n",
            "5",
        ]  # Team size, size=2, no export, exit

        test_data = (
            "user1@test.com\nuser2@test.com\n" "user3@test.com\nuser4@test.com\n"
        )
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify team creation output
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("TEAM ASSIGNMENT RESULTS" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_create_teams_by_count(self, mock_print, mock_input):
        """Test main function creating teams by count."""
        # Mock user creating teams by count, no export, then exit
        mock_input.side_effect = [
            "2",
            "2",
            "n",
            "5",
        ]  # Team count, count=2, no export, exit

        test_data = (
            "user1@test.com\nuser2@test.com\n" "user3@test.com\nuser4@test.com\n"
        )
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify team creation output
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("TEAM ASSIGNMENT RESULTS" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_view_students(self, mock_print, mock_input):
        """Test main function viewing all students."""
        # Mock user viewing students then exit
        mock_input.side_effect = ["3", "5"]  # View students, exit

        test_data = "user1@test.com\nuser2@test.com\n"
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify student list output
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("User1" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_export_student_list(self, mock_print, mock_input):
        """Test main function exporting student list."""
        # Mock user exporting student list then exit
        mock_input.side_effect = [
            "4",
            "",
            "5",
        ]  # Export students, auto filename, exit

        test_data = "user1@test.com\nuser2@test.com\n"
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch("team_picker_app.TeamPickerApp") as mock_app_class:
                        mock_app = Mock()
                        mock_app.get_student_count.return_value = 2
                        mock_app.get_output_directory.return_value = temp_dir
                        mock_app.load_students.return_value = [Mock(), Mock()]
                        mock_app.export_student_list.return_value = {
                            "json_file": f"{temp_dir}/students.json",
                            "image_file": f"{temp_dir}/students.png",
                        }
                        mock_app_class.return_value = mock_app

                        from team_picker_app import main

                        main()

        # Verify export success message
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("exported" in call.lower() for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_with_export(self, mock_print, mock_input):
        """Test main function with team creation and export."""
        # Mock user creating teams and exporting
        mock_input.side_effect = [
            "1",
            "2",
            "y",
            "custom_name",
            "5",
        ]  # Team size, size=2, export, custom name, exit

        test_data = (
            "user1@test.com\nuser2@test.com\n" "user3@test.com\nuser4@test.com\n"
        )
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch("team_picker_app.TeamPickerApp") as mock_app_class:
                        mock_app = Mock()
                        mock_app.get_student_count.return_value = 4
                        mock_app.get_output_directory.return_value = temp_dir
                        mock_app.create_teams_by_size.return_value = Mock()
                        mock_app.format_result.return_value = (
                            "TEAM ASSIGNMENT RESULTS\nTest output"
                        )
                        mock_app.export_result.return_value = {
                            "json_file": f"{temp_dir}/custom_name.json",
                            "image_file": f"{temp_dir}/custom_name.png",
                        }
                        mock_app_class.return_value = mock_app

                        from team_picker_app import main

                        main()

        # Verify export success message
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Exported" in call for call in print_calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_main_function_value_error_handling(self, mock_print, mock_input):
        """Test main function handling ValueError during team creation."""
        # Mock user entering invalid team size
        mock_input.side_effect = [
            "1",
            "0",
            "5",
        ]  # Team size, invalid size=0, exit

        test_data = "user1@test.com\nuser2@test.com\n"
        with patch("builtins.open", mock_open(read_data=test_data)):
            with patch.object(Path, "exists", return_value=True):
                from team_picker_app import main

                main()

        # Verify error message was printed
        assert mock_print.called
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error:" in call for call in print_calls)
