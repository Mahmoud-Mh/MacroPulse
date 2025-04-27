import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_registration():
    print("\nTesting Registration...")
    url = f"{BASE_URL}/api/v1/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_authentication():
    print("\nTesting Authentication...")
    url = f"{BASE_URL}/api/v1/auth/token/"
    data = {
        "username": "test1",
        "password": "test1"  # Using the password you entered in the UI
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response

def test_indicators_v1(token):
    print("\nTesting v1 Indicators...")
    url = f"{BASE_URL}/api/v1/indicators/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response

def test_indicators_v2(token):
    print("\nTesting v2 Indicators...")
    url = f"{BASE_URL}/api/v2/indicators/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response

if __name__ == "__main__":
    # Test authentication first (skip registration since user exists)
    auth_response = test_authentication()
    if auth_response.status_code == 200:
        token = auth_response.json().get("access")
        
        # Test v1 indicators
        test_indicators_v1(token)
        
        # Test v2 indicators
        test_indicators_v2(token) 