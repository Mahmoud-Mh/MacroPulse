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
from datetime import datetime, timezone
from .token_store import TokenStore
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@database_sync_to_async
def get_user(token_key):
    try:
        logger.debug(f"Authenticating WebSocket connection with token: {token_key[:10]}...")
        
        # Check if token is valid via TokenStore
        if not TokenStore.is_token_valid(token_key):
            logger.warning("Token is invalid or blacklisted")
            return AnonymousUser()
        
        # Validate token
        access_token = AccessToken(token_key)
        
        # Check if token is expired
        exp_timestamp = access_token['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if exp_datetime < datetime.now(timezone.utc):
            logger.warning("Token has expired")
            return AnonymousUser()
            
        # Get user from database
        user = User.objects.get(id=access_token['user_id'])
        if not user.is_active:
            logger.warning(f"User {user.username} is not active")
            return AnonymousUser()
            
        logger.info(f"Successfully authenticated user: {user.username}")
        return user
    except TokenError as e:
        logger.error(f"Token validation failed: {str(e)}")
        return AnonymousUser()
    except User.DoesNotExist as e:
        logger.error(f"User does not exist: {str(e)}")
        return AnonymousUser()
    except Exception as e:
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
        '/api/v1/auth/token/',
        '/api/v1/auth/token/refresh/',
        '/api/v1/auth/register/',
        '/api/v1/auth/logout/',
        '/api/v2/auth/token/',
        '/api/v2/auth/token/refresh/',
        '/api/v2/auth/register/',
        '/api/v2/auth/logout/',
        '/admin/',
        '/api/docs/',
        '/api/docs/redoc/',
        '/api/schema/',
        '/health/',
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
        try:
            # Check if token is valid via TokenStore
            if not TokenStore.is_token_valid(token):
                return JsonResponse(
                    {'error': 'Token is invalid or has been blacklisted'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            access_token = AccessToken(token)
            exp_timestamp = access_token['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_datetime < datetime.now(timezone.utc):
                return JsonResponse(
                    {'error': 'Token has expired'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            # Verify user exists and is active
            user = User.objects.get(id=access_token['user_id'])
            if not user.is_active:
                return JsonResponse(
                    {'error': 'User account is not active'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except (TokenError, User.DoesNotExist) as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return self.get_response(request)