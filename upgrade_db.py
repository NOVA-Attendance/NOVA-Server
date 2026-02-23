from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Add 'email' column
        db.session.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(255);"))
        # Add 'student_number' column
        db.session.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS student_number VARCHAR(50);"))
        
        db.session.commit()
        print("Success! Added 'email' and 'student_number' to the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")