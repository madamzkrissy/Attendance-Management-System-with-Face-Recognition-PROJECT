#!/usr/bin/env python
"""
Test script to verify the Attendance Management System setup
"""

import os
import sys

def test_imports():
    """Test all required imports"""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    imports = [
        ("Flask", "flask"),
        ("Flask-SQLAlchemy", "flask_sqlalchemy"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("Pillow", "PIL"),
        ("face-recognition", "face_recognition"),
        ("werkzeug", "werkzeug.security"),
    ]
    
    all_ok = True
    for name, module in imports:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError as e:
            print(f"[FAIL] {name}: {e}")
            all_ok = False
    
    return all_ok

def test_database():
    """Test database configuration"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE")
    print("=" * 60)
    
    try:
        from database import db, Teacher, Student, Section, Attendance, init_db
        print("[OK] Database models imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Database import failed: {e}")
        return False

def test_app():
    """Test Flask app configuration"""
    print("\n" + "=" * 60)
    print("TESTING FLASK APP")
    print("=" * 60)
    
    try:
        from app import app
        print("[OK] Flask app configured successfully")
        print(f"[OK] Debug mode: {app.debug}")
        return True
    except Exception as e:
        print(f"[FAIL] Flask app configuration failed: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("\n" + "=" * 60)
    print("TESTING DIRECTORIES")
    print("=" * 60)
    
    required_dirs = [
        "static/css",
        "static/js",
        "static/images",
        "templates",
        "encodings",
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"[OK] {directory}")
        else:
            os.makedirs(directory, exist_ok=True)
            print(f"[CREATED] {directory}")
    
    return all_ok

def main():
    """Run all tests"""
    print("\n")
    print("###############################################")
    print("# ATTENDANCE SYSTEM - SETUP VERIFICATION")
    print("###############################################")
    print()
    
    results = {
        "Imports": test_imports(),
        "Database": test_database(),
        "Flask App": test_app(),
        "Directories": test_directories(),
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    if all(results.values()):
        print("\n✓ All tests passed! System is ready to run.")
        print("\nTo start the application, run:")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
