from app import app, db
from sqlalchemy import text
import sys

def update_course_code(email, new_course_code):
    """Update a user's course code in the database"""
    with app.app_context():
        try:
            # Check if user exists
            user_result = db.session.execute(text("""
                SELECT user_id, email, course_code FROM users WHERE email = :email
            """), {'email': email}).fetchone()

            if not user_result:
                print(f"Error: User with email '{email}' not found.")
                return False

            old_course_code = user_result.course_code
            print(f"Found user: {email}")
            print(f"   Current course_code: {old_course_code}")

            # Update course code
            db.session.execute(text("""
                UPDATE users SET course_code = :new_course_code WHERE email = :email
            """), {'new_course_code': new_course_code, 'email': email})
            db.session.commit()

            print(f"Course code updated successfully!")
            print(f"   Old: {old_course_code}")
            print(f"   New: {new_course_code}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating course code: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) == 3:
        email_to_update = sys.argv[1]
        new_course_code = sys.argv[2]
        update_course_code(email_to_update, new_course_code)
    else:
        print("Usage: python3 update_course_code.py <email> <new_course_code>")
        print("\nExample:")
        print("  python3 update_course_code.py eknoormeetsingh@gmail.com CEG4913")
        sys.exit(1)
