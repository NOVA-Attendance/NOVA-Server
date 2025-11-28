import pytest
import uuid
from app import app 

# fixtures

@pytest.fixture
def app_fixture():
    app.config.update({
        "TESTING": True  # enable testing mode
    })
    return app

@pytest.fixture
def client(app_fixture):
    return app_fixture.test_client()


# user endpoint tests

def test_create_user(client):
    username = f"user_{uuid.uuid4().hex[:6]}"
    resp = client.post('/users', json={
        "username": username,
        "password": "password123",
        "role": "teacher"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "user_id" in data

def test_get_user(client):
    username = f"user_{uuid.uuid4().hex[:6]}"
    create_resp = client.post('/users', json={
        "username": username,
        "password": "password123",
        "role": "teacher"
    })
    user_id = create_resp.get_json()['user_id']

    get_resp = client.get(f'/users/{user_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['username'] == username

def test_update_user(client):
    username = f"user_{uuid.uuid4().hex[:6]}"
    create_resp = client.post('/users', json={
        "username": username,
        "password": "password123",
        "role": "teacher"
    })
    user_id = create_resp.get_json()['user_id']

    new_username = f"updated_{uuid.uuid4().hex[:6]}"
    update_resp = client.put(f'/users/{user_id}', json={"username": new_username})
    assert update_resp.status_code == 200

    get_resp = client.get(f'/users/{user_id}')
    data = get_resp.get_json()
    assert data['username'] == new_username

def test_delete_user(client):
    username = f"user_{uuid.uuid4().hex[:6]}"
    create_resp = client.post('/users', json={
        "username": username,
        "password": "password123",
        "role": "teacher"
    })
    user_id = create_resp.get_json()['user_id']

    delete_resp = client.delete(f'/users/{user_id}')
    assert delete_resp.status_code == 200

    get_resp = client.get(f'/users/{user_id}')
    assert get_resp.status_code == 404


# student enpoint tests

def test_create_student(client):
    name = f"Student_{uuid.uuid4().hex[:6]}"
    resp = client.post('/students', json={"name": name})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "student_id" in data
    assert "rfid_tag" in data

def test_get_student(client):
    name = f"Student_{uuid.uuid4().hex[:6]}"
    student_resp = client.post('/students', json={"name": name})
    student_id = student_resp.get_json()['student_id']

    get_resp = client.get(f'/students/{student_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['name'] == name

def test_update_student(client):
    student_resp = client.post('/students', json={"name": "Original"})
    student_id = student_resp.get_json()['student_id']

    new_name = "UpdatedName"
    update_resp = client.put(f'/students/{student_id}', json={"name": new_name})
    assert update_resp.status_code == 200

    get_resp = client.get(f'/students/{student_id}')
    data = get_resp.get_json()
    assert data['name'] == new_name


# Class endpoint tests

def test_create_class(client):
    username = f"user_{uuid.uuid4().hex[:6]}"
    user_resp = client.post('/users', json={"username": username, "password": "pass", "role": "teacher"})
    teacher_id = user_resp.get_json()['user_id']

    class_name = f"Class_{uuid.uuid4().hex[:6]}"
    resp = client.post('/classes', json={"class_name": class_name, "teacher_id": teacher_id})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "class_id" in data

def test_get_class(client):
    user_resp = client.post('/users', json={"username": f"user_{uuid.uuid4().hex[:6]}", "password": "pass", "role": "teacher"})
    teacher_id = user_resp.get_json()['user_id']

    class_resp = client.post('/classes', json={"class_name": "Math", "teacher_id": teacher_id})
    class_id = class_resp.get_json()['class_id']

    get_resp = client.get(f'/classes/{class_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['class_name'] == "Math"


# attendance endpoint tests

def test_log_attendance(client):
    student_resp = client.post('/students', json={"name": "Student_Att"})
    student_id = student_resp.get_json()['student_id']

    user_resp = client.post('/users', json={"username": f"user_{uuid.uuid4().hex[:6]}", "password": "pass", "role": "teacher"})
    teacher_id = user_resp.get_json()['user_id']
    class_resp = client.post('/classes', json={"class_name": "History", "teacher_id": teacher_id})
    class_id = class_resp.get_json()['class_id']

    resp = client.post('/attendance', json={"student_id": student_id, "class_id": class_id, "method": "manual"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['message'] == "Attendance recorded"


# RFID & face tests

def test_rfid_scan_success(client):
    student_resp = client.post('/students', json={"name": f"Student_{uuid.uuid4().hex[:6]}"})
    student_data = student_resp.get_json()
    rfid_tag = student_data['rfid_tag']
    student_id = student_data['student_id']

    resp = client.post('/rfid/scan', json={"rfid_tag": rfid_tag})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['student_id'] == student_id
    assert data['status'] == "Verified"

def test_rfid_scan_failure(client):
    resp = client.post('/rfid/scan', json={"rfid_tag": "INVALID123"})
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data

def test_face_verify_success(client):
    student_resp = client.post('/students', json={"name": f"Student_{uuid.uuid4().hex[:6]}"})
    student_id = student_resp.get_json()['student_id']

    resp = client.post('/face/verify', json={"student_id": student_id, "photo_data": "dummy_photo_data"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['student_id'] == student_id
    assert data['status'] == "Verified"

def test_face_verify_failure_missing_fields(client):
    resp = client.post('/face/verify', json={"photo_data": "dummy_photo_data"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

    resp = client.post('/face/verify', json={"student_id": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
