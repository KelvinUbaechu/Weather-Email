from typing import TypedDict


class Forecast(TypedDict):
    """Represents the minimum weather info to be displayed in email"""
    min_temp: float
    max_temp: float
    total_precip: float
    condition: str  # Such as Partly Cloudy or Sunny
    icon_filename: str
