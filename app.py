#!/usr/bin/env python3
"""Team Picker Web Application.

A minimalist, professional web interface for team assignment.
"""

import base64
import os
from datetime import datetime
from pathlib import Path

import matplotlib
from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from models import Student
from team_picker_app import TeamPickerApp

try:
    from striprtf.striprtf import rtf_to_text

    RTF_SUPPORT = True
except ImportError:
    RTF_SUPPORT = False
    print("Warning: striprtf not installed. RTF file support disabled.")


def process_students_with_duplicates(emails, source="upload"):
    """Process a list of emails into student objects, handling duplicates.

    Args:
        emails: List of email addresses
        source: Source of the emails (for error messages)

    Returns:
        tuple: (students_list, duplicates_list, errors_list)
    """
    students = []
    seen_emails = set()
    duplicates = []
    errors = []

    for i, email in enumerate(emails, 1):
        email = email.strip()

        # Skip empty emails
        if not email:
            continue

        # Check for duplicate
        if email.lower() in seen_emails:
            duplicates.append({"email": email, "line": i})
            continue

        # Validate email format
        if "@" not in email:
            errors.append({"email": email, "line": i, "error": "Invalid email format"})
            continue

        try:
            # Create student object
            student = Student(email=email)
            students.append({"name": student.name, "email": email})
            seen_emails.add(email.lower())
        except Exception as e:
            errors.append({"email": email, "line": i, "error": str(e)})

    return students, duplicates, errors


# Configure matplotlib to use non-GUI backend
matplotlib.use("Agg")

app = Flask(__name__)

# Production-ready configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "team-picker-secret-key-2024")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure output directories exist
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_FOLDER, "json"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_FOLDER, "images"), exist_ok=True)


