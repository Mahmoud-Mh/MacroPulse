import aiohttp
import logging
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class FREDAPI:
    def __init__(self):
        self.api_key = settings.FRED_API_KEY
        if not self.api_key:
            logger.error("FRED API key is not configured")
            raise ValueError("FRED API key is not configured")
        self.base_url = "https://api.stlouisfed.org/fred"
        
    async def get_series(self, series_id, observation_start=None, observation_end=None):
        """Fetch economic series data from FRED API"""
        if not observation_start:
            # Get 2 years of data instead of 10 years
            observation_start = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
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
            series_info = await self.get_series_info(series_id)
            if not series_info:
                raise Exception(f"Series {series_id} not found")

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/series/observations"
                logger.debug(f"Making request to {url}")
                logger.debug(f"Request params: {params}")
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"FRED API error: {error_text}")
                        raise Exception(f"FRED API returned status {response.status}: {error_text}")
                        
                    response_text = await response.text()
                    logger.debug(f"Raw FRED API response: {response_text}")
                    
                    try:
                        data = await response.json()
                        logger.debug(f"Parsed JSON response: {data}")
                    except Exception as e:
                        logger.error(f"Failed to parse FRED API response as JSON: {e}")
                        raise Exception(f"Failed to parse FRED API response: {e}")
                    
                    observations = data.get('observations', [])
                    logger.info(f"Received {len(observations)} observations from FRED API")
                    
                    if not observations:
                        logger.warning(f"No data available for series {series_id}")
                        return {
                            'series_id': series_id,
                            'title': series_info.get('title', ''),
                            'observations': [],
                            'units': series_info.get('units', ''),
                            'frequency': series_info.get('frequency', ''),
                            'error': 'No data available for this series'
                        }
                    
                    # Transform observations into the correct format
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
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching FRED data: {e}")
            raise Exception(f"Failed to connect to FRED API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_series: {e}")
            raise
                
    async def get_series_info(self, series_id):
        """Get series information from FRED API"""
        params = {
            'api_key': self.api_key,
            'file_type': 'json',
            'series_id': series_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/series"
                logger.debug(f"Making series info request to {url}")
                
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.debug(f"Raw FRED API series info response: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"FRED API series info error: {response_text}")
                        raise Exception(f"FRED API series info error: {response_text}")
                        
                    try:
                        data = await response.json()
                        series = data.get('seriess', [{}])[0]  # Get first series
                        return {
                            'title': series.get('title', ''),
                            'units': series.get('units', ''),
                            'frequency': series.get('frequency', '')
                        }
                    except Exception as e:
                        logger.error(f"Failed to parse FRED API series info response: {e}")
                        raise Exception(f"Failed to parse FRED API series info response: {e}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching series info: {e}")
            raise Exception(f"Failed to connect to FRED API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_series_info: {e}")
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
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/series/search"
                logger.debug(f"Making search request to {url} with term: {search_term}")
                
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.debug(f"Raw FRED API search response: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"FRED API search error: {response_text}")
                        raise Exception(f"FRED API search error: {response_text}")
                        
                    try:
                        data = await response.json()
                    except Exception as e:
                        logger.error(f"Failed to parse FRED API search response as JSON: {e}")
                        raise Exception(f"Failed to parse FRED API search response: {e}")
                    
                    return {
                        'count': data.get('count', 0),
                        'series': data.get('seriess', [])
                    }
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error while searching FRED data: {e}")
            raise Exception(f"Failed to connect to FRED API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in search_series: {e}")
            raise 