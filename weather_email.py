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


def extract_relevant_forecast_data(forecast_json: dict[str, Any]) -> Forecast:
    """Extracts only the information that will be used in email"""
    day = forecast_json['forecast']['forecastday'][0]['day']
    forecast = {'min_temp': day['mintemp_f'], 'max_temp': day['maxtemp_f'],
                'total_precip': day['totalprecip_in']}
    forecast['condition'] = day['condition']['text']
    forecast['icon_filename'] = day['condition']['icon'].split('/')[-1]
    return forecast