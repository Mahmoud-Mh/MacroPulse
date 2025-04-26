from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from datetime import datetime, timezone

class TokenStore:
    @staticmethod
    def _get_token_key(token):
        """Extract user_id and token type from JWT token"""
        try:
            decoded = AccessToken(token)
        except Exception:
            try:
                decoded = RefreshToken(token)
            except Exception:
                return None
        return f"token_{decoded['user_id']}_{decoded.get('token_type', 'access')}"

    @staticmethod
    def store_tokens(access_token, refresh_token=None):
        """Store user's tokens in cache"""
        try:
            access = AccessToken(access_token)
            user_id = access['user_id']
            
            access_key = f"token_{user_id}_access"
            cache.set(access_key, access_token, timeout=None)
            
            if refresh_token:
                refresh = RefreshToken(refresh_token)
                refresh_key = f"token_{user_id}_refresh"
                cache.set(refresh_key, refresh_token, timeout=None)
            
            return True
        except Exception:
            return False

    @staticmethod
    def is_token_valid(token):
        """Check if token is valid, not expired, and not blacklisted"""
        try:
            token_key = TokenStore._get_token_key(token)
            if not token_key:
                return False

            if cache.get(f"blacklist_{token_key}"):
                return False

            stored_token = cache.get(token_key)
            if not stored_token:
                return False

            try:
                decoded = AccessToken(token)
            except Exception:
                try:
                    decoded = RefreshToken(token)
                except Exception:
                    return False

            exp_timestamp = decoded['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_datetime < datetime.now(timezone.utc):
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def invalidate_token(token):
        """Add token to blacklist until its expiration"""
        try:
            token_key = TokenStore._get_token_key(token)
            if token_key:
                try:
                    decoded = AccessToken(token)
                except Exception:
                    try:
                        decoded = RefreshToken(token)
                    except Exception:
                        return False
                
                exp_timestamp = decoded['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                timeout = int((exp_datetime - now).total_seconds())
                
                if timeout > 0:
                    cache.set(f"blacklist_{token_key}", True, timeout=timeout)
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def clear_user_tokens(user_id):
        """Remove all tokens for a user"""
        access_key = f"token_{user_id}_access"
        refresh_key = f"token_{user_id}_refresh"
        cache.delete(access_key)
        cache.delete(refresh_key) 