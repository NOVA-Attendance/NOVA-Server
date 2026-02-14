from app import app, db
from sqlalchemy import text

# Create comments table for tagging photos/attendance logs

with app.app_context():
    try:
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
        print("Success! Comments table created successfully.")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating comments table: {e}")
