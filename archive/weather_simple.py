#!/usr/bin/env python3
import time
import requests
import random
import json

# Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

def get_mock_data():
    """Generate mock sensor data"""
    temperature = 20.0 + random.uniform(-5, 5)
    humidity = 55.0 + random.uniform(-10, 10)
    pressure = 1013.25 + random.uniform(-10, 10)
    return temperature, humidity, pressure

def send_data(temp, humidity, pressure):
    """Send data to server"""
    try:
        data = {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure, 1),
            'timestamp': int(time.time())
        }
        
        print(f"Sending: Temp={data['temperature']}°C, Humidity={data['humidity']}%, Pressure={data['pressure']}hPa")
        
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            print(f"✓ Data sent successfully: {response.text}")
            return True
        else:
            print(f"✗ Server error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    print("Weather Station Simple - Starting")
    print(f"Server: {SERVER_URL}")
    print(f"Interval: {INTERVAL} seconds")
    print("Using mock data (I2C sensors not available)\n")
    
    while True:
        try:
            # Get mock sensor data
            temp, humidity, pressure = get_mock_data()
            
            # Send to server
            success = send_data(temp, humidity, pressure)
            
            if not success:
                print("Retrying in next cycle...")
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        # Wait for next reading
        print(f"Waiting {INTERVAL} seconds...\n")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
