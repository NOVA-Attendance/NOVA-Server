--
-- Migration: Add auth (2-step verification) and comments to existing NOVA PostgreSQL database
-- Run this AFTER loading novadatabase.sql
--

-- Users: add email and course_code for 2-step verification and registration
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(100);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS course_code VARCHAR(50);

-- Allow prof and ta roles (drop old constraint)
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;

-- Students: add student_number and email
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS student_number VARCHAR(50);
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Verification codes for 2-step email auth
CREATE TABLE IF NOT EXISTS public.verification_codes (
    code_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments on attendance logs
CREATE TABLE IF NOT EXISTS public.comments (
    comment_id SERIAL PRIMARY KEY,
    log_id INTEGER REFERENCES public.attendance_logs(log_id),
    student_id INTEGER REFERENCES public.students(student_id),
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
