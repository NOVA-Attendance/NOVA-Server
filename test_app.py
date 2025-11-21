import pytest
from app import app, db
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# =========================================================
# USER TESTS
# =========================================================

def test_add_user(client):
    response = client.post('/users', json={
        "username": "test_user_unique",
        "password": "password123",
        "role": "teacher"
    })
    assert response.status_code == 201

def test_get_user(client):
    response = client.get('/users/1')  # Adjust ID if needed
    assert response.status_code == 200

def test_update_user(client):
    response = client.put('/users/1', json={
        "username": "updated_user"
    })
    assert response.status_code == 200

# =========================================================
# STUDENT TESTS
# =========================================================

def test_add_student(client):
    response = client.post('/students', json={
        "name": "Test Student",
        "rfid_tag": "RFID999_UNIQUE",
        "photo_path": "/photos/test.jpg"
    })
    assert response.status_code == 201

def test_get_student(client):
    response = client.get('/students/1')  # Adjust ID if needed
    assert response.status_code == 200

def test_update_student(client):
    response = client.put('/students/1', json={
        "name": "Updated Student"
    })
    assert response.status_code == 200

# =========================================================
# CLASS TESTS
# =========================================================

def test_add_class(client):
    response = client.post('/classes', json={
        "class_name": "Test Class",
        "teacher_id": 1,
        "schedule": "Mon 9AM"
    })
    assert response.status_code == 201

def test_get_class(client):
    response = client.get('/classes/1')  # Adjust ID if needed
    assert response.status_code == 200

def test_update_class(client):
    response = client.put('/classes/1', json={
        "class_name": "Updated Class"
    })
    assert response.status_code == 200

# =========================================================
# ATTENDANCE TESTS
# =========================================================

def test_log_attendance(client):
    response = client.post('/attendance', json={
        "student_id": 1,
        "class_id": 1,
        "method": "RFID",
        "timestamp": datetime.utcnow().isoformat()
    })
    assert response.status_code == 201

def test_get_attendance(client):
    response = client.get('/attendance', query_string={
        "class_id": 1,
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    })
    assert response.status_code == 200

