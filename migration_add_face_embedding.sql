-- Add face_embedding column to students (for Jetson face verification)
-- Stores JSON array of floats (e.g. 128-d or 512-d embedding from face model)
ALTER TABLE students ADD COLUMN IF NOT EXISTS face_embedding TEXT;
