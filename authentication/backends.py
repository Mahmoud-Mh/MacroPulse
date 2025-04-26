from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from datetime import datetime, timezone

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that validates tokens"""
    def get_validated_token(self, raw_token):
        try:
            # First validate using parent class
            validated_token = super().get_validated_token(raw_token)
            
            # Get user_id from token
            user_id = validated_token.get('user_id')
            if not user_id:
                raise InvalidToken('Token contains no user ID')
            
            # Check if token is expired
            exp_timestamp = validated_token['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_datetime < datetime.now(timezone.utc):
                raise InvalidToken('Token has expired')
                
            # Check if user exists and is active
            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    raise InvalidToken('User is not active')
            except User.DoesNotExist:
                raise InvalidToken('User does not exist')
            
            return validated_token
            
        except Exception as e:
            raise InvalidToken(str(e))