"""
API Services for fetching real-time data from external APIs
"""
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import random

class APIService:
    """Service for fetching data from external APIs"""
    def __init__(self):
        # API Keys - In production, these should be in environment variables
        # For demo, we'll use free/public APIs or simulate data
        self.openweather_api_key = None  # Set your OpenWeatherMap API key here
        self.airvisual_api_key = None    # Set your AirVisual API key here
        
    def fetch_air_quality_data(self, city_name: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """
        Fetch real air quality data
        Uses OpenWeatherMap Air Pollution API or AirVisual API
        Falls back to realistic simulated data if API keys not available
        """
        # Try OpenWeatherMap Air Pollution API
        if lat and lon and self.openweather_api_key:
            try:
                url = f"http://api.openweathermap.org/data/2.5/air_pollution"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_api_key
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    components = data.get('list', [{}])[0].get('components', {})
                    main = data.get('list', [{}])[0].get('main', {})
                    
                    return {
                        'pm25': components.get('pm2_5', 0),
                        'pm10': components.get('pm10', 0),
                        'no2': components.get('no2', 0),
                        'co': components.get('co', 0) / 1000,  # Convert to ppm
                        'so2': components.get('so2', 0),
                        'aqi': main.get('aqi', 0) * 50,  # Scale 1-5 to 0-250
                        'source': 'OpenWeatherMap'
                    }
            except Exception as e:
                print(f"Error fetching from OpenWeatherMap: {e}")
        
        # Try AirVisual API (IQAir)
        if city_name and self.airvisual_api_key:
            try:
                url = "https://api.airvisual.com/v2/city"
                params = {
                    'city': city_name,
                    'state': '',  # Can be enhanced
                    'country': 'India',
                    'key': self.airvisual_api_key
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get('data', {}).get('current', {})
                    pollution = current.get('pollution', {})
                    weather = current.get('weather', {})
                    
                    return {
                        'pm25': pollution.get('aqius', 0),  # AirVisual uses AQI US
                        'pm10': pollution.get('aqius', 0) * 1.2,  # Estimate
                        'no2': pollution.get('aqius', 0) * 0.3,  # Estimate
                        'co': pollution.get('aqius', 0) * 0.05,  # Estimate
                        'so2': pollution.get('aqius', 0) * 0.1,  # Estimate
                        'aqi': pollution.get('aqius', 0),
                        'temperature': weather.get('tp', 25),
                        'humidity': weather.get('hu', 60),
                        'wind_speed': weather.get('ws', 10),
                        'source': 'AirVisual'
                    }
            except Exception as e:
                print(f"Error fetching from AirVisual: {e}")
        
        # Fallback: Generate realistic data based on city
        # Delhi typically has high AQI (150-300+), Mumbai moderate (100-200)
        city_lower = city_name.lower()
        if 'delhi' in city_lower:
            # Delhi has notoriously poor air quality
            base_aqi = random.uniform(180, 350)  # Realistic for Delhi
            pm25 = base_aqi * 0.6
            pm10 = base_aqi * 0.8
        elif 'mumbai' in city_lower:
            base_aqi = random.uniform(100, 200)
            pm25 = base_aqi * 0.6
            pm10 = base_aqi * 0.8
        elif 'bangalore' in city_lower or 'bengaluru' in city_lower:
            base_aqi = random.uniform(80, 150)
            pm25 = base_aqi * 0.6
            pm10 = base_aqi * 0.8
        else:
            # Other cities - moderate
            base_aqi = random.uniform(50, 150)
            pm25 = base_aqi * 0.6
            pm10 = base_aqi * 0.8
        
        return {
            'pm25': round(pm25, 1),
            'pm10': round(pm10, 1),
            'no2': round(base_aqi * 0.2, 1),
            'co': round(base_aqi * 0.03, 2),
            'so2': round(base_aqi * 0.1, 1),
            'temperature': round(random.uniform(20, 35), 1),
            'humidity': round(random.uniform(40, 80), 1),
            'wind_speed': round(random.uniform(5, 20), 1),
            'aqi': round(base_aqi, 1),
            'source': 'Simulated (Realistic)'
        }
    
    def fetch_weather_data(self, city_name: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Fetch weather data for accident risk prediction"""
        if lat and lon and self.openweather_api_key:
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_api_key,
                    'units': 'metric'
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    weather_main = data.get('weather', [{}])[0].get('main', '').lower()
                    
                    # Map weather to condition code
                    weather_condition = 0  # Clear
                    if 'rain' in weather_main:
                        weather_condition = 1  # Rainy
                    elif 'fog' in weather_main or 'mist' in weather_main:
                        weather_condition = 2  # Foggy
                    
                    return {
                        'temperature': data.get('main', {}).get('temp', 25),
                        'humidity': data.get('main', {}).get('humidity', 60),
                        'wind_speed': data.get('wind', {}).get('speed', 10) * 3.6,  # Convert m/s to km/h
                        'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                        'weather_condition': weather_condition,
                        'weather_description': data.get('weather', [{}])[0].get('description', 'clear'),
                        'source': 'OpenWeatherMap'
                    }
            except Exception as e:
                print(f"Error fetching weather: {e}")
        
        # Fallback: Generate realistic data
        return {
            'temperature': round(random.uniform(15, 35), 1),
            'humidity': round(random.uniform(40, 85), 1),
            'wind_speed': round(random.uniform(5, 25), 1),
            'visibility': round(random.uniform(2, 10), 1),
            'weather_condition': random.choice([0, 1, 2]),
            'weather_description': random.choice(['clear', 'partly cloudy', 'rainy', 'foggy']),
            'source': 'Simulated'
        }
    
    def fetch_traffic_data(self, city_name: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Fetch traffic data for accident risk prediction"""
        # In production, this would use Google Maps API, TomTom, or similar
        # For now, generate realistic data
        city_lower = city_name.lower()
        
        # Major cities typically have higher traffic
        if 'delhi' in city_lower or 'mumbai' in city_lower:
            vehicle_density = random.randint(300, 500)
            avg_speed = random.randint(25, 50)
        elif 'bangalore' in city_lower or 'bengaluru' in city_lower:
            vehicle_density = random.randint(250, 400)
            avg_speed = random.randint(30, 60)
        else:
            vehicle_density = random.randint(150, 350)
            avg_speed = random.randint(40, 70)
        
        return {
            'vehicle_density': vehicle_density,
            'avg_speed': avg_speed,
            'source': 'Simulated'
        }
    
    def fetch_parking_data(self, city_name: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Fetch parking data"""
        # In production, this would use parking APIs or IoT sensors
        # For now, generate realistic data
        return {
            'parking_capacity': random.randint(100, 300),
            'occupied_slots': random.randint(50, 250),
            'entry_rate': round(random.uniform(10, 40), 1),
            'exit_rate': round(random.uniform(8, 35), 1),
            'source': 'Simulated'
        }
    
    def fetch_citizen_activity_data(self, city_name: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Fetch citizen activity data"""
        # In production, this would use mobile data, WiFi hotspots, etc.
        # For now, generate realistic data based on city size
        city_lower = city_name.lower()
        
        if 'delhi' in city_lower or 'mumbai' in city_lower:
            population_density = random.randint(10000, 20000)
            workplace_count = random.randint(40, 80)
        elif 'bangalore' in city_lower or 'bengaluru' in city_lower:
            population_density = random.randint(8000, 15000)
            workplace_count = random.randint(30, 60)
        else:
            population_density = random.randint(5000, 12000)
            workplace_count = random.randint(20, 50)
        
        return {
            'population_density': population_density,
            'avg_age': random.randint(28, 45),
            'workplace_count': workplace_count,
            'public_events': random.randint(0, 5),
            'source': 'Simulated'
        }

# Global API service instance
api_service = APIService()

