import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Create a client user
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/signup/client",
        json=signup_data
    )
    print("Signup Response:", response.json())
    
    # 2. Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data
    )
    print("Login Response:", response.json())
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. List files
        response = requests.get(
            f"{BASE_URL}/files/files",
            headers=headers
        )
        print("Files List Response:", response.json())

if __name__ == "__main__":
    test_api() 