@app.route("/")
def index():
    """Main application page."""
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_students():
    """Upload and process student list file."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        filename = file.filename.lower()
        if filename.endswith(".txt"):
            file_type = "txt"
        elif filename.endswith(".rtf"):
            if not RTF_SUPPORT:
                return (
                    jsonify(
                        {
                            "error": (
                                "RTF file support not available. "
                                "Please install striprtf or use a .txt file."
                            )
                        }
                    ),
                    400,
                )
            file_type = "rtf"
        else:
            return jsonify({"error": "Please upload a .txt or .rtf file"}), 400

        # Save uploaded file
        secure_name = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_name)
        file.save(filepath)

        try:
            # Parse file content based on type
            if file_type == "txt":
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file_type == "rtf":
                with open(filepath, "r", encoding="utf-8") as f:
                    rtf_content = f.read()
                content = rtf_to_text(rtf_content)

            # Parse students from content
            lines = content.strip().split("\n")
            emails = []

            for line in lines:
                email = line.strip()
                # Skip empty lines and common RTF artifacts
                if not email or email.startswith("{") or email.startswith("\\"):
                    continue

                # Clean up any remaining RTF formatting
                email = email.replace("}", "").replace("{", "").strip()
                if email:
                    emails.append(email)

            # Process emails with duplicate detection
            students, duplicates, errors = process_students_with_duplicates(
                emails, source="file_upload"
            )

            if not students:
                return jsonify({"error": "No valid email addresses found"}), 400

            # Prepare response with duplicate and error information
            response_data = {
                "success": True,
                "students": students,
                "count": len(students),
                "file_type": file_type.upper(),
            }

            # Add warnings for duplicates and errors if any
            warnings = []
            if duplicates:
                duplicate_count = len(duplicates)
                plural_suffix = "s" if duplicate_count != 1 else ""
                warnings.append(
                    f"Removed {duplicate_count} duplicate email{plural_suffix}"
                )

            if errors:
                error_count = len(errors)
                plural_suffix = "s" if error_count != 1 else ""
                warnings.append(f"Skipped {error_count} invalid email{plural_suffix}")

            if warnings:
                response_data["warnings"] = warnings
                response_data["duplicates"] = duplicates
                response_data["errors"] = errors

            return jsonify(response_data)

        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

    except Exception as e:
        return jsonify({"error": f"File processing error: {str(e)}"}), 500


@app.route("/api/create-teams", methods=["POST"])
def create_teams():
    """Create teams from student data."""
    try:
        data = request.get_json()
        students_data = data.get("students", [])
        method = data.get("method", "by_count")
        value = data.get("value", 4)

        if not students_data:
            return jsonify({"error": "No students provided"}), 400

        # Create temporary student list file
        temp_file = os.path.join(
            app.config["UPLOAD_FOLDER"], f"temp_{datetime.now().timestamp()}.txt"
        )

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                for student in students_data:
                    f.write(f"{student['email']}\n")

            # Create teams using existing logic
            team_app = TeamPickerApp(temp_file)

            if method == "by_count":
                result = team_app.create_teams_by_count(int(value))
            else:
                result = team_app.create_teams_by_size(int(value))

            # Generate exports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exports = team_app.export_result(result, f"web_teams_{timestamp}")

            # Convert to web-friendly format
            teams_data = []
            for team in result.teams:
                teams_data.append(
                    {
                        "team_number": team.team_number,
                        "members": [
                            {"name": member.name, "email": member.email}
                            for member in team.members
                        ],
                        "size": team.size,
                    }
                )

            # Create temporary image and convert to base64
            temp_img_path = exports["image_file"]
            with open(temp_img_path, "rb") as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode("utf-8")

            response_data = {
                "success": True,
                "teams": teams_data,
                "metadata": {
                    "num_teams": len(teams_data),
                    "total_students": sum(
                        team["size"]
                        for team in teams_data
                        if isinstance(team["size"], int)
                    ),
                    "method": method,
                    "timestamp": timestamp,
                },
                "image_base64": img_base64,
                "download_links": {
                    "json": f"/api/download/json/{timestamp}",
                    "image": f"/api/download/image/{timestamp}",
                },
            }

            return jsonify(response_data)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    except Exception as e:
        return jsonify({"error": f"Team creation error: {str(e)}"}), 500


@app.route("/api/manual-students", methods=["POST"])
def create_manual_students():
    """Create student data from manually entered email addresses."""
    try:
        data = request.get_json()
        emails = data.get("emails", [])

        if not emails:
            return jsonify({"error": "No emails provided"}), 400

        # Filter out empty emails and validate format
        valid_emails = []
        for email in emails:
            email = email.strip()
            if email and "@" in email:
                valid_emails.append(email)

        if not valid_emails:
            return jsonify({"error": "No valid email addresses provided"}), 400

        # Create student objects from emails using the existing Student model
        students, duplicates, errors = process_students_with_duplicates(
            valid_emails, source="manual_entry"
        )

        if not students:
            return (
                jsonify(
                    {"error": "Could not process any of the provided email addresses"}
                ),
                400,
            )

        return jsonify(
            {
                "success": True,
                "students": students,
                "count": len(students),
                "source": "manual_entry",
                "duplicates": duplicates,
                "errors": errors,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Manual student creation error: {str(e)}"}), 500


@app.route("/api/download/json/<timestamp>")
def download_json(timestamp):
    """Download JSON export file."""
    try:
        json_path = Path(f"output/json/web_teams_{timestamp}.json")
        if json_path.exists():
            return send_file(
                json_path, as_attachment=True, download_name=f"teams_{timestamp}.json"
            )
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/image/<timestamp>")
def download_image(timestamp):
    """Download PNG export file."""
    try:
        img_path = Path(f"output/images/web_teams_{timestamp}.png")
        if img_path.exists():
            return send_file(
                img_path, as_attachment=True, download_name=f"teams_{timestamp}.png"
            )
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sample-data")
def get_sample_data():
    """Get sample student data for demo purposes."""
    sample_emails = [
        "john.doe@university.edu",
        "jane.smith@university.edu",
        "alex.johnson@university.edu",
        "maria.garcia@university.edu",
        "david.brown@university.edu",
        "sarah.wilson@university.edu",
        "michael.davis@university.edu",
        "emily.taylor@university.edu",
        "james.anderson@university.edu",
        "lisa.thomas@university.edu",
        "robert.jackson@university.edu",
        "jennifer.white@university.edu",
    ]

    # Process sample emails with duplicate detection for consistency
    students, duplicates, errors = process_students_with_duplicates(
        sample_emails, source="sample_data"
    )

    return jsonify(
        {
            "success": True,
            "students": students,
            "count": len(students),
            "source": "sample_data",
        }
    )


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error handler."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Custom 500 error handler."""
    return render_template("500.html"), 500


@app.errorhandler(403)
def forbidden(error):
    """Custom 403 error handler."""
    return render_template("404.html"), 403  # Use 404 template for 403 as well


if __name__ == "__main__":
    # Development configuration
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)  # nosec B104
