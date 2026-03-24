from app import app, db
from sqlalchemy import text

# Team members with RFID card IDs from Jetson taps (UOttawa student cards).
# Update rfid_tag with the number shown when each person taps (e.g. "RFID read: 584192787859" -> "584192787859").
# Then run: python3 seed_database.py
team_members = [
    {
        "name": "Christopher King",
        "student_number": "300226522",
        "email": "cking028@uottawa.ca",
        "rfid_tag": "584192787859",  # From Jetson tap (Chris's UOttawa card)
        "photo_path": "photos/christopher.jpg"
    },
    {
        "name": "Denzel Shaka",
        "student_number": "300185848",
        "email": "dshak053@uottawa.ca",
        "rfid_tag": None,  # Add card ID after Denzel taps on Jetson
        "photo_path": "photos/denzel.jpg"
    },
    {
        "name": "Eknoor Goraya",
        "student_number": "300278785",
        "email": "egora090@uottawa.ca",
        "rfid_tag": "584184173193",
        "photo_path": "photos/eknoor.jpg"
    },
    {
        "name": "Fareis Canoe",
        "student_number": "300299663",
        "email": "fcano068@uottawa.ca",
        "rfid_tag": "584187104259",
        "photo_path": "photos/fareis.jpg"
    },
    {
        "name": "Manan Dayalani",
        "student_number": "300256144",
        "email": "mdaya049@uottawa.ca",
        "rfid_tag": "584185154983",
        "photo_path": "photos/manan.jpg"
    },
    {
        "name": "Rayane Chemsi",
        "student_number": "300324494",
        "email": "rchem099@uottawa.ca",
        "rfid_tag": None,  # Add card ID after Rayane taps on Jetson
        "photo_path": None
    }
]

with app.app_context():
    print(" Seeding database...")
    
    try:
        # Clear existing students to avoid duplicates
        db.session.execute(text("DELETE FROM students"))
        
        # Add each member with student_number
        for member in team_members:
            db.session.execute(text("""
                INSERT INTO students (name, student_number, rfid_tag, photo_path)
                VALUES (:name, :student_number, :rfid_tag, :photo_path)
            """), {
                'name': member['name'],
                'student_number': member['student_number'],
                'rfid_tag': member['rfid_tag'],
                'photo_path': member['photo_path']
            })
        
        db.session.commit()
        print(f" Success! Added {len(team_members)} team members to the database.")
        
    except Exception as e:
        db.session.rollback()
        print(f" Error: {e}")