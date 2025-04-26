import asyncio
import websockets
import json
import requests

async def test_websocket():
    # First get a token through the REST API
    login_data = {
        "username": "testuser",  # Replace with your test user
        "password": "testpass"   # Replace with your test password
    }
    
    try:
        # Get the token
        response = requests.post('http://localhost:8000/auth/token/', data=login_data)
        if response.status_code != 200:
            print("Failed to get token:", response.text)
            return
            
        token = response.json()['access']
        
        # Test authenticated connection
        async with websockets.connect(
            f'ws://localhost:8000/ws/economic_data/?token={token}'
        ) as websocket:
            print("Connected with authentication!")
            
            # Send a test message
            await websocket.send(json.dumps({
                'message': 'Test message with auth'
            }))
            
            # Wait for response
            response = await websocket.recv()
            print("Received:", response)
            
            # Keep connection open briefly
            await asyncio.sleep(2)
            
        # Test connection without token (should fail)
        try:
            async with websockets.connect(
                'ws://localhost:8000/ws/economic_data/'
            ) as websocket:
                print("Warning: Connected without authentication!")
        except websockets.exceptions.ConnectionClosed:
            print("Successfully rejected unauthenticated connection")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 