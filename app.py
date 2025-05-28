#!/usr/bin/env python3
"""
Team Picker Web Application
A minimalist, professional web interface for team assignment.
"""

import os
import json
import io
import base64
from datetime import datetime
from pathlib import Path

# Configure matplotlib to use non-GUI backend before importing Flask
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

try:
    from striprtf.striprtf import rtf_to_text
    RTF_SUPPORT = True
except ImportError:
    RTF_SUPPORT = False
    print("Warning: striprtf not installed. RTF file support disabled.")

from team_picker_app import TeamPickerApp
from services import StudentRepository, ImageExportService, JsonExportService
from models import Student

app = Flask(__name__)
app.config['SECRET_KEY'] = 'team-picker-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_students():
    """Upload and process student list file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            file_type = 'txt'
        elif filename.endswith('.rtf'):
            if not RTF_SUPPORT:
                return jsonify({
                    'error': 'RTF file support not available. Please install striprtf or use a .txt file.'
                }), 400
            file_type = 'rtf'
        else:
            return jsonify({'error': 'Please upload a .txt or .rtf file'}), 400
        
        # Save uploaded file
        secure_name = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        file.save(filepath)
        
        try:
            # Parse file content based on type
            if file_type == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_type == 'rtf':
                with open(filepath, 'r', encoding='utf-8') as f:
                    rtf_content = f.read()
                content = rtf_to_text(rtf_content)
            
            # Parse students from content
            students = []
            lines = content.strip().split('\n')
            
            for line_num, line in enumerate(lines, 1):
                email = line.strip()
                # Skip empty lines and common RTF artifacts
                if not email or email.startswith('{') or email.startswith('\\'):
                    continue
                    
                if '@' in email:
                    # Clean up any remaining RTF formatting
                    email = email.replace('}', '').replace('{', '').strip()
                    if email and '@' in email:
                        students.append({
                            'name': Student(email=email).name,
                            'email': email
                        })
                elif email and len(email) > 3:  # Ignore very short non-email lines
                    return jsonify({
                        'error': f'Invalid email format on line {line_num}: {email}'
                    }), 400
            
            if not students:
                return jsonify({'error': 'No valid email addresses found'}), 400
            
            return jsonify({
                'success': True,
                'students': students,
                'count': len(students),
                'file_type': file_type.upper()
            })
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
    except Exception as e:
        return jsonify({'error': f'File processing error: {str(e)}'}), 500

@app.route('/api/create-teams', methods=['POST'])
def create_teams():
    """Create teams from student data."""
    try:
        data = request.get_json()
        students_data = data.get('students', [])
        method = data.get('method', 'by_count')
        value = data.get('value', 4)
        
        if not students_data:
            return jsonify({'error': 'No students provided'}), 400
        
        # Create temporary student list file
        temp_file = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{datetime.now().timestamp()}.txt')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                for student in students_data:
                    f.write(f"{student['email']}\n")
            
            # Create teams using existing logic
            team_app = TeamPickerApp(temp_file)
            
            if method == 'by_count':
                result = team_app.create_teams_by_count(int(value))
            else:
                result = team_app.create_teams_by_size(int(value))
            
            # Generate exports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exports = team_app.export_result(result, f"web_teams_{timestamp}")
            
            # Convert to web-friendly format
            teams_data = []
            for team in result.teams:
                teams_data.append({
                    'team_number': team.team_number,
                    'members': [{'name': member.name, 'email': member.email} for member in team.members],
                    'size': team.size
                })
            
            # Generate image as base64 for web display
            image_service = ImageExportService()
            img_buffer = io.BytesIO()
            
            # Create temporary image and convert to base64
            temp_img_path = exports['image_file']
            with open(temp_img_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            response_data = {
                'success': True,
                'teams': teams_data,
                'metadata': {
                    'method': result.method.value,
                    'total_students': result.total_students,
                    'num_teams': result.num_teams,
                    'base_team_size': result.base_team_size,
                    'timestamp': timestamp
                },
                'image_base64': img_base64,
                'download_links': {
                    'json': f"/api/download/json/{timestamp}",
                    'image': f"/api/download/image/{timestamp}"
                }
            }
            
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    except Exception as e:
        return jsonify({'error': f'Team creation error: {str(e)}'}), 500

@app.route('/api/download/json/<timestamp>')
def download_json(timestamp):
    """Download JSON export file."""
    try:
        json_path = Path(f"output/json/web_teams_{timestamp}.json")
        if json_path.exists():
            return send_file(json_path, as_attachment=True, 
                           download_name=f"teams_{timestamp}.json")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/image/<timestamp>')
def download_image(timestamp):
    """Download PNG export file."""
    try:
        img_path = Path(f"output/images/web_teams_{timestamp}.png")
        if img_path.exists():
            return send_file(img_path, as_attachment=True,
                           download_name=f"teams_{timestamp}.png")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-data')
def get_sample_data():
    """Get sample student data for demo purposes."""
    sample_students = [
        {'name': 'John Doe', 'email': 'john.doe@university.edu'},
        {'name': 'Jane Smith', 'email': 'jane.smith@university.edu'},
        {'name': 'Alex Johnson', 'email': 'alex.johnson@university.edu'},
        {'name': 'Maria Garcia', 'email': 'maria.garcia@university.edu'},
        {'name': 'David Brown', 'email': 'david.brown@university.edu'},
        {'name': 'Sarah Wilson', 'email': 'sarah.wilson@university.edu'},
        {'name': 'Michael Davis', 'email': 'michael.davis@university.edu'},
        {'name': 'Emily Taylor', 'email': 'emily.taylor@university.edu'},
        {'name': 'James Anderson', 'email': 'james.anderson@university.edu'},
        {'name': 'Lisa Thomas', 'email': 'lisa.thomas@university.edu'},
        {'name': 'Robert Jackson', 'email': 'robert.jackson@university.edu'},
        {'name': 'Jennifer White', 'email': 'jennifer.white@university.edu'},
    ]
    
    return jsonify({
        'success': True,
        'students': sample_students,
        'count': len(sample_students)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 