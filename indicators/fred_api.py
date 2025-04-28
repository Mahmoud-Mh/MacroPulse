import aiohttp
import logging
from datetime import datetime, timedelta
from django.conf import settings
import asyncio
import re

logger = logging.getLogger(__name__)

class FREDAPI:
    def __init__(self):
        self.api_key = settings.FRED_API_KEY.strip()  # Remove any whitespace
        if not self._validate_api_key(self.api_key):
            logger.error("Invalid FRED API key format")
            raise ValueError("Invalid FRED API key format. Key must be a 32 character alphanumeric lowercase string.")
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session = None
        
    def _validate_api_key(self, key):
        """Validate that the API key matches FRED's requirements"""
        if not key:
            return False
        # Check if key is 32 characters long and only contains lowercase alphanumeric characters
        return bool(re.match(r'^[a-z0-9]{32}$', key))
        
    async def ensure_session(self):
        """Ensure we have an active session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        """Close the session if it exists"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            
    async def __aenter__(self):
        await self.ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
            
    async def get_series(self, series_id, observation_start=None, observation_end=None):
        """Fetch economic series data from FRED API"""
        if not observation_start:
            
            observation_start = (datetime.now() - timedelta(days=7500)).strftime('%Y-%m-%d')
        if not observation_end:
            observation_end = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'series_id': series_id,
            'observation_start': observation_start,
            'observation_end': observation_end,
            'sort_order': 'desc'  # Get newest data first
        }
        
        logger.info(f"Fetching FRED series {series_id} from {observation_start} to {observation_end}")
        
        try:
            await self.ensure_session()
            series_info = await self.get_series_info(series_id)
            if not series_info:
                raise Exception(f"Series {series_id} not found")

            url = f"{self.base_url}/series/observations"
            logger.debug(f"Making request to {url}")
            
            async with self.session.get(url, params=params) as response:
                response_text = await response.text()
                logger.debug(f"Raw FRED API response: {response_text}")
                
                if response.status != 200:
                    logger.error(f"FRED API error: {response_text}")
                    raise Exception(f"FRED API error: {response_text}")
                    
                data = await response.json()
                observations = data.get('observations', [])
                
                if not observations:
                    return {
                        'series_id': series_id,
                        'title': series_info.get('title', ''),
                        'observations': [],
                        'units': series_info.get('units', ''),
                        'frequency': series_info.get('frequency', ''),
                        'error': 'No data available for this series'
                    }
                
                transformed_observations = []
                for obs in observations:
                    value = obs.get('value')
                    if value and value != '.':  # Skip missing or invalid values
                        try:
                            float_value = float(value)
                            transformed_observations.append({
                                'date': obs.get('date'),
                                'value': str(float_value)  # Convert back to string to maintain precision
                            })
                        except ValueError:
                            logger.warning(f"Skipping invalid numeric value: {value}")
                
                logger.info(f"Transformed {len(transformed_observations)} valid observations")
                if transformed_observations:
                    logger.debug(f"Sample observation: {transformed_observations[0]}")
                else:
                    logger.warning(f"No valid numeric data found for series {series_id}")
                    return {
                        'series_id': series_id,
                        'title': series_info.get('title', ''),
                        'observations': [],
                        'units': series_info.get('units', ''),
                        'frequency': series_info.get('frequency', ''),
                        'error': 'No valid numeric data found for this series'
                    }
                
                return {
                    'series_id': series_id,
                    'title': series_info.get('title', ''),
                    'observations': transformed_observations,
                    'units': series_info.get('units', ''),
                    'frequency': series_info.get('frequency', '')
                }
                    
        except Exception as e:
            logger.error(f"Error in get_series: {str(e)}")
            raise
        finally:
            if not self.session.closed:
                await self.close()
                
    async def get_series_info(self, series_id):
        """Get series information from FRED API"""
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'series_id': series_id
        }
        
        try:
            await self.ensure_session()
            url = f"{self.base_url}/series"
            async with self.session.get(url, params=params) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    logger.error(f"FRED API series info error: {response_text}")
                    raise Exception(f"FRED API series info error: {response_text}")
                    
                data = await response.json()
                series = data.get('seriess', [{}])[0]
                return {
                    'title': series.get('title', ''),
                    'units': series.get('units', ''),
                    'frequency': series.get('frequency', '')
                }
                    
        except Exception as e:
            logger.error(f"Error in get_series_info: {str(e)}")
            raise
                
    async def search_series(self, search_term):
        """Search for economic series in FRED API"""
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'search_text': search_term,
            'limit': 10
        }
        
        try:
            await self.ensure_session()
            url = f"{self.base_url}/series/search"
            async with self.session.get(url, params=params) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    logger.error(f"FRED API search error: {response_text}")
                    raise Exception(f"FRED API search error: {response_text}")
                    
                data = await response.json()
                return {
                    'count': data.get('count', 0),
                    'series': data.get('seriess', [])
                }
                    
        except Exception as e:
            logger.error(f"Error in search_series: {str(e)}")
            raise
        finally:
            if not self.session.closed:
                await self.close() 