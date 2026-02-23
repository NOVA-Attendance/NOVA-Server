from app import app, db
from sqlalchemy import text

# Create tables based on the SQLite schema
# Adapted from novadatabase.sql for SQLite

with app.app_context():
    try:
        # Create students table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                rfid_tag VARCHAR(50) UNIQUE,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create users table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'teacher')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create classes table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name VARCHAR(50) NOT NULL,
                teacher_id INTEGER,
                schedule VARCHAR(100),
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)
            )
        """))
        
        # Create enrollments table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                class_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (class_id) REFERENCES classes(class_id)
            )
        """))
        
        # Create attendance_logs table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                class_id INTEGER,
                method VARCHAR(20) CHECK(method IN ('RFID', 'FACE')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(10) CHECK(status IN ('Present', 'Absent')),
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (class_id) REFERENCES classes(class_id)
            )
        """))
        
        # Create comments table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER,
                student_id INTEGER,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (log_id) REFERENCES attendance_logs(log_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """))
        
        db.session.commit()
        print("Success! All database tables created successfully.")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating tables: {e}")
