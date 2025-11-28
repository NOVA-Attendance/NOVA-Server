from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import string

app = Flask(__name__)

# Database Setup

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:group9@localhost/attendance_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Endpoints

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'error': 'Missing required fields'}), 400

    hashed_password = generate_password_hash(password)

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
        params['password_hash'] = generate_password_hash(password)
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


# RFID & FACE endpoints


@app.route('/rfid/scan', methods=['POST'])
def rfid_scan():
    data = request.get_json()
    rfid_tag = data.get('rfid_tag')

    if not rfid_tag:
        return jsonify({'error': 'Missing RFID tag'}), 400

    try:
        result = db.session.execute(text("""
            SELECT student_id, name FROM students WHERE rfid_tag = :rfid_tag
        """), {'rfid_tag': rfid_tag}).fetchone()

        if result:
            return jsonify({
                'student_id': result.student_id,
                'status': 'Verified'
            }), 200
        else:
            return jsonify({'error': 'RFID tag not recognized'}), 404
    except Exception as e:
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


# Main entry point

if __name__ == '__main__':
    app.run(debug=True)
