from app import app, db
from sqlalchemy import text

# Fix users table to support 'prof' and 'ta' roles
# SQLite doesn't support ALTER TABLE for CHECK constraints easily,
# so we'll recreate the table without the restrictive constraint

with app.app_context():
    try:
        # Create new users table with updated constraint
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS users_new (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL,
                email VARCHAR(100),
                course_code VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Copy data from old table
        db.session.execute(text("""
            INSERT INTO users_new (user_id, username, password_hash, role, email, course_code, created_at)
            SELECT user_id, username, password_hash, role, email, course_code, created_at
            FROM users
        """))
        
        # Drop old table
        db.session.execute(text("DROP TABLE users"))
        
        # Rename new table
        db.session.execute(text("ALTER TABLE users_new RENAME TO users"))
        
        db.session.commit()
        print("Users table updated successfully - now supports 'prof' and 'ta' roles!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        print("Note: If table already updated, this is expected.")
