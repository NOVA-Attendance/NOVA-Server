#!/usr/bin/env python3
"""Test the /students API endpoint"""

from app import app

with app.test_client() as client:
    # Test the /students endpoint
    response = client.get('/students')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.content_type}")
    print(f"\nResponse Data:")
    print(response.get_data(as_text=True))
    
    if response.status_code == 200:
        import json
        data = json.loads(response.get_data(as_text=True))
        print(f"\nSuccess! Found {len(data)} students")
        for student in data:
            print(f"  - {student.get('name')} (ID: {student.get('student_id')})")
    else:
        print(f"\nError: Status {response.status_code}")
