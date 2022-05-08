import os, requests
from dotenv import load_dotenv
from typing import Any, TypedDict


load_dotenv()


class Forecast(TypedDict):
    """Represents the minimum weather info to be displayed in email"""
    min_temp: float
    max_temp: float
    total_precip: float
    condition: str  # Such as Partly Cloudy or Sunny
    icon_filename: str


def get_forecast_json(zip_code: str) -> dict[str, Any]:
    """Returns the forecast data for the specified zip code
    
    Currently, there are no checks to determine whether the zip code
    is valid or if the API can be accessed"""
    api_key = os.getenv('WEATHER_API_KEY')
    params = {'key': api_key, 'q': zip_code, 'days': 1,
          'aqi': 'no', 'alerts': 'no'}
    link = 'http://api.weatherapi.com/v1/forecast.json'
    response = requests.get(link, params=params)
    return response.json()