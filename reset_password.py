#!/usr/bin/env python3
"""
Reset password for a user
"""
from app import app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def reset_password(email, new_password):
    """Reset password for a user"""
    with app.app_context():
        try:
            # Check if user exists
            result = db.session.execute(text("""
                SELECT user_id, email FROM users WHERE email = :email
            """), {'email': email}).fetchone()
            
            if not result:
                print(f"User with email {email} not found")
                return False
            
            # Hash the new password
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            
            # Update password
            db.session.execute(text("""
                UPDATE users SET password_hash = :password_hash WHERE email = :email
            """), {'email': email, 'password_hash': hashed_password})
            db.session.commit()
            
            print(f"Password reset successful for {email}")
            print(f"New password: {new_password}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting password: {e}")
            return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 reset_password.py <email> <new_password>")
        print("\nExample:")
        print("  python3 reset_password.py eknoormeetsingh@gmail.com password123")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    if len(new_password) < 6:
        print("Error: Password must be at least 6 characters long")
        sys.exit(1)
    
    reset_password(email, new_password)
