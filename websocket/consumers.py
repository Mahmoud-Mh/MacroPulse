import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from authentication.token_store import TokenStore

User = get_user_model()

class EconomicDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the token from query parameters
        token = self.scope.get('query_string', b'').decode().split('token=')[-1]
        
        if not token:
            await self.close()
            return
            
        try:
            # Verify the token exists in our store
            user_id = await self.get_user_from_token(token)
            if not user_id:
                await self.close()
                return
                
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close()
                return
                
            await self.channel_layer.group_add(
                "economic_data",
                self.channel_name
            )
            await self.accept()
            
        except TokenError:
            await self.close()
            return
            
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # First verify the token is valid
            access_token = AccessToken(token)
            # Then check if it exists in our store
            if TokenStore.validate_token(str(access_token)):
                return access_token['user_id']
            return None
        except TokenError:
            return None
            
    @database_sync_to_async  
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                "economic_data",
                self.channel_name
            )
        except:
            pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            await self.channel_layer.group_send(
                "economic_data",
                {
                    'type': 'economic_data_message',
                    'message': message
                }
            )
        except json.JSONDecodeError:
            pass

    async def economic_data_message(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'message': message
        })) 