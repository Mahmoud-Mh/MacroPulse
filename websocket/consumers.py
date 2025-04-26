from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EconomicDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        user = self.scope["user"]
        if user.is_anonymous:
            logger.warning("Anonymous user attempted to connect")
            await self.close(code=4401)
            return
            
        logger.info(f"WebSocket connection established for user: {user.username}")
        await self.accept()
        await self.send_welcome_message(user.username)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        user = self.scope["user"]
        logger.info(f"WebSocket connection closed for user: {user.username if not user.is_anonymous else 'anonymous'}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            logger.debug(f"Received message from {self.scope['user'].username}: {data}")
            await self.handle_message(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error("Internal server error")

    async def send_welcome_message(self, username):
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': f'Welcome {username}!',
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_message(self, data):
        response = {
            'type': 'echo',
            'content': data,
            'timestamp': datetime.now().isoformat()
        }
        await self.send(text_data=json.dumps(response))
        logger.debug(f"Sent response to {self.scope['user'].username}")

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))
