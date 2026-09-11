import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {"error": "API key is not configured."}

    url = f"{BASE_URL}/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return {"error": "City not found."}

        if response.status_code == 401:
            return {"error": "Invalid API key."}

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}

    except requests.exceptions.ConnectionError:
        return {"error": "Network connection error."}

    except requests.exceptions.RequestException:
        return {"error": "Unable to fetch weather data."}


def get_forecast(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {"error": "API key is not configured."}

    url = f"{BASE_URL}/forecast"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return {"error": "City not found."}

        if response.status_code == 401:
            return {"error": "Invalid API key."}

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}

    except requests.exceptions.ConnectionError:
        return {"error": "Network connection error."}

    except requests.exceptions.RequestException:
        return {"error": "Unable to fetch forecast data."}