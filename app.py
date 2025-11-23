from flask import Flask, render_template, request, jsonify, make_response
import numpy as np
import random
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Import location services
from location_services import location_service, load_city_data, save_city_data, CityData
# Import API services
from api_services import api_service

app = Flask(__name__)

def predict_accident_risk(vehicle_density, avg_speed, road_condition, weather_condition, visibility, time_of_day):
    score = (vehicle_density/500)*0.4 + (1 - avg_speed/100)*0.3 + \
            (2 - road_condition)*0.1 + weather_condition*0.1 + \
            (1 - visibility/1000)*0.1
    
    if score < 0.4: return "Low"
    elif score < 0.7: return "Medium"
    else: return "High"

def predict_air_quality(pm25, pm10, no2, co, so2, temperature, humidity, wind_speed):
    aqi = (0.4*pm25 + 0.3*pm10 + 0.1*no2 + 15*co + 0.05*so2 - 
           0.2*wind_speed - 0.1*humidity)
    return max(0, min(500, aqi))

def predict_citizen_activity(population_density, avg_age, workplace_count, public_events, temperature, day_of_week):
    score = (population_density/15000)*0.4 + (workplace_count/50)*0.3 + \
            (public_events/5)*0.2 + (temperature/40)*0.1
    
    if score < 0.4: return "Low"
    elif score < 0.7: return "Moderate"
    else: return "High"

def predict_parking_availability(parking_capacity, occupied_slots, entry_rate, exit_rate, time_of_day, weekday, nearby_events):
    utilization = occupied_slots/parking_capacity
    inflow = entry_rate - exit_rate
    score = utilization + inflow/50 + nearby_events*0.5
    
    return "Full" if score > 1.2 else "Available"

def calculate_smart_city_score(air_quality, accident_risk, parking_status, activity_level):
    """Calculate overall smart city score (0-100)"""
    # Normalize inputs
    if isinstance(air_quality, str):
        aq_score = 100 - min(100, float(air_quality) * 0.2)  # Scale AQI (0-500) to 0-100
    else:
        aq_score = 100 - min(100, air_quality * 0.2)
    
    risk_scores = {"Low": 90, "Medium": 60, "High": 30}
    acc_score = risk_scores.get(accident_risk, 50)
    
    park_scores = {"Available": 90, "Full": 30}
    park_score = park_scores.get(parking_status, 50)
    
    activity_scores = {"Low": 70, "Moderate": 50, "High": 30}
    act_score = activity_scores.get(activity_level, 50)
    
    # Weighted average
    score = (aq_score * 0.4 + acc_score * 0.3 + 
             park_score * 0.2 + act_score * 0.1)
    
    return round(score, 1)

