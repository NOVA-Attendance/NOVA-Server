from app import app, db
from sqlalchemy import text

# The team data with mock RFID ID values
# These are the actual RFID card ID values that will be read by the scanner
# For now using mock values - replace with real values when you have them
team_members = [
    {
        "name": "Christopher King",
        "student_number": "300226522",
        "email": "cking028@uottawa.ca",
        "rfid_tag": "A1B2C3D4",  # Mock RFID ID - replace with actual card ID
        "photo_path": "photos/christopher.jpg"
    },
    {
        "name": "Denzel Shaka",
        "student_number": "300185848",
        "email": "dshak053@uottawa.ca",
        "rfid_tag": "E5F6G7H8",  # Mock RFID ID - replace with actual card ID
        "photo_path": "photos/denzel.jpg"
    },
    {
        "name": "Eknoor Goraya",
        "student_number": "300278785",
        "email": "egora090@uottawa.ca",
        "rfid_tag": "I9J0K1L2",  # Mock RFID ID - replace with actual card ID
        "photo_path": "photos/eknoor.jpg"
    },
    {
        "name": "Fareis Canoe",
        "student_number": "300299663",
        "email": "fcano068@uottawa.ca",
        "rfid_tag": "M3N4O5P6",  # Mock RFID ID - replace with actual card ID
        "photo_path": "photos/fareis.jpg"
    },
    {
        "name": "Manan Dayalani",
        "student_number": "300256144",
        "email": "mdaya049@uottawa.ca",
        "rfid_tag": "Q7R8S9T0",  # Mock RFID ID - replace with actual card ID
        "photo_path": "photos/manan.jpg"
    },
    {
        "name": "Rayane Chemsi",
        "student_number": "300324494",
        "email": "rchem099@uottawa.ca",
        "rfid_tag": "U1V2W3X4",  # Mock RFID ID - replace with actual card ID
        "photo_path": None # No photo for Rayane based on your design
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