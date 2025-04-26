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

User = get_user_model()

@database_sync_to_async
def get_user(token_key):
    """Authenticate WebSocket user from JWT token"""
    try:
        access_token = AccessToken(token_key)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except (InvalidTokenError, User.DoesNotExist):
        return AnonymousUser()

class WebSocketJWTAuthMiddleware(BaseMiddleware):
    """Middleware to authenticate WebSocket connections using JWT tokens"""
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        scope['user'] = await get_user(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)

class TokenValidationMiddleware:
    """Middleware to validate JWT tokens for API requests"""
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
            return self.get_response(request)

        token = auth_header.split(' ')[1]
        try:
            access_token = AccessToken(token)
            jti = access_token.get('jti')
            user_id = access_token.get('user_id')

            if jti and user_id:
                try:
                    token_record = OutstandingToken.objects.get(
                        jti=jti,
                        user_id=user_id
                    )
                    if BlacklistedToken.objects.filter(token=token_record).exists():
                        return JsonResponse(
                            {'error': 'Token has been blacklisted'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                except OutstandingToken.DoesNotExist:
                    pass

        except TokenError:
            return JsonResponse(
                {'error': 'Invalid token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return self.get_response(request) 