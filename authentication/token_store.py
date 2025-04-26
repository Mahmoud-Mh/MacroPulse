from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class TokenStore:
    @staticmethod
    def _get_token_key(raw_token):
        """Extract user_id and token type from JWT token"""
        try:
            # Try to decode the token directly
            if isinstance(raw_token, bytes):
                raw_token = raw_token.decode()
                
            logger.debug(f"Attempting to validate token: {raw_token[:20]}...")
            
            # Try as access token first
            try:
                token = AccessToken(raw_token)
                token_type = 'access'
            except Exception:
                # Try as refresh token
                try:
                    token = RefreshToken(raw_token)
                    token_type = 'refresh'
                except Exception as e:
                    logger.error(f"Failed to decode token: {str(e)}")
                    return None
            
            user_id = token.get('user_id')
            if not user_id:
                logger.error("Token does not contain user_id")
                return None
                
            key = f"token_{user_id}_{token_type}"
            logger.debug(f"Successfully extracted token key: {key}")
            return key
            
        except Exception as e:
            logger.error(f"Error extracting token key: {str(e)}")
            return None

    @staticmethod
    def store_tokens(access_token, refresh_token=None):
        """Store user's tokens in cache with proper expiry"""
        try:
            access = AccessToken(access_token)
            user_id = access['user_id']
            
            # Calculate remaining time until token expiry
            exp_timestamp = access['exp']
            now = datetime.now(timezone.utc).timestamp()
            timeout = int(exp_timestamp - now)
            
            # Store access token with expiry
            access_key = f"token_{user_id}_access"
            cache.set(access_key, access_token, timeout=timeout)
            logger.debug(f"Stored access token for user {user_id} with {timeout}s timeout")
            
            # Store refresh token if provided
            if refresh_token:
                refresh = RefreshToken(refresh_token)
                refresh_exp_timestamp = refresh['exp']
                refresh_timeout = int(refresh_exp_timestamp - now)
                refresh_key = f"token_{user_id}_refresh"
                cache.set(refresh_key, refresh_token, timeout=refresh_timeout)
                logger.debug(f"Stored refresh token for user {user_id} with {refresh_timeout}s timeout")
            
            return True
        except Exception as e:
            logger.error(f"Failed to store tokens: {str(e)}")
            return False

    @staticmethod
    def is_token_valid(token):
        """Check if token is valid, not expired, and not blacklisted"""
        try:
            # Get token key
            token_key = TokenStore._get_token_key(token)
            if not token_key:
                logger.warning("Could not extract token key")
                return False

            # Check if token is blacklisted
            if cache.get(f"blacklist_{token_key}"):
                logger.warning(f"Token {token_key} is blacklisted")
                return False

            # Validate token and check expiry
            try:
                token_obj = AccessToken(token)
            except Exception:
                try:
                    token_obj = RefreshToken(token)
                except Exception:
                    logger.warning("Token is neither a valid access nor refresh token")
                    return False

            exp_timestamp = token_obj['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_datetime < datetime.now(timezone.utc):
                logger.warning("Token has expired")
                return False

            # Token is valid
            logger.debug(f"Token {token_key} is valid")
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False

    @staticmethod
    def invalidate_token(token):
        """Add token to blacklist until its expiration"""
        try:
            token_key = TokenStore._get_token_key(token)
            if token_key:
                try:
                    token_obj = AccessToken(token)
                except Exception:
                    try:
                        token_obj = RefreshToken(token)
                    except Exception:
                        return False
                
                exp_timestamp = token_obj['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                timeout = int((exp_datetime - now).total_seconds())
                
                if timeout > 0:
                    cache.set(f"blacklist_{token_key}", True, timeout=timeout)
                    logger.info(f"Token {token_key} blacklisted for {timeout}s")
                    return True
        except Exception as e:
            logger.error(f"Failed to invalidate token: {str(e)}")
        return False

    @staticmethod
    def clear_user_tokens(user_id):
        """Remove all tokens for a user"""
        access_key = f"token_{user_id}_access"
        refresh_key = f"token_{user_id}_refresh"
        cache.delete(access_key)
        cache.delete(refresh_key)
        logger.info(f"Cleared all tokens for user {user_id}") 