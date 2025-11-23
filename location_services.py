"""
Location Services for Smart City System
Handles geocoding, reverse geocoding, and city data management
"""
import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
import random

@dataclass
class CityData:
    """Data class for city information"""
    name: str
    latitude: float
    longitude: float
    
    def to_dict(self):
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

class LocationService:
    """Service for handling location operations"""
    
    # Common city coordinates (fallback for demo)
    CITY_COORDINATES = {
        'new delhi': {'lat': 28.6139, 'lon': 77.2090},
        'mumbai': {'lat': 19.0760, 'lon': 72.8777},
        'bangalore': {'lat': 12.9716, 'lon': 77.5946},
        'kolkata': {'lat': 22.5726, 'lon': 88.3639},
        'chennai': {'lat': 13.0827, 'lon': 80.2707},
        'hyderabad': {'lat': 17.3850, 'lon': 78.4867},
        'pune': {'lat': 18.5204, 'lon': 73.8567},
        'london': {'lat': 51.5074, 'lon': -0.1278},
        'new york': {'lat': 40.7128, 'lon': -74.0060},
        'tokyo': {'lat': 35.6762, 'lon': 139.6503},
        'paris': {'lat': 48.8566, 'lon': 2.3522},
        'sydney': {'lat': -33.8688, 'lon': 151.2093},
    }
    
    def geocode(self, city_name: str) -> Optional[CityData]:
        """
        Convert city name to coordinates
        In a real app, this would use a geocoding API like Google Maps or OpenStreetMap
        """
        city_name_lower = city_name.lower().strip()
        
        # Check if city is in our database
        if city_name_lower in self.CITY_COORDINATES:
            coords = self.CITY_COORDINATES[city_name_lower]
            return CityData(
                name=city_name.title(),
                latitude=coords['lat'],
                longitude=coords['lon']
            )
        
        # Try partial matches
        for city, coords in self.CITY_COORDINATES.items():
            if city_name_lower in city or city in city_name_lower:
                return CityData(
                    name=city.title(),
                    latitude=coords['lat'],
                    longitude=coords['lon']
                )
        
        # If not found, return None (in production, use a real geocoding API)
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[CityData]:
        """
        Convert coordinates to city name
        In a real app, this would use a reverse geocoding API
        """
        # Find the closest city (simple distance calculation)
        min_distance = float('inf')
        closest_city = None
        
        for city, coords in self.CITY_COORDINATES.items():
            # Simple distance calculation (not accurate for large distances)
            distance = ((coords['lat'] - latitude) ** 2 + (coords['lon'] - longitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_city = city
        
        if closest_city and min_distance < 0.5:  # Within ~50km
            coords = self.CITY_COORDINATES[closest_city]
            return CityData(
                name=closest_city.title(),
                latitude=coords['lat'],
                longitude=coords['lon']
            )
        
        # If no close city found, create a generic city data
        return CityData(
            name=f"Location ({latitude:.4f}, {longitude:.4f})",
            latitude=latitude,
            longitude=longitude
        )

# Global location service instance
location_service = LocationService()

# City data storage
CITY_DATA_FILE = 'data/city_data.json'

def load_city_data() -> Dict[str, Any]:
    """Load city data from JSON file"""
    if os.path.exists(CITY_DATA_FILE):
        try:
            with open(CITY_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_city_data(data: Dict[str, Any]):
    """Save city data to JSON file"""
    os.makedirs(os.path.dirname(CITY_DATA_FILE), exist_ok=True)
    with open(CITY_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

