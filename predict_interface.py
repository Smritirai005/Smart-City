import pandas as pd
import numpy as np
# from smart_city_system import SmartCitySystem

def predict_accident_risk(vehicle_density, avg_speed, road_condition, weather_condition, visibility, time_of_day):
    """Predict accident risk level"""
    # Example prediction logic
    score = (vehicle_density/500)*0.4 + (1 - avg_speed/100)*0.3 + \
            (2 - road_condition)*0.1 + weather_condition*0.1 + \
            (1 - visibility/1000)*0.1
    
    if score < 0.4: return "Low Risk"
    elif score < 0.7: return "Medium Risk"
    else: return "High Risk"

def predict_air_quality(pm25, pm10, no2, co, so2, temperature, humidity, wind_speed):
    """Predict AQI value"""
    aqi = (0.4*pm25 + 0.3*pm10 + 0.1*no2 + 15*co + 0.05*so2 - 
           0.2*wind_speed - 0.1*humidity)
    return max(0, min(500, aqi))

def predict_citizen_activity(population_density, avg_age, workplace_count, public_events, temperature, day_of_week):
    """Predict citizen activity level"""
    score = (population_density/15000)*0.4 + (workplace_count/50)*0.3 + \
            (public_events/5)*0.2 + (temperature/40)*0.1
    
    if score < 0.4: return "Low Activity"
    elif score < 0.7: return "Moderate Activity"
    else: return "High Activity"

def predict_parking_availability(parking_capacity, occupied_slots, entry_rate, exit_rate, time_of_day, weekday, nearby_events):
    """Predict parking availability"""
    utilization = occupied_slots/parking_capacity
    inflow = entry_rate - exit_rate
    score = utilization + inflow/50 + nearby_events*0.5
    
    return "Full" if score > 1.2 else "Available"

def demo_predictions():
    """Demonstrate the prediction system with sample inputs"""
    print("SMART CITY PREDICTION SYSTEM - DEMO")
    print("="*50)
    
    # Accident Risk Prediction
    print("\nACCIDENT RISK PREDICTION")
    risk = predict_accident_risk(
        vehicle_density=300, avg_speed=45, road_condition=1, 
        weather_condition=1, visibility=200, time_of_day=3
    )
    print(f"Prediction: {risk}")
    
    # Air Quality Prediction
    print("\nAIR QUALITY PREDICTION")
    aqi = predict_air_quality(
        pm25=85, pm10=120, no2=45, co=1.2, so2=25, 
        temperature=28, humidity=65, wind_speed=8
    )
    print(f"Predicted AQI: {aqi:.1f}")
    
    # Citizen Activity Prediction
    print("\nCITIZEN ACTIVITY PREDICTION")
    activity = predict_citizen_activity(
        population_density=8000, avg_age=35, workplace_count=25, 
        public_events=2, temperature=25, day_of_week=1
    )
    print(f"Prediction: {activity}")
    
    # Parking Availability Prediction
    print("\nPARKING AVAILABILITY PREDICTION")
    parking = predict_parking_availability(
        parking_capacity=150, occupied_slots=120, entry_rate=25, 
        exit_rate=15, time_of_day=2, weekday=1, nearby_events=1
    )
    print(f"Prediction: {parking}")
    
    print(f"\n{'SYSTEM OPERATIONAL':^50}")
    print("="*50)

if __name__ == "__main__":
    demo_predictions()