# NOVA-Server

Backend API and database for [NOVA](https://github.com/NOVA-Attendance) (Next-gen Online Verification for Attendance).

**Repos:**
- [NOVA](https://github.com/NOVA-Attendance/NOVA) – Jetson / embedded (RFID, camera, AI)
- [NOVA-Server](https://github.com/NOVA-Attendance/NOVA-Server) – this repo (Flask API, PostgreSQL/SQLite)
- [NOVA-UI](https://github.com/NOVA-Attendance/NOVA-UI) – React dashboard

---

## Quick run

```bash
# Optional: use SQLite for local dev (default is PostgreSQL)
echo "DATABASE_URI=sqlite:///nova.db" >> .env

# Create/update all required tables and columns used by app.py
python3 create_tables.py

# Seed students (with team RFID card IDs)
python3 seed_database.py

# Install deps (face embedding requires same model as Jetson - deepface)
pip install flask flask-cors flask-sqlalchemy py-dotenv deepface

# Start backend
python3 app.py
```

Backend: **http://localhost:5001**

---

## Key endpoints (for Jetson + UI)

| Endpoint | Purpose |
|----------|--------|
| `POST /rfid/scan` | Card tap → match student, mark attendance, return `face_embedding` if stored |
| `GET /rfid/face-embedding?rfid_id=X` | Get stored face embedding for a card (Jetson face check) |
| `POST /face/enroll` | Upload image → compute embedding (DeepFace, same as [NOVA](https://github.com/NOVA-Attendance/NOVA)), store for student |
| `GET /students`, `GET /attendance/recent` | Used by NOVA-UI |

Face embedding uses **DeepFace (Facenet512)** so it matches the Jetson/NOVA repo; coordinate with Faris if the model name changes.
