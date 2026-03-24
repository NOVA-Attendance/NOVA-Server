#!/usr/bin/env python3
"""
Test script to verify registration endpoint works
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_registration():
    """Test the registration endpoint"""
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "test123",
        "course_code": "TEST101",
        "role": "prof"
    }
    
    print("Testing registration endpoint...")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\nRegistration successful!")
        else:
            print(f"\nRegistration failed: {response.json().get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("\nCannot connect to server. Make sure the backend is running:")
        print("   python3 app.py")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_registration()
