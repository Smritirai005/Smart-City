import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# 1. Accident Risk Analysis Dataset
df1 = pd.DataFrame({
    'vehicle_density': np.random.randint(50, 500, 1000),
    'avg_speed': np.random.randint(20, 100, 1000),
    'road_condition': np.random.choice([0,1,2], 1000, p=[0.2,0.5,0.3]),
    'weather_condition': np.random.choice([0,1,2], 1000, p=[0.5,0.3,0.2]),
    'visibility': np.random.randint(50, 1000, 1000),
    'time_of_day': np.random.choice([0,1,2,3], 1000)
})

risk = []
for i in range(1000):
    score = (df1.loc[i,'vehicle_density']/500)*0.4 + (1 - df1.loc[i,'avg_speed']/100)*0.3 + \
            (2 - df1.loc[i,'road_condition'])*0.1 + (df1.loc[i,'weather_condition'])*0.1 + \
            (1 - df1.loc[i,'visibility']/1000)*0.1
    if score < 0.4: risk.append('Low')
    elif score < 0.7: risk.append('Medium')
    else: risk.append('High')
df1['accident_risk'] = risk
df1.to_csv("accident_risk.csv", index=False)

# 2. Air Quality Prediction Dataset
df2 = pd.DataFrame({
    'pm25': np.random.uniform(10, 300, 1000),
    'pm10': np.random.uniform(20, 400, 1000),
    'no2': np.random.uniform(10, 150, 1000),
    'co': np.random.uniform(0.2, 3.0, 1000),
    'so2': np.random.uniform(5, 80, 1000),
    'temperature': np.random.uniform(10, 40, 1000),
    'humidity': np.random.uniform(30, 90, 1000),
    'wind_speed': np.random.uniform(0, 30, 1000)
})
df2['aqi'] = (0.4*df2['pm25'] + 0.3*df2['pm10'] + 0.1*df2['no2'] + 
              15*df2['co'] + 0.05*df2['so2'] - 0.2*df2['wind_speed'] - 
              0.1*df2['humidity'] + np.random.normal(0,10,1000))
df2['aqi'] = df2['aqi'].clip(0, 500)
df2.to_csv("air_quality.csv", index=False)

# 3. Citizen Activity Monitoring Dataset
df3 = pd.DataFrame({
    'population_density': np.random.randint(500, 15000, 1000),
    'avg_age': np.random.randint(18, 60, 1000),
    'workplace_count': np.random.randint(0, 50, 1000),
    'public_events': np.random.randint(0, 5, 1000),
    'temperature': np.random.uniform(15, 40, 1000),
    'day_of_week': np.random.randint(0, 7, 1000)
})

activity = []
for i in range(1000):
    score = (df3.loc[i,'population_density']/15000)*0.4 + (df3.loc[i,'workplace_count']/50)*0.3 + \
            (df3.loc[i,'public_events']/5)*0.2 + (df3.loc[i,'temperature']/40)*0.1
    if score < 0.4: activity.append('Low')
    elif score < 0.7: activity.append('Moderate')
    else: activity.append('High')
df3['activity_level'] = activity
df3.to_csv("citizen_activity.csv", index=False)

# 4. Smart Parking Dataset
df4 = pd.DataFrame({
    'parking_capacity': np.random.randint(50, 300, 1000),
    'occupied_slots': np.random.randint(0, 300, 1000),
    'entry_rate': np.random.uniform(5, 50, 1000),
    'exit_rate': np.random.uniform(0, 40, 1000),
    'time_of_day': np.random.choice([0,1,2,3], 1000),
    'weekday': np.random.randint(0, 7, 1000),
    'nearby_events': np.random.choice([0,1], 1000, p=[0.8,0.2])
})

availability = []
for i in range(1000):
    utilization = df4.loc[i,'occupied_slots']/df4.loc[i,'parking_capacity']
    inflow = df4.loc[i,'entry_rate'] - df4.loc[i,'exit_rate']
    score = utilization + inflow/50 + df4.loc[i,'nearby_events']*0.5
    if score > 1.2: availability.append('Full')
    else: availability.append('Available')
df4['availability'] = availability
df4.to_csv("smart_parking.csv", index=False)

print("All datasets created successfully!")
print(f"accident_risk.csv: {len(df1)} rows")
print(f"air_quality.csv: {len(df2)} rows") 
print(f"citizen_activity.csv: {len(df3)} rows")
print(f"smart_parking.csv: {len(df4)} rows")