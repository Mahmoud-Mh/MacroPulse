import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = 'http://localhost:8000'

def test_auth():
    """Test authentication flow"""
    try:
        # Step 1: Get token
        auth_url = f"{BASE_URL}/api/v1/auth/token/"
        credentials = {
            "username": "test1",
            "password": "test1"
        }
        
        response = requests.post(auth_url, json=credentials)
        if response.status_code != 200:
            logger.error(f"Authentication failed: {response.text}")
            return
            
        token = response.json()['access']
        logger.info("Successfully obtained token")
        
        # Step 2: Test protected endpoint
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test indicators endpoint
        indicators_url = f"{BASE_URL}/api/v1/indicators/"
        response = requests.get(indicators_url, headers=headers)
        logger.info(f"Indicators response: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Indicators data: {response.json()}")
        else:
            logger.error(f"Failed to get indicators: {response.text}")
            
        # Test docs endpoint
        docs_url = f"{BASE_URL}/api/docs/"
        response = requests.get(docs_url, headers=headers)
        logger.info(f"Docs response: {response.status_code}")
        if response.status_code == 200:
            logger.info("Successfully accessed API docs")
        else:
            logger.error(f"Failed to access docs: {response.text}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    test_auth() 