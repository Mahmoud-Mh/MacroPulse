import requests
import json

def test_fred_api():
    api_key = "46a4f7f6f63c11533490bfdf32039609"
    base_url = "https://api.stlouisfed.org/fred"
    
    # Test endpoint - get series info for GDP (GDPC1)
    params = {
        'api_key': api_key,
        'file_type': 'json',
        'series_id': 'GDPC1'
    }
    
    url = f"{base_url}/series"
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print("Response Headers:", json.dumps(dict(response.headers), indent=2))
    print("Response Body:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_fred_api() 