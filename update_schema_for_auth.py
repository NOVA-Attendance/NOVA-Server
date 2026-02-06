from app import app, db
from sqlalchemy import text

# Update database schema for new authentication system
# Adds: email, course_code to users table
# Adds: verification_codes table for 2-step auth

with app.app_context():
    try:
        # Add email and course_code columns to users table if they don't exist
        try:
            db.session.execute(text("""
                ALTER TABLE users ADD COLUMN email VARCHAR(100)
            """))
            print("✅ Added email column to users")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Note: email column may already exist: {e}")
        
        try:
            db.session.execute(text("""
                ALTER TABLE users ADD COLUMN course_code VARCHAR(50)
            """))
            print("✅ Added course_code column to users")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Note: course_code column may already exist: {e}")
        
        # Update role check to include 'prof' and 'ta'
        try:
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
            print("✅ Created verification_codes table")
        except Exception as e:
            print(f"Note: verification_codes table may already exist: {e}")
        
        # Add student_number to students table if it doesn't exist
        try:
            db.session.execute(text("""
                ALTER TABLE students ADD COLUMN student_number VARCHAR(50)
            """))
            print("✅ Added student_number column to students")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"Note: student_number column may already exist: {e}")
        
        db.session.commit()
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating schema: {e}")
