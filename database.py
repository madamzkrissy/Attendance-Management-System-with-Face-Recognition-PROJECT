from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ============ DATABASE MODELS ============

class Teacher(db.Model):
    __tablename__ = 'teacher'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sections = db.relationship('Section', backref='teacher', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Teacher {self.name}>'

class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    sr_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    face_encoding_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    section = db.relationship('Section', backref='students', foreign_keys=[section_id])
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.sr_code} {self.name}>'

class Section(db.Model):
    __tablename__ = 'section'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    schedule = db.Column(db.String(255), nullable=True)  # e.g., "MWF 8:00-9:00"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='section', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Section {self.name}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)
    marked_by = db.Column(db.String(50), nullable=False)  # face_recognition, teacher, system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    # student and section relationships are defined in their models
    
    def __repr__(self):
        return f'<Attendance {self.student_id} {self.date} {self.status}>'

# ============ DATABASE INITIALIZATION ============

def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully")