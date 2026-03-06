-- Purpose: Store face embeddings for Jetson face verification.
-- Backend computes embedding (same model as NOVA/Jetson - DeepFace/Facenet512) and stores here;
-- Jetson requests via GET /rfid/face-embedding and compares live camera to this.
ALTER TABLE students ADD COLUMN IF NOT EXISTS face_embedding TEXT;
