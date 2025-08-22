#!/usr/bin/env python3
"""
Mock weather station sender for testing VPS connection
Sends simulated sensor data to the VPS
"""

import time
import requests
import random
from config import SERVER_URL, REQUEST_TIMEOUT, CONTINUOUS_MODE_INTERVAL

def generate_mock_data():
    """Generate realistic mock weather data"""
    # Simulate typical indoor conditions with some variation
    temperature = round(random.uniform(18.0, 25.0), 1)
    humidity = round(random.uniform(40.0, 70.0), 1)
    pressure = round(random.uniform(1010.0, 1025.0), 1)
    
    return temperature, humidity, pressure

def send_data(temp, humidity, pressure=None):
    try:
        data = {
            'temperature': temp,
            'humidity': humidity,
            'timestamp': int(time.time())
        }
        if pressure is not None:
            data['pressure'] = pressure
            
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            pressure_text = f", {pressure:.1f}hPa" if pressure else ""
            print(f"Data sent successfully: {temp:.1f}°C, {humidity:.1f}%{pressure_text}")
            return True
        else:
            print(f"Server error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def main():
    print("Starting mock weather station for VPS testing...")
    print(f"Sending data to: {SERVER_URL}")
    print(f"Interval: {CONTINUOUS_MODE_INTERVAL} seconds")
    print("=" * 50)
    
    while True:
        try:
            temperature, humidity, pressure = generate_mock_data()
            
            print(f"Generated: {temperature:.1f}°C, {humidity:.1f}%, {pressure:.1f}hPa")
            success = send_data(temperature, humidity, pressure)
            
            if not success:
                print("Failed to send data, retrying next cycle...")
                
        except Exception as error:
            print(f"General error: {error}")
            
        # Wait before next reading
        print(f"Waiting {CONTINUOUS_MODE_INTERVAL} seconds...")
        print("-" * 30)
        time.sleep(CONTINUOUS_MODE_INTERVAL)

if __name__ == "__main__":
    main()