#!/usr/bin/env python3
import time
import requests
import random
import math

# Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

class RealisticSensor:
    def __init__(self):
        self.base_temp = 22.0
        self.base_humidity = 55.0
        self.base_pressure = 1013.25
        self.time_offset = 0
        
    def get_data(self):
        """Generate realistic sensor data with smooth changes"""
        # Simulate daily temperature variation
        hour = (time.time() / 3600) % 24
        daily_variation = 3 * math.sin((hour - 6) * math.pi / 12)  # Peak at 18:00
        
        # Small random variations
        temp_noise = random.gauss(0, 0.2)
        hum_noise = random.gauss(0, 0.5)
        press_noise = random.gauss(0, 0.3)
        
        temperature = self.base_temp + daily_variation + temp_noise
        humidity = max(30, min(80, self.base_humidity + hum_noise))
        pressure = self.base_pressure + press_noise
        
        # Slowly drift base values
        self.base_temp += random.gauss(0, 0.01)
        self.base_humidity += random.gauss(0, 0.02)
        self.base_pressure += random.gauss(0, 0.01)
        
        return temperature, humidity, pressure

sensor = RealisticSensor()

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
            print(f"✓ Data sent successfully")
            return True
        else:
            print(f"✗ Server error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Network error: {e}")
        return False

def main():
    print("Weather Station (Realistic Simulation) - Starting")
    print(f"Server: {SERVER_URL}")
    print(f"Interval: {INTERVAL} seconds")
    print("Note: Using simulated data - ENV III module not responding\n")
    
    while True:
        try:
            # Get simulated sensor data
            temp, humidity, pressure = sensor.get_data()
            
            # Send to server
            send_data(temp, humidity, pressure)
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
