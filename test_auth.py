import requests
import json
import time
from datetime import datetime
import sys

BASE_URL = 'http://127.0.0.1:8000'

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_auth_flow():
    try:
        # Generate unique username with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        username = f'testuser_{timestamp}'
        
        print("\n1. Testing Registration...")
        registration_data = {
            'username': username,
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': f'{username}@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = requests.post(f'{BASE_URL}/api/auth/register/', data=registration_data)
        print_response(response)
        if response.status_code != 201:
            print("Registration failed!")
            return
        print("Registration successful!")

        # Add a small delay to ensure database operations complete
        time.sleep(1)

        print("\n2. Testing Token Obtain...")
        token_data = {
            'username': username,
            'password': 'testpass123'
        }
        response = requests.post(f'{BASE_URL}/api/auth/token/', data=token_data)
        print_response(response)
        if response.status_code != 200:
            print("Token obtain failed!")
            return
        print("Token obtain successful!")
        
        tokens = response.json()
        access_token = tokens['access']
        refresh_token = tokens['refresh']

        print("\n3. Testing Profile Access...")
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'{BASE_URL}/api/auth/profile/', headers=headers)
        print_response(response)
        if response.status_code != 200:
            print("Profile access failed!")
            return
        print("Profile access successful!")

        print("\n4. Testing Token Refresh...")
        refresh_data = {'refresh': refresh_token}
        response = requests.post(f'{BASE_URL}/api/auth/token/refresh/', data=refresh_data)
        print_response(response)
        if response.status_code != 200:
            print("Token refresh failed!")
            return
        print("Token refresh successful!")

        print("\n5. Testing Logout...")
        headers = {'Authorization': f'Bearer {access_token}'}
        logout_data = {'refresh': refresh_token}
        response = requests.post(f'{BASE_URL}/api/auth/logout/', headers=headers, json=logout_data)
        print_response(response)
        if response.status_code != 204:
            print("Logout failed!")
            return
        print("Logout successful!")

        print("\n6. Testing Post-Logout Access (should fail)...")
        response = requests.get(f'{BASE_URL}/api/auth/profile/', headers=headers)
        print_response(response)
        if response.status_code != 401:
            print("Post-logout access test failed - endpoint should return 401!")
            return
        print("Post-logout access test successful - properly denied access!")

        print("All tests completed successfully!")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Django server is running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_auth_flow() 