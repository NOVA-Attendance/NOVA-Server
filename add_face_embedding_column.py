"""Add face_embedding column to students table. Run once: python3 add_face_embedding_column.py"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE students ADD COLUMN face_embedding TEXT"))
        db.session.commit()
        print("Added face_embedding column to students.")
    except Exception as e:
        db.session.rollback()
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("face_embedding column already exists.")
        else:
            print(f"Error: {e}")
