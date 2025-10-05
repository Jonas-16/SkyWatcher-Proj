import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

# ------------------ User Settings ------------------ #
google_api_key = "AIzaSyCKv-2M-DEyU6U-P-ZDeoB2zM0kgG-sVYA"  # your key
username = "vaz_jonas"
password = "A08MvxQ0uV51sV81Ovqp"

# ------------------ Helper Functions ------------------ #
def get_coordinates(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "WeatherDataRetrieval/1.0"}
    response = requests.get(url, params=params, headers=headers)
    if not response.text.strip():
        raise ValueError(f"No response from Nominatim API for '{place_name}'")
    json_data = response.json()
    if json_data:
        return float(json_data[0]["lat"]), float(json_data[0]["lon"])
    else:
        raise ValueError(f"Place '{place_name}' not found!")

# ------------------ Google Weather (Live) ------------------ #
def get_google_weather(lat, lon, api_key):
    try:
        base_url = "https://weather.googleapis.com/v1/currentConditions:lookup"
        params = {"key": api_key, "location.latitude": lat, "location.longitude": lon}
        resp_current = requests.get(base_url, params=params)
        if not resp_current.text.strip():
            return pd.DataFrame()  # empty df if no data
        current = resp_current.json().get("currentConditions", [{}])[0]
        return current
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

"""Small CLI wrapper that uses the backend WeatherService to fetch and print a summary.

This file is a thin wrapper: the heavy lifting lives in
`backend/app/services/weather_service.py` to avoid duplication.
"""

import asyncio
import sys
from backend.app.services.weather_service import WeatherService


async def main(place: str, date: str):
    svc = WeatherService()
    result = await svc.analyze_weather_probability(place, date)
    print("Place:", result.get('place'))
    print("Date:", result.get('date'))
    print("Coordinates:", result.get('coordinates'))
    print("Temperature:", result.get('temperature'))
    print("Probabilities:", result.get('probabilities'))
    print("Hourly breakdown rows:", len(result.get('hourly_breakdown', [])))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python get-coordinates.py <place> <YYYY-MM-DD>")
        sys.exit(2)
    place = sys.argv[1]
    date = sys.argv[2]
    asyncio.run(main(place, date))
