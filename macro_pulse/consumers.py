import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import asyncio
import logging
from datetime import datetime
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)
User = get_user_model()

class EconomicDataConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = False
        self.heartbeat_task = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1  # seconds
        self.group_name = None

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        try:
            # The connection is already authenticated by the middleware
            user = self.scope.get('user')
            if not user or user.is_anonymous:
                logger.warning("WebSocket connection rejected: Invalid user")
                await self.close(code=4002, reason="Invalid user")
                return

            # Join economic data group with user-specific group name
            self.group_name = f"economic_data_{user.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            # Set connected flag
            self.connected = True
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
            
            # Send initial data
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'message': 'Connected to economic data stream',
                'user_id': user.id,
                'timestamp': datetime.now().isoformat()
            }))
            
            logger.info(f"WebSocket connected for user {user.username}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            await self.close(code=1011, reason="Internal server error")
            return

    async def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        try:
            text_data_json = json.loads(text_data)
            
            # Handle heartbeat messages
            if text_data_json.get('type') == 'heartbeat':
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat_ack',
                    'timestamp': datetime.now().isoformat()
                }))
                return
            
            # Handle other message types here
            # For example:
            # if text_data_json.get('type') == 'subscribe':
            #     await self.handle_subscription(text_data_json)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        self.connected = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        # Leave economic data group
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def heartbeat_loop(self):
        """Send periodic heartbeats to keep connection alive"""
        while self.connected:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                if self.connected:
                    await self.send(text_data=json.dumps({
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    }))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                if self.connected:
                    await self.close(code=1011, reason="Internal server error")

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None 