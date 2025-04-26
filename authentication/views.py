from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer
from .token_store import TokenStore

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user and return their tokens"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Store tokens
        TokenStore.store_tokens(access_token, refresh_token)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': access_token,
                'refresh': refresh_token,
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain(request):
    """Login endpoint - validate credentials and return tokens"""
    try:
        user = User.objects.get(username=request.data.get('username'))
        if not user.check_password(request.data.get('password')):
            raise User.DoesNotExist
            
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Store tokens
        TokenStore.store_tokens(access_token, refresh_token)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """Generate new access token using refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not TokenStore.is_token_valid(refresh_token):
            return Response(
                {'error': 'Invalid or expired refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        # Store new access token
        TokenStore.store_tokens(access_token)
        
        return Response({
            'access': access_token,
        })
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Invalidate user's tokens"""
    try:
        # Get tokens from request
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.split(' ')[1] if auth_header else None
        refresh_token = request.data.get('refresh')
        
        # Invalidate both tokens
        if access_token:
            TokenStore.invalidate_token(access_token)
        if refresh_token:
            TokenStore.invalidate_token(refresh_token)
            
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get authenticated user's profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
