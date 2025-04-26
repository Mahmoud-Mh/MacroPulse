import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Indicator
from .serializers import IndicatorListSerializer
from django.contrib.auth.models import AnonymousUser


class IndicatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Check if user is authenticated
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4001)  # Custom close code for unauthorized
            return

        # Join indicators group with user-specific group name
        self.group_name = f"indicators_{self.scope['user'].id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send init data
        indicators = await self.get_latest_indicators()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'indicators': indicators
        }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave indicators group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        try:
            text_data_json = json.loads(text_data)
            command = text_data_json.get('command')
            
            if command == 'get_latest':
                indicators = await self.get_latest_indicators()
                await self.send(text_data=json.dumps({
                    'type': 'latest_indicators',
                    'indicators': indicators
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown command'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def indicator_update(self, event):
        """
        Called when someone has messaged our group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'indicator_update',
            'indicator': event['indicator']
        }))

    @database_sync_to_async
    def get_latest_indicators(self):
        """
        Get the latest indicators from the database.
        """
        # Add user-specific filtering if needed
        indicators = Indicator.objects.all().order_by('-last_update')[:10]
        serializer = IndicatorListSerializer(indicators, many=True)
        return serializer.data 