def get_city_status(score):
    """Convert score to status category"""
    if score >= 80:
        return {"status": "Excellent", "color": "#10B981", "icon": "fa-star", "label": "Good"}
    elif score >= 60:
        return {"status": "Good", "color": "#3B82F6", "icon": "fa-thumbs-up", "label": "Good"}
    elif score >= 40:
        return {"status": "Moderate", "color": "#F59E0B", "icon": "fa-info-circle", "label": "Moderate"}
    else:
        return {"status": "Critical", "color": "#EF4444", "icon": "fa-exclamation-triangle", "label": "Critical"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    module = data['module']
    
    try:
        result_data = {}
        
        if module == 'accident':
            result = predict_accident_risk(
                float(data['vehicle_density']), float(data['avg_speed']),
                int(data['road_condition']), int(data['weather_condition']),
                float(data['visibility']), int(data['time_of_day'])
            )
            result_data = {
                'prediction': result,
                'inputs': {
                    'vehicle_density': float(data['vehicle_density']),
                    'avg_speed': float(data['avg_speed']),
                    'road_condition': int(data['road_condition']),
                    'weather_condition': int(data['weather_condition']),
                    'visibility': float(data['visibility']),
                    'time_of_day': int(data['time_of_day'])
                }
            }
        elif module == 'air_quality':
            result = round(predict_air_quality(
                float(data['pm25']), float(data['pm10']), float(data['no2']),
                float(data['co']), float(data['so2']), float(data['temperature']),
                float(data['humidity']), float(data['wind_speed'])
            ), 1)
            result_data = {
                'prediction': result,
                'inputs': {
                    'pm25': float(data['pm25']),
                    'pm10': float(data['pm10']),
                    'no2': float(data['no2']),
                    'co': float(data['co']),
                    'so2': float(data['so2']),
                    'temperature': float(data['temperature']),
                    'humidity': float(data['humidity']),
                    'wind_speed': float(data['wind_speed'])
                }
            }
        elif module == 'activity':
            result = predict_citizen_activity(
                int(data['population_density']), int(data['avg_age']),
                int(data['workplace_count']), int(data['public_events']),
                float(data['temperature']), int(data['day_of_week'])
            )
            result_data = {
                'prediction': result,
                'inputs': {
                    'population_density': int(data['population_density']),
                    'avg_age': int(data['avg_age']),
                    'workplace_count': int(data['workplace_count']),
                    'public_events': int(data['public_events']),
                    'temperature': float(data['temperature']),
                    'day_of_week': int(data['day_of_week'])
                }
            }
        elif module == 'parking':
            result = predict_parking_availability(
                int(data['parking_capacity']), int(data['occupied_slots']),
                float(data['entry_rate']), float(data['exit_rate']),
                int(data['time_of_day']), int(data['weekday']), int(data['nearby_events'])
            )
            result_data = {
                'prediction': result,
                'inputs': {
                    'parking_capacity': int(data['parking_capacity']),
                    'occupied_slots': int(data['occupied_slots']),
                    'entry_rate': float(data['entry_rate']),
                    'exit_rate': float(data['exit_rate']),
                    'time_of_day': int(data['time_of_day']),
                    'weekday': int(data['weekday']),
                    'nearby_events': int(data['nearby_events'])
                }
            }
        
        return jsonify({'success': True, **result_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch_data', methods=['GET'])
def fetch_data():
    """Fetch data from APIs for a specific module"""
    module = request.args.get('module')
    city_name = request.args.get('city')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    if not city_name and (not lat or not lon):
        return jsonify({'error': 'City name or coordinates required'}), 400
    
    try:
        if module == 'air_quality':
            data = api_service.fetch_air_quality_data(city_name or '', lat, lon)
            return jsonify({'success': True, 'data': data})
        elif module == 'accident':
            weather_data = api_service.fetch_weather_data(city_name or '', lat, lon)
            traffic_data = api_service.fetch_traffic_data(city_name or '', lat, lon)
            return jsonify({
                'success': True,
                'data': {**weather_data, **traffic_data}
            })
        elif module == 'parking':
            data = api_service.fetch_parking_data(city_name or '', lat, lon)
            return jsonify({'success': True, 'data': data})
        elif module == 'activity':
            data = api_service.fetch_citizen_activity_data(city_name or '', lat, lon)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'error': 'Invalid module'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/city_score', methods=['GET'])
def get_city_score():
    """Get Smart City Score - optionally for a specific city"""
    city_name = request.args.get('city')
    
    if city_name:
        # Get city-specific metrics
        metrics = get_city_metrics(city_name)
        city = location_service.geocode(city_name)
        
        if city:
            # Run all models for this city
            all_metrics = run_all_models_for_city(city_name, city.latitude, city.longitude)
            score = calculate_smart_city_score(
                air_quality=all_metrics['air_quality'],
                accident_risk=all_metrics['accident_risk'],
                parking_status=all_metrics['parking_status'],
                activity_level=all_metrics['activity_level']
            )
            status = get_city_status(score)
            
            return jsonify({
                'score': score,
                'status': status,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'metrics': all_metrics,
                'city': city_name
            })
    
    # Default sample data
    sample_data = {
        'air_quality': 45,  # AQI
        'accident_risk': 'Medium',
        'parking_status': 'Available',
        'activity_level': 'Moderate'
    }
    
    score = calculate_smart_city_score(**sample_data)
    status = get_city_status(score)
    
    return jsonify({
        'score': score,
        'status': status,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'metrics': sample_data
    })

@app.route('/api/heatmap_data', methods=['GET'])
def get_heatmap_data():
    """Generate heatmap data based on city location and predictions"""
    city_name = request.args.get('city')
    lat = request.args.get('lat', type=float, default=28.6139)  # Default to New Delhi
    lon = request.args.get('lon', type=float, default=77.2090)
    
    # Get city if name provided
    if city_name:
        city = location_service.geocode(city_name)
        if city:
            lat, lon = city.latitude, city.longitude
    
    def generate_points(center_lat, center_lng, count, radius_km, intensity_range=(0.1, 1.0)):
        """Generate heatmap points with varying intensity"""
        points = []
        for _ in range(count):
            r = radius_km * (random.random() ** 0.5)
            theta = random.uniform(0, 2 * 3.14159)
            dx = r * 0.01 * random.choice([-1, 1]) * random.random()
            dy = r * 0.01 * random.choice([-1, 1]) * random.random()
            
            points.append([
                center_lat + dy,
                center_lng + dx,
                random.uniform(intensity_range[0], intensity_range[1])
            ])
        return points
    
    # Generate heatmap data based on city metrics if available
    if city_name:
        metrics = get_city_metrics(city_name)
        
        # Adjust intensity based on actual metrics
        aqi = metrics.get('air_quality', 50)
        air_intensity = (0.3, min(1.0, 0.3 + (aqi / 500) * 0.7))
        
        risk = metrics.get('accident_risk', 'Medium')
        risk_intensity = {'Low': (0.2, 0.5), 'Medium': (0.4, 0.7), 'High': (0.6, 1.0)}.get(risk, (0.4, 0.7))
        
        parking = metrics.get('parking_status', 'Available')
        parking_intensity = {'Available': (0.3, 0.6), 'Full': (0.7, 1.0)}.get(parking, (0.4, 0.7))
        
        activity = metrics.get('activity_level', 'Moderate')
        activity_intensity = {'Low': (0.2, 0.5), 'Moderate': (0.4, 0.7), 'High': (0.6, 1.0)}.get(activity, (0.4, 0.7))
        
        return jsonify({
            'accident_risk': generate_points(lat, lon, 100, 5, risk_intensity),
            'air_quality': generate_points(lat, lon, 150, 5, air_intensity),
            'parking': generate_points(lat, lon, 50, 5, parking_intensity),
            'crowd_density': generate_points(lat, lon, 200, 5, activity_intensity)
        })
    
    # Default heatmap data
    return jsonify({
        'accident_risk': generate_points(lat, lon, 100, 5),
        'air_quality': generate_points(lat, lon, 150, 5),
        'parking': generate_points(lat, lon, 50, 5),
        'crowd_density': generate_points(lat, lon, 200, 5)
    })

# Load city data
CITY_DATA = load_city_data()

def run_all_models_for_city(city_name: str, lat: float, lon: float, use_api: bool = True) -> Dict[str, Any]:
    """Run all ML models for a given city location"""
    # Fetch real data from APIs if available, otherwise use realistic simulated data
    if use_api:
        # Fetch Air Quality Data
        air_data = api_service.fetch_air_quality_data(city_name, lat, lon)
        pm25 = air_data.get('pm25', random.uniform(20, 120))
        pm10 = air_data.get('pm10', random.uniform(30, 150))
        no2 = air_data.get('no2', random.uniform(15, 80))
        co = air_data.get('co', random.uniform(0.5, 2.5))
        so2 = air_data.get('so2', random.uniform(10, 60))
        temperature = air_data.get('temperature', random.uniform(15, 35))
        humidity = air_data.get('humidity', random.uniform(40, 85))
        wind_speed = air_data.get('wind_speed', random.uniform(5, 25))
        aqi_from_api = air_data.get('aqi', None)
        
        # Use API AQI if available, otherwise calculate
        if aqi_from_api:
            aqi = aqi_from_api
        else:
            aqi = predict_air_quality(pm25, pm10, no2, co, so2, temperature, humidity, wind_speed)
        
        # Fetch Weather Data for Accident Risk
        weather_data = api_service.fetch_weather_data(city_name, lat, lon)
        weather_condition = weather_data.get('weather_condition', random.choice([0, 1, 2]))
        visibility = weather_data.get('visibility', random.uniform(2, 10)) * 1000  # Convert to meters
        
        # Fetch Traffic Data
        traffic_data = api_service.fetch_traffic_data(city_name, lat, lon)
        vehicle_density = traffic_data.get('vehicle_density', random.randint(100, 450))
        avg_speed = traffic_data.get('avg_speed', random.randint(30, 80))
        
        # Fetch Parking Data
        parking_data = api_service.fetch_parking_data(city_name, lat, lon)
        parking_capacity = parking_data.get('parking_capacity', random.randint(100, 300))
        occupied_slots = parking_data.get('occupied_slots', random.randint(50, parking_capacity))
        entry_rate = parking_data.get('entry_rate', random.uniform(10, 40))
        exit_rate = parking_data.get('exit_rate', random.uniform(8, 35))
        
        # Fetch Citizen Activity Data
        activity_data = api_service.fetch_citizen_activity_data(city_name, lat, lon)
        population_density = activity_data.get('population_density', random.randint(5000, 15000))
        avg_age = activity_data.get('avg_age', random.randint(25, 50))
        workplace_count = activity_data.get('workplace_count', random.randint(15, 50))
        public_events = activity_data.get('public_events', random.randint(0, 5))
        activity_temperature = weather_data.get('temperature', random.uniform(18, 32))
    else:
        # Use random data (fallback)
        pm25 = random.uniform(20, 120)
        pm10 = random.uniform(30, 150)
        no2 = random.uniform(15, 80)
        co = random.uniform(0.5, 2.5)
        so2 = random.uniform(10, 60)
        temperature = random.uniform(15, 35)
        humidity = random.uniform(40, 85)
        wind_speed = random.uniform(5, 25)
        aqi = predict_air_quality(pm25, pm10, no2, co, so2, temperature, humidity, wind_speed)
        
        vehicle_density = random.randint(100, 450)
        avg_speed = random.randint(30, 80)
        weather_condition = random.choice([0, 1, 2])
        visibility = random.randint(200, 900)
        
        parking_capacity = random.randint(100, 300)
        occupied_slots = random.randint(50, parking_capacity)
        entry_rate = random.uniform(10, 40)
        exit_rate = random.uniform(8, 35)
        
        population_density = random.randint(5000, 15000)
        avg_age = random.randint(25, 50)
        workplace_count = random.randint(15, 50)
        public_events = random.randint(0, 5)
        activity_temperature = random.uniform(18, 32)
    
    # Run ML models with fetched data
    road_condition = random.choice([0, 1, 2])  # Could be enhanced with road data API
    time_of_day = datetime.now().hour // 6  # 0-3 based on current hour
    parking_time_of_day = time_of_day
    weekday = datetime.now().weekday()
    day_of_week = weekday
    nearby_events = random.choice([0, 1])
    
    accident_risk = predict_accident_risk(vehicle_density, avg_speed, road_condition, 
                                         weather_condition, visibility, time_of_day)
    
    parking_status = predict_parking_availability(parking_capacity, occupied_slots, 
                                                   entry_rate, exit_rate, 
                                                   parking_time_of_day, weekday, nearby_events)
    
    activity_level = predict_citizen_activity(population_density, avg_age, workplace_count,
                                             public_events, activity_temperature, day_of_week)
    
    return {
        'air_quality': round(aqi, 1),
        'accident_risk': accident_risk,
        'parking_status': parking_status,
        'activity_level': activity_level,
        'location': {'lat': lat, 'lon': lon},
        'raw_data': {
            'air_quality': {
                'pm25': round(pm25, 1),
                'pm10': round(pm10, 1),
                'no2': round(no2, 1),
                'co': round(co, 2),
                'so2': round(so2, 1),
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(wind_speed, 1)
            },
            'accident_risk': {
                'vehicle_density': vehicle_density,
                'avg_speed': avg_speed,
                'road_condition': road_condition,
                'weather_condition': weather_condition,
                'visibility': round(visibility, 0)
            },
            'parking': {
                'parking_capacity': parking_capacity,
                'occupied_slots': occupied_slots,
                'entry_rate': round(entry_rate, 1),
                'exit_rate': round(exit_rate, 1)
            },
            'activity': {
                'population_density': population_density,
                'avg_age': avg_age,
                'workplace_count': workplace_count,
                'public_events': public_events
            }
        }
    }

def get_city_metrics(city_name: str) -> Dict[str, Any]:
    """Get or generate metrics for a city"""
    city_name = city_name.title()  # Normalize case
    
    # Get or create city data
    if city_name not in CITY_DATA:
        # Generate some random but realistic data for new cities
        CITY_DATA[city_name] = {
            'air_quality': random.uniform(30, 150),  # AQI
            'accident_risk': random.choice(['Low', 'Medium', 'High']),
            'parking_status': random.choice(['Available', 'Full']),
            'activity_level': random.choice(['Low', 'Moderate', 'High']),
            'energy_consumption': random.uniform(1000, 5000),  # MW
            'traffic_congestion': random.uniform(0.1, 0.9),  # 0-1 scale
            'last_updated': datetime.now().isoformat()
        }
        save_city_data(CITY_DATA)
        
    return CITY_DATA[city_name]

def generate_insights(city_name: str, metrics: Dict[str, Any]) -> Dict[str, str]:
    """Generate insights and recommendations based on city metrics"""
    insights = {
        'overview': "",
        'strengths': [],
        'concerns': [],
        'recommendations': []
    }
    
    # Air Quality Insights
    aqi = metrics.get('air_quality', 50)
    if aqi < 50:
        insights['strengths'].append("Excellent air quality (AQI < 50)")
    elif aqi < 100:
        insights['strengths'].append("Good air quality (AQI < 100)")
    else:
        insights['concerns'].append(f"Poor air quality (AQI: {aqi:.1f})")
        insights['recommendations'].append("• Implement stricter emissions controls\n• Increase green spaces and urban forests\n• Promote electric vehicle adoption\n• Enhance public transportation")
    
    # Accident Risk Insights
    risk = metrics.get('accident_risk', 'Low')
    if risk == 'Low':
        insights['strengths'].append("Low accident risk - safe road conditions")
    elif risk == 'High':
        insights['concerns'].append("High accident risk areas detected")
        insights['recommendations'].append("• Improve road safety measures in high-risk areas\n• Install traffic calming measures\n• Enhance street lighting and visibility\n• Implement intelligent traffic management systems")
    elif risk == 'Medium':
        insights['concerns'].append("Moderate accident risk - monitoring required")
        insights['recommendations'].append("• Monitor traffic patterns closely\n• Consider preventive safety measures")
    
    # Parking Insights
    parking = metrics.get('parking_status', 'Available')
    if parking == 'Available':
        insights['strengths'].append("Adequate parking availability")
    else:
        insights['concerns'].append("Parking spaces are full")
        insights['recommendations'].append("• Implement dynamic pricing for parking\n• Promote alternative transportation options\n• Expand parking capacity in high-demand areas\n• Develop smart parking guidance systems")
    
    # Activity Level Insights
    activity = metrics.get('activity_level', 'Moderate')
    if activity == 'High':
        insights['concerns'].append("High crowd density detected")
        insights['recommendations'].append("• Monitor crowd flow patterns\n• Ensure adequate public facilities\n• Plan for peak hour management")
    elif activity == 'Low':
        insights['strengths'].append("Low crowd density - comfortable urban environment")
    
    # Energy Consumption Insights (if available)
    energy = metrics.get('energy_consumption', 0)
    if energy > 4000:
        insights['concerns'].append(f"High energy consumption ({energy:.0f} MW)")
        insights['recommendations'].append("• Promote energy efficiency programs\n• Increase renewable energy sources\n• Implement smart grid technologies")
    
    # Traffic Congestion Insights (if available)
    congestion = metrics.get('traffic_congestion', 0)
    if congestion > 0.7:
        insights['concerns'].append(f"Severe traffic congestion ({congestion*100:.0f}%)")
        insights['recommendations'].append("• Improve public transportation\n• Implement smart traffic management\n• Promote carpooling and ride-sharing")
    
    # Generate overview
    if insights['strengths'] and not insights['concerns']:
        insights['overview'] = f"{city_name} is performing well across all major metrics. The city demonstrates strong urban management and sustainable practices."
    elif insights['concerns'] and not insights['strengths']:
        insights['overview'] = f"{city_name} has several areas that need immediate attention. Prioritize the recommended actions to improve overall city performance."
    else:
        insights['overview'] = f"{city_name} shows a mix of strengths and areas for improvement. Focus on addressing the concerns while maintaining current strengths."
    
    return insights

@app.route('/api/city/predict', methods=['GET'])
def predict_city():
    """Endpoint for location-based predictions - runs all models"""
    city_name = request.args.get('city')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    use_api = request.args.get('use_api', 'true').lower() == 'true'
    
    # Get city data
    city = None
    if city_name:
        city = location_service.geocode(city_name)
    elif lat is not None and lon is not None:
        city = location_service.reverse_geocode(lat, lon)
    
    if not city:
        return jsonify({
            'error': 'Could not determine city. Please provide a valid city name or coordinates.'
        }), 400
    
    # Run all ML models for this city
    all_metrics = run_all_models_for_city(city.name, city.latitude, city.longitude, use_api=use_api)
    
    # Update city data with latest predictions
    city_metrics = get_city_metrics(city.name)
    city_metrics.update({
        'air_quality': all_metrics['air_quality'],
        'accident_risk': all_metrics['accident_risk'],
        'parking_status': all_metrics['parking_status'],
        'activity_level': all_metrics['activity_level'],
        'last_updated': datetime.now().isoformat()
    })
    CITY_DATA[city.name] = city_metrics
    save_city_data(CITY_DATA)
    
    # Calculate overall smart city score
    score = calculate_smart_city_score(
        air_quality=all_metrics['air_quality'],
        accident_risk=all_metrics['accident_risk'],
        parking_status=all_metrics['parking_status'],
        activity_level=all_metrics['activity_level']
    )
    
    # Generate insights and recommendations
    insights = generate_insights(city.name, city_metrics)
    
    # Check for threshold breaches
    alerts = check_threshold_breaches(city.name, all_metrics)
    
    # Prepare response
    response = {
        'city': city.name,
        'location': {
            'lat': city.latitude,
            'lon': city.longitude
        },
        'metrics': all_metrics,
        'score': score,
        'status': get_city_status(score),
        'insights': insights,
        'alerts': alerts,
        'last_updated': city_metrics['last_updated']
    }
    
    return jsonify(response)

def check_threshold_breaches(city_name: str, metrics: Dict[str, Any]) -> list:
    """Check for threshold breaches and return alerts"""
    alerts = []
    
    # Air Quality Thresholds (AQI)
    aqi = metrics.get('air_quality', 0)
    if aqi > 150:
        alerts.append({
            'type': 'error',
            'message': f'⚠️ Critical: Air quality is unhealthy (AQI: {aqi:.1f})',
            'metric': 'air_quality',
            'value': aqi,
            'threshold': 150
        })
    elif aqi > 100:
        alerts.append({
            'type': 'warning',
            'message': f'⚠️ Warning: Air quality is moderate (AQI: {aqi:.1f})',
            'metric': 'air_quality',
            'value': aqi,
            'threshold': 100
        })
    
    # Accident Risk Thresholds
    risk = metrics.get('accident_risk', 'Low')
    if risk == 'High':
        alerts.append({
            'type': 'error',
            'message': '🚨 Critical: High accident risk detected in the area',
            'metric': 'accident_risk',
            'value': risk,
            'threshold': 'High'
        })
    elif risk == 'Medium':
        alerts.append({
            'type': 'warning',
            'message': '⚠️ Warning: Moderate accident risk in the area',
            'metric': 'accident_risk',
            'value': risk,
            'threshold': 'Medium'
        })
    
    # Parking Thresholds
    parking = metrics.get('parking_status', 'Available')
    if parking == 'Full':
        alerts.append({
            'type': 'warning',
            'message': '🚗 Warning: Parking spaces are full',
            'metric': 'parking',
            'value': parking,
            'threshold': 'Full'
        })
    
    # Activity Level Thresholds
    activity = metrics.get('activity_level', 'Moderate')
    if activity == 'High':
        alerts.append({
            'type': 'info',
            'message': '👥 High crowd density detected',
            'metric': 'activity',
            'value': activity,
            'threshold': 'High'
        })
    
    return alerts

def send_alert(message, level="info"):
    """Send a real-time alert"""
    # In a real app, this would use WebSockets or similar for real-time updates
    print(f"ALERT [{level.upper()}]: {message}")

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts for a city"""
    city_name = request.args.get('city')
    
    if not city_name:
        return jsonify({'alerts': []})
    
    metrics = get_city_metrics(city_name)
    alerts = check_threshold_breaches(city_name, metrics)
    
    return jsonify({'alerts': alerts})

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)