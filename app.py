from flask import Flask, render_template, request, jsonify
import numpy as np

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    module = data['module']
    
    try:
        if module == 'accident':
            result = predict_accident_risk(
                float(data['vehicle_density']), float(data['avg_speed']),
                int(data['road_condition']), int(data['weather_condition']),
                float(data['visibility']), int(data['time_of_day'])
            )
        elif module == 'air_quality':
            result = round(predict_air_quality(
                float(data['pm25']), float(data['pm10']), float(data['no2']),
                float(data['co']), float(data['so2']), float(data['temperature']),
                float(data['humidity']), float(data['wind_speed'])
            ), 1)
        elif module == 'activity':
            result = predict_citizen_activity(
                int(data['population_density']), int(data['avg_age']),
                int(data['workplace_count']), int(data['public_events']),
                float(data['temperature']), int(data['day_of_week'])
            )
        elif module == 'parking':
            result = predict_parking_availability(
                int(data['parking_capacity']), int(data['occupied_slots']),
                float(data['entry_rate']), float(data['exit_rate']),
                int(data['time_of_day']), int(data['weekday']), int(data['nearby_events'])
            )
        
        return jsonify({'success': True, 'prediction': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)