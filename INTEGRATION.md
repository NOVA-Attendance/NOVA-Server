# NOVA Backend Integration

## How the Backend Integrates with the Original PostgreSQL Schema and Frontend

### Original Backend (Denzel's PostgreSQL Work)

The original `novadatabase.sql` defines the core schema:

- **users** – `user_id`, `username`, `password_hash`, `role` (admin/teacher)
- **students** – `student_id`, `name`, `rfid_tag`, `photo_path`
- **classes** – `class_id`, `class_name`, `teacher_id`, `schedule`
- **enrollments** – `enrollment_id`, `student_id`, `class_id`
- **attendance_logs** – `log_id`, `student_id`, `class_id`, `method`, `timestamp`, `status`

### Extensions Added (Auth, Comments, etc.)

1. **2-step verification**
   - `users.email`, `users.course_code`
   - `verification_codes` table for email verification codes
   - Roles extended to `prof` and `ta`

2. **Comments**
   - `comments` table linked to `attendance_logs` and `students`

3. **Students**
   - `students.student_number`, `students.email` (optional)

### Database Choice

- **Development:** SQLite (`nova.db`) – used by default in `app.py`
- **Production:** PostgreSQL – uncomment the PostgreSQL URI in `app.py` and use `novadatabase_updated.sql`

### Frontend Integration

The frontend (NOVA-UI) talks to these backend APIs:

| Frontend Feature | Backend Endpoint | Notes |
|------------------|------------------|-------|
| Login / 2-step auth | `POST /auth/login`, `POST /auth/verify` | Uses `users`, `verification_codes` |
| Registration | `POST /auth/register` | Uses `users` (email, course_code) |
| Students list | `GET /students` | Uses `students` |
| Attendance | `GET /attendance`, `POST /attendance` | Uses `attendance_logs` |
| Comments | `GET /comments`, `POST /comments` | Uses `comments` |
| Classes | `GET /classes` | Uses `classes` |

### Updated Database Files

- **novadatabase_updated.sql** – Full schema including all new tables and columns (for fresh setup or reference).
- **migration_add_auth_and_comments.sql** – Run this on top of `novadatabase.sql` to add auth and comments tables/columns.
