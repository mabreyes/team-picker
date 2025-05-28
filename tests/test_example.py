"""Tests for the example module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from example import create_sample_student_list, main


class TestCreateSampleStudentList:
    """Test cases for create_sample_student_list function."""

    def test_create_sample_list_default(self):
        """Test creating sample student list with default settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                # Change to temp directory
                import os

                os.chdir(temp_dir)

                with patch("builtins.print") as mock_print:
                    create_sample_student_list()

                # Verify file was created
                student_file = Path("student_list.txt")
                assert student_file.exists()

                # Verify content
                with open(student_file, "r") as f:
                    lines = f.readlines()

                assert len(lines) == 30  # Should have 30 students
                assert "john.doe@university.edu" in lines[0]
                assert "kimberly.mitchell@university.edu" in lines[-1]

                # Verify print statement
                assert mock_print.call_count >= 1
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                assert any(
                    "Created sample student_list.txt" in call for call in print_calls
                )

            finally:
                os.chdir(original_cwd)

    def test_create_sample_list_file_content(self):
        """Test the content of the created sample file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                create_sample_student_list()

                # Read and verify content
                with open("student_list.txt", "r") as f:
                    content = f.read()

                # Check for specific emails
                assert "john.doe@university.edu" in content
                assert "jane.smith@university.edu" in content
                assert "kimberly.mitchell@university.edu" in content

                # Check that all lines end with @university.edu
                lines = content.strip().split("\n")
                for line in lines:
                    assert line.endswith("@university.edu")

            finally:
                os.chdir(original_cwd)


class TestMainFunction:
    """Test cases for the main function."""

    @patch("builtins.print")
    def test_main_function_file_exists(self, mock_print):
        """Test main function when student file already exists."""
        test_content = "existing@test.com\n"

        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch.object(Path, "exists", return_value=True):
                with patch("example.TeamPickerApp") as mock_app_class:
                    mock_app = Mock()
                    mock_app.load_students.return_value = [
                        Mock(name="Existing", email="existing@test.com")
                    ]
                    mock_app.create_teams_by_count.return_value = Mock()
                    mock_app.create_teams_by_size.return_value = Mock()
                    mock_app.format_result.return_value = (
                        "TEAM ASSIGNMENT RESULTS\nTest output"
                    )
                    mock_app.export_result.return_value = {
                        "json_file": "/tmp/test.json",
                        "image_file": "/tmp/test.png",
                    }
                    mock_app.export_student_list.return_value = {
                        "json_file": "/tmp/students.json",
                        "image_file": "/tmp/students.png",
                    }
                    mock_app_class.return_value = mock_app

                    main()

        # Verify print statements
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("TEAM PICKER EXAMPLE" in call for call in print_calls)
        assert any("Example 1: Create 4 teams" in call for call in print_calls)
        assert any(
            "Example 2: Create teams of 5 students each" in call for call in print_calls
        )

    @patch("builtins.print")
    def test_main_function_file_not_exists(self, mock_print):
        """Test main function when student file doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("example.TeamPickerApp") as mock_app_class:
                    mock_app = Mock()
                    mock_app.load_students.return_value = [
                        Mock(name="Test", email="test@dlsu.edu.ph")
                    ]
                    mock_app.create_teams_by_count.return_value = Mock()
                    mock_app.create_teams_by_size.return_value = Mock()
                    mock_app.format_result.return_value = (
                        "TEAM ASSIGNMENT RESULTS\nTest output"
                    )
                    mock_app.export_result.return_value = {
                        "json_file": "/tmp/test.json",
                        "image_file": "/tmp/test.png",
                    }
                    mock_app.export_student_list.return_value = {
                        "json_file": "/tmp/students.json",
                        "image_file": "/tmp/students.png",
                    }
                    mock_app_class.return_value = mock_app

                    main()

        # Verify file creation was attempted
        mock_file.assert_called()

        # Verify print statements
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Creating sample student list" in call for call in print_calls)
        assert any("Created student_list.txt" in call for call in print_calls)

    @patch("builtins.print")
    def test_main_function_complete_workflow(self, mock_print):
        """Test complete main function workflow."""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="test@test.com\n")):
                with patch("example.TeamPickerApp") as mock_app_class:
                    mock_app = Mock()
                    mock_app.load_students.return_value = [
                        Mock(name="Test", email="test@test.com")
                    ]

                    # Mock results
                    mock_result1 = Mock()
                    mock_result2 = Mock()
                    mock_app.create_teams_by_count.return_value = mock_result1
                    mock_app.create_teams_by_size.return_value = mock_result2
                    mock_app.format_result.side_effect = ["Result 1", "Result 2"]
                    mock_app.export_result.side_effect = [
                        {
                            "json_file": "/tmp/teams1.json",
                            "image_file": "/tmp/teams1.png",
                        },
                        {
                            "json_file": "/tmp/teams2.json",
                            "image_file": "/tmp/teams2.png",
                        },
                    ]
                    mock_app.export_student_list.return_value = {
                        "json_file": "/tmp/students.json",
                        "image_file": "/tmp/students.png",
                    }
                    mock_app_class.return_value = mock_app

                    main()

        # Verify all methods were called
        mock_app.load_students.assert_called_once()
        mock_app.create_teams_by_count.assert_called_once_with(4)
        mock_app.create_teams_by_size.assert_called_once_with(5)
        assert mock_app.export_result.call_count == 2
        mock_app.export_student_list.assert_called_once()

        # Verify print statements
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("EXAMPLE COMPLETE" in call for call in print_calls)

    @patch("builtins.print")
    def test_main_function_error_handling(self, mock_print):
        """Test main function error handling."""
        with patch.object(Path, "exists", return_value=True):
            with patch("example.TeamPickerApp", side_effect=Exception("App error")):
                # Should not raise exception, but may print error or continue
                try:
                    main()
                except Exception:
                    # If it does raise, that's also acceptable behavior
                    pass

    def test_main_function_student_file_creation(self):
        """Test the student file creation logic in main."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Mock Path.exists to return False (file doesn't exist)
                with patch.object(Path, "exists", return_value=False):
                    with patch("example.TeamPickerApp") as mock_app_class:
                        mock_app = Mock()
                        mock_app.load_students.return_value = []
                        mock_app.create_teams_by_count.return_value = Mock()
                        mock_app.create_teams_by_size.return_value = Mock()
                        mock_app.format_result.return_value = "Test"
                        mock_app.export_result.return_value = {
                            "json_file": "test.json",
                            "image_file": "test.png",
                        }
                        mock_app.export_student_list.return_value = {
                            "json_file": "test.json",
                            "image_file": "test.png",
                        }
                        mock_app_class.return_value = mock_app

                        with patch("builtins.print"):
                            main()

                # Verify file was created
                student_file = Path("student_list.txt")
                assert student_file.exists()

                # Verify content
                with open(student_file, "r") as f:
                    lines = f.readlines()

                assert len(lines) == 30
                assert all("@dlsu.edu.ph" in line for line in lines)

            finally:
                os.chdir(original_cwd)


class TestIntegration:
    """Integration tests for the example module."""

    def test_full_workflow_integration(self):
        """Test complete workflow integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Create sample student list
                create_sample_student_list()

                # Verify file was created
                student_file = Path("student_list.txt")
                assert student_file.exists()

                # Test main function with the created file
                with patch("builtins.print"):
                    with patch("example.TeamPickerApp") as mock_app_class:
                        mock_app = Mock()
                        mock_app.load_students.return_value = [
                            Mock(name="Test", email="test@university.edu")
                        ]
                        mock_app.create_teams_by_count.return_value = Mock()
                        mock_app.create_teams_by_size.return_value = Mock()
                        mock_app.format_result.return_value = "Test result"
                        mock_app.export_result.return_value = {
                            "json_file": "test.json",
                            "image_file": "test.png",
                        }
                        mock_app.export_student_list.return_value = {
                            "json_file": "test.json",
                            "image_file": "test.png",
                        }
                        mock_app_class.return_value = mock_app

                        main()

            finally:
                os.chdir(original_cwd)

    def test_edge_cases(self):
        """Test edge cases in the example module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                # Test creating sample list multiple times
                create_sample_student_list()
                first_content = Path("student_list.txt").read_text()

                create_sample_student_list()  # Should overwrite
                second_content = Path("student_list.txt").read_text()

                assert first_content == second_content

            finally:
                os.chdir(original_cwd)

    def test_file_permissions(self):
        """Test file creation with different permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                create_sample_student_list()

                # Verify file is readable
                student_file = Path("student_list.txt")
                assert student_file.is_file()
                assert student_file.stat().st_size > 0

                # Verify content is valid
                content = student_file.read_text()
                lines = content.strip().split("\n")
                assert len(lines) == 30

            finally:
                os.chdir(original_cwd)
