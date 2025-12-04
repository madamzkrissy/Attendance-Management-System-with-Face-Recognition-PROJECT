import os
import pickle
import base64
import json
from datetime import datetime, timedelta
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from database import db, init_db, Teacher, Student, Section, Attendance
import face_recognition

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    init_db()

# Decorator for teacher-only routes
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'teacher':
            return redirect(url_for('teacher_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/take_attendance/<int:section_id>', methods=['GET'])
@teacher_required
def take_attendance(section_id):
    """Teacher takes attendance for a section"""
    section = Section.query.get_or_404(section_id)
    
    # Get all students in this section
    students = Student.query.filter_by(section_id=section_id).all()
    
    # Get today's attendance records
    today = datetime.now().date()
    attendance_records = Attendance.query.filter(
        Attendance.section_id == section_id,
        Attendance.date == today
    ).all()
    
    # Create attendance dictionary
    attendance_dict = {}
    present_count = 0
    absent_count = 0
    late_count = 0
    
    for record in attendance_records:
        attendance_dict[record.student_id] = {
            'status': record.status,
            'time_in': record.time_in.strftime('%I:%M %p') if record.time_in else '--'
        }
        if record.status == 'present':
            present_count += 1
        elif record.status == 'late':
            late_count += 1
        elif record.status == 'absent':
            absent_count += 1
    
    return render_template('take_attendance.html',
                         section=section,
                         students=students,
                         attendance=attendance_dict,
                         present_count=present_count,
                         absent_count=absent_count,
                         late_count=late_count,
                         current_date=today.strftime('%B %d, %Y'))

@app.route('/detect_face_attendance', methods=['POST'])
@teacher_required
def detect_face_attendance():
    """Detect face during attendance taking"""
    try:
        data = request.get_json()
        image_data = data['image']
        section_id = data['section_id']
        
        # Convert base64 image to OpenCV format
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        
        if not face_encodings:
            return jsonify({'success': False, 'message': 'No face detected'})
        
        # Load known encodings for this section
        section = Section.query.get(section_id)
        students = Student.query.filter_by(section_id=section_id).all()
        
        # Match faces
        for face_encoding in face_encodings:
            for student in students:
                # Load student encoding
                encoding_path = os.path.join('encodings', f"{student.sr_code}.pkl")
                if os.path.exists(encoding_path):
                    with open(encoding_path, 'rb') as f:
                        known_encoding = pickle.load(f)
                    
                    # Compare faces
                    matches = face_recognition.compare_faces([known_encoding], face_encoding)
                    
                    if True in matches:
                        # Mark attendance
                        mark_attendance_for_student(student.id, section_id)
                        
                        return jsonify({
                            'success': True,
                            'student': {
                                'id': student.id,
                                'name': student.name,
                                'sr_code': student.sr_code
                            },
                            'status': calculate_attendance_status()
                        })
        
        return jsonify({'success': False, 'message': 'Face not recognized'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/mark_attendance', methods=['POST'])
@teacher_required
def mark_attendance():
    """Manually mark attendance for a student"""
    try:
        data = request.get_json()
        sr_code = data['sr_code']
        section_id = data['section_id']
        status = data['status']
        manual = data.get('manual', False)
        
        student = Student.query.filter_by(sr_code=sr_code, section_id=section_id).first()
        if not student:
            return jsonify({'success': False, 'message': 'Student not found in this section'})
        
        today = datetime.now().date()
        
        # Check if already marked today
        existing = Attendance.query.filter_by(
            student_id=student.id,
            section_id=section_id,
            date=today
        ).first()
        
        if existing:
            existing.status = status
            existing.time_in = datetime.now() if status in ['present', 'late'] else None
        else:
            attendance = Attendance(
                student_id=student.id,
                section_id=section_id,
                date=today,
                status=status,
                time_in=datetime.now() if status in ['present', 'late'] else None,
                marked_by='teacher' if manual else 'face_recognition'
            )
            db.session.add(attendance)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Attendance marked as {status}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/end_attendance_session', methods=['POST'])
@teacher_required
def end_attendance_session():
    """End the attendance session and mark remaining as absent"""
    try:
        data = request.get_json()
        section_id = data['section_id']
        
        section = Section.query.get(section_id)
        students = Student.query.filter_by(section_id=section_id).all()
        today = datetime.now().date()
        
        # Mark absent for students without attendance
        for student in students:
            existing = Attendance.query.filter_by(
                student_id=student.id,
                section_id=section_id,
                date=today
            ).first()
            
            if not existing:
                attendance = Attendance(
                    student_id=student.id,
                    section_id=section_id,
                    date=today,
                    status='absent',
                    time_in=None,
                    marked_by='system'
                )
                db.session.add(attendance)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Attendance session ended'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def calculate_attendance_status():
    """Calculate if student is late based on schedule"""
    current_time = datetime.now().time()
    
    # Example: If schedule is "MWF 8:00-9:00 AM"
    # You would parse the schedule and check if current time is after start time
    # This is a simplified version
    late_threshold = datetime.strptime('08:15', '%H:%M').time()
    
    if current_time > late_threshold:
        return 'late'
    else:
        return 'present'

def mark_attendance_for_student(student_id, section_id):
    """Mark attendance for a specific student"""
    today = datetime.now().date()
    
    existing = Attendance.query.filter_by(
        student_id=student_id,
        section_id=section_id,
        date=today
    ).first()
    
    if not existing:
        status = calculate_attendance_status()
        
        attendance = Attendance(
            student_id=student_id,
            section_id=section_id,
            date=today,
            status=status,
            time_in=datetime.now(),
            marked_by='face_recognition'
        )
        db.session.add(attendance)
        db.session.commit()
        
    return True

# ============ STUDENT ROUTES ============

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    """Student login page"""
    if request.method == 'POST':
        data = request.get_json()
        sr_code = data.get('sr_code')
        
        student = Student.query.filter_by(sr_code=sr_code).first()
        if student:
            session['user_id'] = student.id
            session['user_type'] = 'student'
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'SR Code not found'})
    
    return render_template('student_login.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    """Student registration page"""
    if request.method == 'POST':
        data = request.get_json()
        sr_code = data.get('sr_code')
        name = data.get('name')
        email = data.get('email')
        
        existing = Student.query.filter_by(sr_code=sr_code).first()
        if existing:
            return jsonify({'success': False, 'message': 'SR Code already registered'})
        
        student = Student(sr_code=sr_code, name=name, email=email)
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('student_register.html')

@app.route('/student_portal')
def student_portal():
    """Student portal dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        student_id=student_id,
        date=today
    ).first()
    
    return render_template('student_portal.html', student=student, attendance=today_attendance)

@app.route('/student_profile')
def student_profile():
    """Student profile page"""
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    attendance_records = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('student_profile.html', 
                         student=student, 
                         attendance_records=attendance_records)

# ============ GENERAL ROUTES ============

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    """Teacher login page"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher and teacher.check_password(password):
            session['user_id'] = teacher.id
            session['user_type'] = 'teacher'
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('teacher_login.html')

@app.route('/teacher_dashboard')
@teacher_required
def teacher_dashboard():
    """Teacher dashboard"""
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)
    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    
    return render_template('teacher_dashboard.html', teacher=teacher, sections=sections)

@app.route('/teacher_sections')
@teacher_required
def teacher_sections():
    """List sections for teacher"""
    teacher_id = session.get('user_id')
    sections = Section.query.filter_by(teacher_id=teacher_id).all()
    
    sections_data = [{
        'id': s.id,
        'name': s.name,
        'student_count': len(s.students)
    } for s in sections]
    
    return jsonify(sections_data)

@app.route('/view_attendance/<int:section_id>')
@teacher_required
def view_attendance(section_id):
    """View attendance records"""
    section = Section.query.get_or_404(section_id)
    students = Student.query.filter_by(section_id=section_id).all()
    
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    attendance_records = Attendance.query.filter(
        Attendance.section_id == section_id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('view_attendance.html',
                         section=section,
                         students=students,
                         attendance_records=attendance_records)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)