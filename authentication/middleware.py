from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from jwt import InvalidTokenError
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .token_store import TokenStore
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@database_sync_to_async
def get_user(token_key):
    try:
        logger.debug(f"Authenticating WebSocket connection with token: {token_key[:10]}...")
        
        if not TokenStore.is_token_valid(token_key):
            logger.warning("Token is invalid or blacklisted")
            return AnonymousUser()
            
        access_token = AccessToken(token_key)
        user = User.objects.get(id=access_token['user_id'])
        logger.info(f"Successfully authenticated user: {user.username}")
        return user
    except (InvalidTokenError, User.DoesNotExist) as e:
        logger.error(f"Authentication failed: {str(e)}")
        return AnonymousUser()

class WebSocketJWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            if scope["type"] == "websocket":
                query_string = scope.get('query_string', b'').decode()
                query_params = parse_qs(query_string)
                token = query_params.get('token', [None])[0]
                
                if not token:
                    logger.warning("No token provided in WebSocket connection")
                    scope['user'] = AnonymousUser()
                else:
                    scope['user'] = await get_user(token)
                    
                if isinstance(scope['user'], AnonymousUser):
                    await send({
                        "type": "websocket.close",
                        "code": 4401,
                    })
                    return
                
                return await super().__call__(scope, receive, send)
            
            return await super().__call__(scope, receive, send)
            
        except Exception as e:
            logger.error(f"Error in WebSocket middleware: {str(e)}")
            if scope["type"] == "websocket":
                await send({
                    "type": "websocket.close",
                    "code": 4500,
                })
            return

class TokenValidationMiddleware:
    EXEMPT_PATHS = {
        '/api/auth/token/',
        '/api/auth/token/refresh/',
        '/api/auth/register/',
        '/api/auth/logout/',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/api/') or request.path in self.EXEMPT_PATHS:
            return self.get_response(request)
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'No valid token provided'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        token = auth_header.split(' ')[1]
        if not TokenStore.is_token_valid(token):
            return JsonResponse(
                {'error': 'Token is invalid or has been blacklisted'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return self.get_response(request)