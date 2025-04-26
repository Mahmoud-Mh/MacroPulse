import aiohttp
import logging
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class FREDAPI:
    def __init__(self):
        self.api_key = settings.FRED_API_KEY
        self.base_url = "https://api.stlouisfed.org/fred"
        
    async def get_series(self, series_id, observation_start=None, observation_end=None):
        """Fetch economic series data from FRED API"""
        if not observation_start:
            observation_start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not observation_end:
            observation_end = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'series_id': series_id,
            'observation_start': observation_start,
            'observation_end': observation_end
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/series/observations", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"FRED API error: {error_text}")
                    raise Exception(f"FRED API error: {error_text}")
                    
                data = await response.json()
                return {
                    'series_id': series_id,
                    'title': data.get('title', ''),
                    'observations': data.get('observations', []),
                    'units': data.get('units', ''),
                    'frequency': data.get('frequency', '')
                }
                
    async def search_series(self, search_term):
        """Search for economic series in FRED API"""
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'search_text': search_term,
            'limit': 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/series/search", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"FRED API error: {error_text}")
                    raise Exception(f"FRED API error: {error_text}")
                    
                data = await response.json()
                return {
                    'count': data.get('count', 0),
                    'series': data.get('seriess', [])
                } 