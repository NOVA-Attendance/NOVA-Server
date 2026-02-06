from app import app, db

with app.app_context():
    # This creates the file 'nova.db' and all the empty tables
    db.create_all()
    print(" Success! Database created successfully.")