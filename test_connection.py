#!/usr/bin/env python3
"""Quick test to verify the backend is working and returning data"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Test query
        result = db.session.execute(text("SELECT student_id, name, rfid_tag, photo_path FROM students")).fetchall()
        students = [dict(row._mapping) for row in result]
        
        print(f"Database connection successful!")
        print(f"Found {len(students)} students in database:")
        for student in students:
            print(f"   - {student['name']} (ID: {student['student_id']}, RFID: {student['rfid_tag']})")
        
    except Exception as e:
        print(f"Error: {e}")
