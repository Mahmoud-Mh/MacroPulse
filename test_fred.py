from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv()

fred = Fred(api_key=os.getenv('FRED_API_KEY'))

try:
    # Try to get GDP data
    gdp = fred.get_series('GDP')
    print("Latest GDP value:", gdp.iloc[-1])
    print("Success!")
except Exception as e:
    print("Error:", str(e)) 