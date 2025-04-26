from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .token_store import TokenStore

class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that validates tokens against our token store"""
    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        
        # Get user_id from token
        user_id = validated_token.get('user_id')
        if not user_id:
            raise InvalidToken('Token contains no user ID')
        
        # Check if token is valid in our store (FIXED ARGUMENT)
        decoded_token = raw_token.decode()
        if not TokenStore.is_token_valid(decoded_token):  # Only pass the token
            raise InvalidToken('Token is not valid or has been invalidated')
        
        return validated_token