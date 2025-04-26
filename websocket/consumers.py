from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
import logging
from indicators.fred_api import FREDAPI

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
        """Handle different types of economic data requests"""
        message_type = data.get('type')
        
        if message_type == 'heartbeat':
            # Acknowledge heartbeat
            await self.send(text_data=json.dumps({
                'type': 'heartbeat_ack',
                'timestamp': datetime.now().isoformat()
            }))
            return
            
        if message_type == 'get_series':
            series_id = data.get('series_id')
            if not series_id:
                await self.send_error("Series ID is required")
                return
                
            try:
                fred_api = FREDAPI()
                series_data = await fred_api.get_series(series_id)
                logger.info(f"FRED API response for series {series_id}: {series_data}")
                await self.send(text_data=json.dumps({
                    'type': 'series_data',
                    'series_id': series_id,
                    'data': series_data,
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error fetching series data: {str(e)}")
                await self.send_error(f"Error fetching series data: {str(e)}")
                
        elif message_type == 'search_series':
            search_term = data.get('search_term')
            if not search_term:
                await self.send_error("Search term is required")
                return
                
            try:
                fred_api = FREDAPI()
                search_results = await fred_api.search_series(search_term)
                await self.send(text_data=json.dumps({
                    'type': 'search_results',
                    'search_term': search_term,
                    'results': search_results,
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error searching series: {str(e)}")
                await self.send_error(f"Error searching series: {str(e)}")
                
        else:
            await self.send_error(f"Unknown message type: {message_type}")

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))
