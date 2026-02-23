from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import random
import string
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv not installed, just use environment variables directly
    pass

app = Flask(__name__)
# Enable CORS for all routes - allow all origins in development
CORS(app, resources={r"/*": {"origins": "*"}})

# Database Setup
# Default: PostgreSQL. Override with DATABASE_URI in .env if needed (e.g. sqlite for local dev without Postgres).
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'postgresql://postgres:group9@localhost/attendance_system'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Email Configuration
# Set these environment variables or update here for email sending
# IMPORTANT: For 2-step verification to work, you MUST configure email settings
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'true').lower() == 'true'  # Default to true
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')  # Your email address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # Your email password or app password
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'

def send_verification_email(email, code):
    """Send verification code via email - REQUIRED for 2-step verification"""
    # Check if email is properly configured
    if not EMAIL_ENABLED:
        print(f"EMAIL DISABLED")
        print(f"   Set EMAIL_ENABLED=true in .env file to enable 2-step verification")
        print(f"   TEMPORARY CODE for {email}: {code}")
        return False
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(f"EMAIL NOT CONFIGURED")
        print(f"   To enable 2-step verification:")
        print(f"   1. Run: python3 setup_email.py")
        print(f"   2. Or create .env file with EMAIL_SENDER and EMAIL_PASSWORD")
        print(f"   3. See README_EMAIL.md for detailed instructions")
        print(f"   TEMPORARY CODE for {email}: {code}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = email
        msg['Subject'] = 'NOVA - Your Verification Code'
        
        # Email body
        body = f"""
        <html>
          <body>
            <h2>NOVA Verification Code</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #26C6DA; font-size: 32px; letter-spacing: 5px;">{code}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">NOVA - Next-gen Online Verification for Attendance</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Verification code sent via email to {email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"Email authentication failed: {str(e)}")
        print(f"   Check your EMAIL_SENDER and EMAIL_PASSWORD in .env file")
        print(f"   For Gmail: Make sure you're using an App Password, not your regular password")
        print(f"   TEMPORARY CODE for {email}: {code}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {str(e)}")
        print(f"   Check your SMTP server settings (EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)")
        print(f"   TEMPORARY CODE for {email}: {code}")
        return False
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
        print(f"   Check your email configuration in .env file")
        print(f"   TEMPORARY CODE for {email}: {code}")
        return False

# Authentication & User Endpoints

@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with email, name, course code, and role"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    course_code = data.get('course_code')
    role = data.get('role')  # 'prof' or 'ta'

    # Validate required fields with specific messages
    missing_fields = []
    if not name or not name.strip():
        missing_fields.append('Full Name')
    if not email or not email.strip():
        missing_fields.append('Email')
    if not password or not password.strip():
        missing_fields.append('Password')
    if not course_code or not course_code.strip():
        missing_fields.append('Course Code')
    if not role or not role.strip():
        missing_fields.append('Role')
    
    if missing_fields:
        return jsonify({
            'error': f'Please fill in all required fields: {", ".join(missing_fields)}'
        }), 400

    # Validate email format
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'error': 'Please enter a valid email address'}), 400

    # Validate password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    # Validate role
    if role not in ['prof', 'ta']:
        return jsonify({
            'error': f'Invalid role. Role must be either "prof" (Professor) or "ta" (Teaching Assistant)'
        }), 400

    # Check if email already exists
    existing_user = db.session.execute(text("""
        SELECT email FROM users WHERE email = :email
    """), {'email': email}).fetchone()
    
    if existing_user:
        return jsonify({
            'error': 'This email is already registered. Please use a different email or try logging in instead.'
        }), 400

    # Use pbkdf2 method instead of scrypt for Python 3.9 compatibility
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        # SQLite doesn't support RETURNING, so we need to insert then query
        db.session.execute(text("""
            INSERT INTO users (username, email, password_hash, role, course_code)
            VALUES (:username, :email, :password_hash, :role, :course_code)
        """), {
            'username': email,  # Use email as username
            'email': email,
            'password_hash': hashed_password,
            'role': role,  # Store the actual role (prof or ta)
            'course_code': course_code
        })
        db.session.commit()
        
        # Get the inserted user_id
        result = db.session.execute(text("""
            SELECT user_id FROM users WHERE email = :email
        """), {'email': email}).fetchone()
        user_id = result[0] if result else None
        
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e).lower()
        if 'unique' in error_msg or 'username' in error_msg or 'email' in error_msg:
            return jsonify({
                'error': 'This email is already registered. Please use a different email or try logging in instead.'
            }), 400
        return jsonify({
            'error': f'Registration failed: Email or username already exists. Please try a different email.'
        }), 400
    except Exception as e:
        db.session.rollback()
        # Log the full error for debugging
        print(f"Registration error: {str(e)}")
        return jsonify({
            'error': f'Registration failed: {str(e)}. Please check all fields and try again.'
        }), 500

@app.route('/auth/send-code', methods=['POST'])
def send_verification_code():
    """Send verification code to email (2-step verification)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        # Verify user exists and password is correct
        result = db.session.execute(text("""
            SELECT user_id, password_hash, email, course_code, role
            FROM users WHERE email = :email
        """), {'email': email}).fetchone()

        if not result:
            return jsonify({'error': 'Invalid email or password'}), 401

        if not check_password_hash(result.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Generate 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = datetime.now() + timedelta(minutes=10)

        # Store code in database
        db.session.execute(text("""
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES (:email, :code, :expires_at)
        """), {
            'email': email,
            'code': code,
            'expires_at': expires_at
        })
        db.session.commit()

        # Send verification code via email (REQUIRED for 2-step verification)
        email_sent = send_verification_email(email, code)
        
        if email_sent:
            # Email sent successfully - real 2-step verification (like all professional 2FA systems)
            response_data = {
                'message': 'Verification code sent to your email. Please check your inbox (and spam folder).',
                'email_sent': True
            }
            # Security: Never include code in response when email is sent
        else:
            # Email failed - this should not happen in production
            # Only show code in dev/testing mode
            response_data = {
                'message': 'Verification code generated. Email not configured - code shown below for testing only.',
                'code': code,  # Only for dev/testing
                'email_sent': False,
                'warning': 'Email not configured. Set up email for proper 2-step verification. Run: python3 setup_email.py'
            }
            print(f"EMAIL NOT CONFIGURED")
            print(f"   Verification code for {email}: {code}")
            print(f"   To enable email: Run 'python3 setup_email.py' or create .env file")
            print(f"   See README_EMAIL.md for instructions")

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/auth/verify-code', methods=['POST'])
def verify_code():
    """Verify code and return auth token"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({'error': 'Missing email or code'}), 400

    try:
        # Check if code is valid
        result = db.session.execute(text("""
            SELECT code_id, expires_at, used
            FROM verification_codes
            WHERE email = :email AND code = :code AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
        """), {'email': email, 'code': code}).fetchone()

        if not result:
            return jsonify({'error': 'Invalid or expired code'}), 401

        # Convert expires_at string to datetime object (SQLite returns TIMESTAMP as string)
        expires_at = result.expires_at
        if isinstance(expires_at, str):
            # SQLite returns timestamps in format: 'YYYY-MM-DD HH:MM:SS'
            try:
                expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Try ISO format as fallback
                try:
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                except ValueError:
                    # Last resort: parse with dateutil if available
                    from dateutil import parser
                    expires_at = parser.parse(expires_at)
        elif not isinstance(expires_at, datetime):
            # If it's not a datetime, try to convert
            expires_at = datetime.strptime(str(expires_at), '%Y-%m-%d %H:%M:%S')
        
        if datetime.now() > expires_at:
            return jsonify({'error': 'Code has expired'}), 401

        # Mark code as used
        db.session.execute(text("""
            UPDATE verification_codes SET used = 1 WHERE code_id = :code_id
        """), {'code_id': result.code_id})

        # Get user info
        user_result = db.session.execute(text("""
            SELECT user_id, email, course_code, role
            FROM users WHERE email = :email
        """), {'email': email}).fetchone()
        
        if not user_result:
            db.session.rollback()
            return jsonify({'error': 'User not found'}), 404
        
        # Role is stored as-is (prof or ta)
        role_frontend = user_result.role

        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'user': {
                'user_id': user_result.user_id,
                'email': user_result.email,
                'course_code': user_result.course_code,
                'role': role_frontend
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    """Legacy endpoint - use /auth/register instead"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'error': 'Missing required fields'}), 400

    # Use pbkdf2 method instead of scrypt for Python 3.9 compatibility
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        result = db.session.execute(text("""
            INSERT INTO users (username, password_hash, role)
            VALUES (:username, :password_hash, :role)
            RETURNING user_id
        """), {'username': username, 'password_hash': hashed_password, 'role': role})
        user_id = result.fetchone()[0]
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        result = db.session.execute(text("""
            SELECT user_id, username, role, created_at
            FROM users WHERE user_id = :user_id
        """), {'user_id': user_id}).fetchone()

        if result:
            return jsonify(dict(result._mapping)), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    updates = []
    params = {'user_id': user_id}

    if username:
        updates.append("username = :username")
        params['username'] = username
    if password:
        updates.append("password_hash = :password_hash")
        params['password_hash'] = generate_password_hash(password, method='pbkdf2:sha256')
    if role:
        updates.append("role = :role")
        params['role'] = role

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = :user_id RETURNING user_id"

    try:
        result = db.session.execute(text(query), params).fetchone()
        if not result:
            db.session.rollback()
            return jsonify({'error': 'User not found'}), 404
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = db.session.execute(text("""
            DELETE FROM users WHERE user_id = :user_id RETURNING user_id
        """), {'user_id': user_id}).fetchone()
        if result:
            db.session.commit()
            return jsonify({'message': f'User {user_id} deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# student endpoints


def generate_random_rfid(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        # Fetch all students from the database
        result = db.session.execute(text("SELECT student_id, name, student_number, rfid_tag, photo_path FROM students")).fetchall()
        
        # Convert list of rows to list of dictionaries
        students = [dict(row._mapping) for row in result]
        return jsonify(students), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    name = data.get('name')
    rfid_tag = data.get('rfid_tag') or generate_random_rfid()
    photo_path = data.get('photo_path')

    if not name:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        result = db.session.execute(text("""
            INSERT INTO students (name, rfid_tag, photo_path)
            VALUES (:name, :rfid_tag, :photo_path)
            RETURNING student_id
        """), {'name': name, 'rfid_tag': rfid_tag, 'photo_path': photo_path})
        student_id = result.fetchone()[0]
        db.session.commit()
        return jsonify({'message': 'Student created successfully', 'student_id': student_id, 'rfid_tag': rfid_tag}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'RFID tag already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        result = db.session.execute(text("""
            SELECT student_id, name, rfid_tag, photo_path
            FROM students WHERE student_id = :student_id
        """), {'student_id': student_id}).fetchone()

        if result:
            return jsonify(dict(result._mapping)), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        result = db.session.execute(text("""
            DELETE FROM students WHERE student_id = :student_id RETURNING student_id
        """), {'student_id': student_id}).fetchone()
        if result:
            db.session.commit()
            return jsonify({'message': f'Student {student_id} deleted successfully'}), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    name = data.get('name')
    rfid_tag = data.get('rfid_tag')
    photo_path = data.get('photo_path')

    updates = []
    params = {'student_id': student_id}

    if name:
        updates.append("name = :name")
        params['name'] = name
    if rfid_tag:
        updates.append("rfid_tag = :rfid_tag")
        params['rfid_tag'] = rfid_tag
    if photo_path:
        updates.append("photo_path = :photo_path")
        params['photo_path'] = photo_path

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = :student_id RETURNING student_id"

    try:
        result = db.session.execute(text(query), params).fetchone()
        if not result:
            db.session.rollback()
            return jsonify({'error': 'Student not found'}), 404
        db.session.commit()
        return jsonify({'message': 'Student updated successfully'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'RFID tag already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# class endpoints


@app.route('/classes', methods=['GET'])
def get_all_classes():
    try:
        results = db.session.execute(text("""
            SELECT c.class_id, c.class_name, c.teacher_id, c.schedule, u.username as teacher_name,
                   COUNT(e.student_id) as student_count
            FROM classes c
            LEFT JOIN users u ON c.teacher_id = u.user_id
            LEFT JOIN enrollments e ON c.class_id = e.class_id
            GROUP BY c.class_id, c.class_name, c.teacher_id, c.schedule, u.username
        """)).fetchall()
        
        classes = [dict(row._mapping) for row in results]
        return jsonify(classes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes', methods=['POST'])
def create_class():
    data = request.get_json()
    class_name = data.get('class_name')
    teacher_id = data.get('teacher_id')
    schedule = data.get('schedule')

    if not class_name or not teacher_id:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        result = db.session.execute(text("""
            INSERT INTO classes (class_name, teacher_id, schedule)
            VALUES (:class_name, :teacher_id, :schedule)
            RETURNING class_id
        """), {'class_name': class_name, 'teacher_id': teacher_id, 'schedule': schedule})
        class_id = result.fetchone()[0]
        db.session.commit()
        return jsonify({'message': 'Class created successfully', 'class_id': class_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    try:
        result = db.session.execute(text("""
            SELECT class_id, class_name, teacher_id, schedule
            FROM classes WHERE class_id = :class_id
        """), {'class_id': class_id}).fetchone()

        if result:
            return jsonify(dict(result._mapping)), 200
        else:
            return jsonify({'error': 'Class not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    data = request.get_json()
    class_name = data.get('class_name')
    teacher_id = data.get('teacher_id')
    schedule = data.get('schedule')

    updates = []
    params = {'class_id': class_id}

    if class_name:
        updates.append("class_name = :class_name")
        params['class_name'] = class_name
    if teacher_id:
        updates.append("teacher_id = :teacher_id")
        params['teacher_id'] = teacher_id
    if schedule:
        updates.append("schedule = :schedule")
        params['schedule'] = schedule

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    query = f"UPDATE classes SET {', '.join(updates)} WHERE class_id = :class_id RETURNING class_id"

    try:
        result = db.session.execute(text(query), params).fetchone()
        if not result:
            db.session.rollback()
            return jsonify({'error': 'Class not found'}), 404
        db.session.commit()
        return jsonify({'message': 'Class updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    try:
        result = db.session.execute(text("""
            DELETE FROM classes WHERE class_id = :class_id RETURNING class_id
        """), {'class_id': class_id}).fetchone()
        if result:
            db.session.commit()
            return jsonify({'message': f'Class {class_id} deleted successfully'}), 200
        else:
            return jsonify({'error': 'Class not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        results = db.session.execute(text("""
            SELECT user_id, username, role, created_at
            FROM users
        """)).fetchall()
        
        users = [dict(row._mapping) for row in results]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<int:class_id>/roster', methods=['GET'])
def get_class_roster(class_id):
    try:
        results = db.session.execute(text("""
            SELECT s.student_id, s.name, s.rfid_tag
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            WHERE e.class_id = :class_id
        """), {'class_id': class_id}).fetchall()

        roster = [dict(row._mapping) for row in results]
        return jsonify(roster), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# attendance endpoints


@app.route('/attendance', methods=['POST'])
def log_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    method = data.get('method')

    if not student_id or not class_id or not method:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        db.session.execute(text("""
            INSERT INTO attendance_logs (student_id, class_id, method, status)
            VALUES (:student_id, :class_id, :method, 'Present')
        """), {'student_id': student_id, 'class_id': class_id, 'method': method})
        db.session.commit()
        return jsonify({'message': 'Attendance recorded'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/attendance', methods=['GET'])
def get_attendance():
    class_id = request.args.get('class_id')
    date = request.args.get('date')

    if not class_id or not date:
        return jsonify({'error': 'Missing class_id or date parameter'}), 400

    try:
        results = db.session.execute(text("""
            SELECT a.student_id, s.name, a.timestamp, a.method, a.status
            FROM attendance_logs a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.class_id = :class_id
              AND DATE(a.timestamp) = :date
        """), {'class_id': class_id, 'date': date}).fetchall()

        logs = [dict(row._mapping) for row in results]
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/recent', methods=['GET'])
def get_recent_attendance():
    """Get recent attendance logs (for Tap Monitor)"""
    limit = request.args.get('limit', 20, type=int)
    try:
        results = db.session.execute(text("""
            SELECT a.log_id, a.student_id, s.name, a.timestamp, a.method, a.status, s.photo_path
            FROM attendance_logs a
            JOIN students s ON a.student_id = s.student_id
            ORDER BY a.timestamp DESC
            LIMIT :limit
        """), {'limit': limit}).fetchall()

        logs = [dict(row._mapping) for row in results]
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/statistics', methods=['GET'])
def get_attendance_statistics():
    """Get attendance statistics for dashboard"""
    class_id = request.args.get('class_id', type=int)
    
    try:
        if class_id:
            # Get stats for specific class
            results = db.session.execute(text("""
                SELECT 
                    DATE(a.timestamp) as date,
                    COUNT(DISTINCT a.student_id) as count
                FROM attendance_logs a
                WHERE a.class_id = :class_id
                GROUP BY DATE(a.timestamp)
                ORDER BY date DESC
                LIMIT 10
            """), {'class_id': class_id}).fetchall()
        else:
            # Get overall stats
            results = db.session.execute(text("""
                SELECT 
                    DATE(a.timestamp) as date,
                    COUNT(DISTINCT a.student_id) as count
                FROM attendance_logs a
                GROUP BY DATE(a.timestamp)
                ORDER BY date DESC
                LIMIT 10
            """)).fetchall()
        
        stats = [dict(row._mapping) for row in results]
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/student-stats', methods=['GET'])
def get_student_attendance_stats():
    """Get attendance statistics per student"""
    class_id = request.args.get('class_id', type=int)
    
    try:
        if class_id:
            results = db.session.execute(text("""
                SELECT 
                    s.student_id,
                    s.name,
                    COUNT(a.log_id) as total_attendance,
                    COUNT(DISTINCT DATE(a.timestamp)) as days_present
                FROM students s
                LEFT JOIN attendance_logs a ON s.student_id = a.student_id AND a.class_id = :class_id
                GROUP BY s.student_id, s.name
                ORDER BY s.name
            """), {'class_id': class_id}).fetchall()
        else:
            results = db.session.execute(text("""
                SELECT 
                    s.student_id,
                    s.name,
                    COUNT(a.log_id) as total_attendance,
                    COUNT(DISTINCT DATE(a.timestamp)) as days_present
                FROM students s
                LEFT JOIN attendance_logs a ON s.student_id = a.student_id
                GROUP BY s.student_id, s.name
                ORDER BY s.name
            """)).fetchall()
        
        stats = [dict(row._mapping) for row in results]
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# RFID & FACE endpoints


@app.route('/rfid/scan', methods=['POST'])
def rfid_scan():
    """Scan RFID card - matches ID to student and automatically marks attendance"""
    data = request.get_json()
    rfid_id = data.get('rfid_id') or data.get('rfid_tag')  # Accept both field names
    course_code = data.get('course_code')  # Optional - for filtering by course

    if not rfid_id:
        return jsonify({'error': 'Missing RFID ID'}), 400

    try:
        # Find student by RFID ID
        result = db.session.execute(text("""
            SELECT student_id, name, student_number, rfid_tag, photo_path
            FROM students WHERE rfid_tag = :rfid_id
        """), {'rfid_id': rfid_id}).fetchone()

        if not result:
            return jsonify({
                'error': 'RFID card not recognized',
                'rfid_id': rfid_id,
                'message': 'This card is not registered in the system'
            }), 404

        # Automatically log attendance
        # For now, we'll use a default class_id of 1 or get from course_code
        # In the future, you can link course_code to class_id
        class_id = 1  # Default - can be improved later
        
        # Check if already logged today (prevent duplicates)
        today = datetime.now().date()
        existing = db.session.execute(text("""
            SELECT log_id FROM attendance_logs
            WHERE student_id = :student_id
            AND DATE(timestamp) = :date
            AND class_id = :class_id
        """), {
            'student_id': result.student_id,
            'date': today,
            'class_id': class_id
        }).fetchone()

        if existing:
            return jsonify({
                'student_id': result.student_id,
                'name': result.name,
                'student_number': result.student_number,
                'status': 'Already marked present today',
                'timestamp': datetime.now().isoformat()
            }), 200

        # Log attendance
        db.session.execute(text("""
            INSERT INTO attendance_logs (student_id, class_id, method, status)
            VALUES (:student_id, :class_id, 'RFID', 'Present')
        """), {
            'student_id': result.student_id,
            'class_id': class_id
        })
        db.session.commit()

        return jsonify({
            'student_id': result.student_id,
            'name': result.name,
            'student_number': result.student_number,
            'photo_path': result.photo_path,
            'status': 'Present',
            'message': 'Attendance marked successfully',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/face/verify', methods=['POST'])
def face_verify():
    data = request.get_json()
    student_id = data.get('student_id')
    photo_data = data.get('photo_data')

    if not student_id or not photo_data:
        return jsonify({'error': 'Missing fields'}), 400

    # Here you would integrate a real face recognition model
    return jsonify({
        'student_id': student_id,
        'status': 'Verified'
    }), 200


# Comments endpoints

@app.route('/comments', methods=['POST'])
def create_comment():
    """Create a comment for a photo/attendance log"""
    data = request.get_json()
    photo_id = data.get('photoId')  # This is actually log_id from attendance_logs
    comment_text = data.get('comment')

    if not photo_id or not comment_text or not comment_text.strip():
        return jsonify({'error': 'Missing photoId or comment'}), 400

    try:
        # Verify the log exists and get student_id
        log_result = db.session.execute(text("""
            SELECT student_id FROM attendance_logs WHERE log_id = :log_id
        """), {'log_id': photo_id}).fetchone()

        if not log_result:
            return jsonify({'error': 'Attendance log not found'}), 404

        student_id = log_result[0]

        # Insert comment
        db.session.execute(text("""
            INSERT INTO comments (log_id, student_id, comment_text)
            VALUES (:log_id, :student_id, :comment_text)
        """), {
            'log_id': photo_id,
            'student_id': student_id,
            'comment_text': comment_text.strip()
        })
        db.session.commit()

        return jsonify({
            'message': 'Comment saved successfully',
            'log_id': photo_id,
            'student_id': student_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/comments', methods=['GET'])
def get_comments():
    """Get all comments, optionally filtered by log_id or student_id"""
    log_id = request.args.get('log_id', type=int)
    student_id = request.args.get('student_id', type=int)

    try:
        if log_id:
            # Get comments for a specific log
            results = db.session.execute(text("""
                SELECT comment_id, log_id, student_id, comment_text, created_at
                FROM comments
                WHERE log_id = :log_id
                ORDER BY created_at DESC
            """), {'log_id': log_id}).fetchall()
        elif student_id:
            # Get comments for a specific student
            results = db.session.execute(text("""
                SELECT comment_id, log_id, student_id, comment_text, created_at
                FROM comments
                WHERE student_id = :student_id
                ORDER BY created_at DESC
            """), {'student_id': student_id}).fetchall()
        else:
            # Get all comments
            results = db.session.execute(text("""
                SELECT comment_id, log_id, student_id, comment_text, created_at
                FROM comments
                ORDER BY created_at DESC
            """)).fetchall()

        comments = [dict(row._mapping) for row in results]
        return jsonify(comments), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/comments/<int:log_id>', methods=['GET'])
def get_comments_by_log(log_id):
    """Get comments for a specific attendance log"""
    try:
        results = db.session.execute(text("""
            SELECT comment_id, log_id, student_id, comment_text, created_at
            FROM comments
            WHERE log_id = :log_id
            ORDER BY created_at DESC
        """), {'log_id': log_id}).fetchall()

        comments = [dict(row._mapping) for row in results]
        return jsonify(comments), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

# Main entry point

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
