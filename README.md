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

# Add face_embedding column (once)
python3 add_face_embedding_column.py

# Seed students (with team RFID card IDs)
python3 seed_database.py

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
| `POST /face/enroll` | Upload image → compute embedding, store for student (by `student_id` or `rfid_id`) |
| `GET /students`, `GET /attendance/recent` | Used by NOVA-UI |

See **JETSON_RFID_INTEGRATION.md** for Jetson integration and **INTEGRATION.md** for schema/frontend mapping.
