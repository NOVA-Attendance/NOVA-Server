from app import app, db
from sqlalchemy import text

# Single source of truth for DB schema setup.
# Run this script to create all required tables/columns used by app.py.

with app.app_context():
    try:
        # Users (auth)
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) UNIQUE,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'teacher', 'prof', 'ta')),
                course_code VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Students
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                student_number VARCHAR(50),
                email VARCHAR(255),
                rfid_tag VARCHAR(50) UNIQUE,
                photo_path TEXT,
                face_embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Classes
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name VARCHAR(50) NOT NULL,
                teacher_id INTEGER,
                schedule VARCHAR(100),
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)
            )
        """))

        # Enrollments
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                class_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                UNIQUE(student_id, class_id)
            )
        """))

        # Attendance logs
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

        # Verification codes for 2-step auth
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) NOT NULL,
                code VARCHAR(6) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Comments linked to attendance logs
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
