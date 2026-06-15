import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_weather_data():
    """Fetch current weather data for Dirang, Arunachal Pradesh, India"""
    # Try to load API keys from Django settings, or fall back to environment variables
    openweather_key = None
    weatherapi_key = None
    try:
        from django.conf import settings
        openweather_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        weatherapi_key = getattr(settings, 'WEATHERAPI_KEY', None)
    except Exception as e:
        logger.debug(f"Could not load API keys from settings: {e}")

    if not openweather_key:
        openweather_key = os.environ.get('OPENWEATHER_API_KEY')
    if not weatherapi_key:
        weatherapi_key = os.environ.get('WEATHERAPI_KEY')
    
    # Mode 1: WeatherAPI.com (Preferred for detailed fields)
    if weatherapi_key:
        try:
            # Query for Dirang, Arunachal Pradesh, India
            url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q=Dirang,Arunachal Pradesh,India"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data['current']
                return {
                    'temperature': current['temp_c'],
                    'humidity': current['humidity'],
                    'condition': current['condition']['text'],
                    'wind_speed': round(current['wind_kph'] / 3.6, 1),  # convert km/h to m/s
                    'last_updated': current['last_updated'],
                    'source': 'WeatherAPI'
                }
            else:
                logger.warning(f"WeatherAPI failed with status code: {response.status_code}")
        except Exception as e:
            logger.error(f"WeatherAPI fetch failed: {e}")
            
    # Mode 2: OpenWeatherMap API
    if openweather_key:
        try:
            # Dirang, IN (latitude/longitude or query query)
            url = f"https://api.openweathermap.org/data/2.5/weather?q=Dirang,IN&appid={openweather_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Convert DT unix timestamp to human-readable string
                last_updated = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M')
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'condition': data['weather'][0]['description'].title(),
                    'wind_speed': data['wind']['speed'],
                    'last_updated': last_updated,
                    'source': 'OpenWeatherMap'
                }
            else:
                logger.warning(f"OpenWeatherMap failed with status code: {response.status_code}")
        except Exception as e:
            logger.error(f"OpenWeatherMap fetch failed: {e}")

    # Mode 3: Open-Meteo API (Free fallback, no API key needed)
    try:
        # Latitude and longitude for Dirang, Arunachal Pradesh, India: 27.3584, 92.2422
        url = "https://api.open-meteo.com/v1/forecast?latitude=27.3584&longitude=92.2422&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current']
            
            # Map WMO weather code to standard condition text
            wmo_code = current.get('weather_code', 0)
            wmo_codes = {
                0: "Clear Sky",
                1: "Mainly Clear",
                2: "Partly Cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing Rime Fog",
                51: "Light Drizzle",
                53: "Moderate Drizzle",
                55: "Dense Drizzle",
                56: "Light Freezing Drizzle",
                57: "Dense Freezing Drizzle",
                61: "Slight Rain",
                63: "Moderate Rain",
                65: "Heavy Rain",
                66: "Light Freezing Rain",
                67: "Heavy Freezing Rain",
                71: "Slight Snow Fall",
                73: "Moderate Snow Fall",
                75: "Heavy Snow Fall",
                77: "Snow Grains",
                80: "Slight Rain Showers",
                81: "Moderate Rain Showers",
                82: "Violent Rain Showers",
                85: "Slight Snow Showers",
                86: "Heavy Snow Showers",
                95: "Thunderstorm",
                96: "Thunderstorm with Hail",
                99: "Thunderstorm with Heavy Hail"
            }
            condition = wmo_codes.get(wmo_code, "Partly Cloudy")
            
            # Format time from '2026-06-15T12:15' to '2026-06-15 12:15'
            time_str = current.get('time', '')
            if 'T' in time_str:
                last_updated = time_str.replace('T', ' ')
            else:
                last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
                
            # Convert wind speed from km/h to m/s
            wind_kph = current.get('wind_speed_10m', 0.0)
            wind_speed = round(wind_kph / 3.6, 1)

            return {
                'temperature': current.get('temperature_2m'),
                'humidity': current.get('relative_humidity_2m'),
                'condition': condition,
                'wind_speed': wind_speed,
                'last_updated': last_updated,
                'source': 'Open-Meteo'
            }
        else:
            logger.warning(f"Open-Meteo failed with status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Open-Meteo fetch failed: {e}")

    # Failure / Fallback: return None
    return None

