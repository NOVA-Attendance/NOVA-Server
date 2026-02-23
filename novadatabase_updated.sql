--
-- NOVA PostgreSQL Database - Updated Schema
-- Includes original schema (Denzel) + auth/2-step verification + comments
-- Run this to create a fresh database, or use the migration section at the bottom
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- ============================================================
-- ORIGINAL SCHEMA (from novadatabase.sql)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extended users table: email, course_code for 2-step auth and registration
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(100);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS course_code VARCHAR(50);

-- Drop old role constraint if exists (allows admin, teacher, prof, ta)
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;

CREATE TABLE IF NOT EXISTS public.students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rfid_tag VARCHAR(50) UNIQUE,
    photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.students ADD COLUMN IF NOT EXISTS student_number VARCHAR(50);
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS email VARCHAR(255);

CREATE TABLE IF NOT EXISTS public.classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    teacher_id INTEGER REFERENCES public.users(user_id),
    schedule VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS public.enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES public.students(student_id),
    class_id INTEGER REFERENCES public.classes(class_id)
);

CREATE TABLE IF NOT EXISTS public.attendance_logs (
    log_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES public.students(student_id),
    class_id INTEGER REFERENCES public.classes(class_id),
    method VARCHAR(20) CHECK (method IN ('RFID', 'FACE')),
    "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) CHECK (status IN ('Present', 'Absent'))
);

-- ============================================================
-- NEW TABLES (2-step auth, comments)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.verification_codes (
    code_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.comments (
    comment_id SERIAL PRIMARY KEY,
    log_id INTEGER REFERENCES public.attendance_logs(log_id),
    student_id INTEGER REFERENCES public.students(student_id),
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- MIGRATION: If you already have novadatabase.sql loaded,
-- run only these statements to add new schema:
-- ============================================================
-- ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(100);
-- ALTER TABLE public.users ADD COLUMN IF NOT EXISTS course_code VARCHAR(50);
-- ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;
-- ALTER TABLE public.students ADD COLUMN IF NOT EXISTS student_number VARCHAR(50);
-- ALTER TABLE public.students ADD COLUMN IF NOT EXISTS email VARCHAR(255);
-- CREATE TABLE IF NOT EXISTS public.verification_codes (...);
-- CREATE TABLE IF NOT EXISTS public.comments (...);
