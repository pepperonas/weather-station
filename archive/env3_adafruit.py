#!/usr/bin/env python3
import time
import requests
import board
import adafruit_sht31d

# Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

# Initialize I2C and sensor
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_sht31d.SHT31D(i2c)
    print("✓ SHT31D sensor initialized")
except Exception as e:
    print(f"✗ Failed to initialize sensor: {e}")
    sensor = None

def read_sensor():
    """Read temperature and humidity from SHT31D"""
    if not sensor:
        return None, None
    
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        return temperature, humidity
    except Exception as e:
        print(f"Sensor read error: {e}")
        return None, None

def send_data(temp, humidity):
    """Send data to server"""
    try:
        data = {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'timestamp': int(time.time())
        }
        
        print(f"Sending: Temp={data['temperature']}°C, Humidity={data['humidity']}%")
        
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
    print("ENV III Weather Station (Adafruit) - Starting")
    print(f"Server: {SERVER_URL}")
    print(f"Interval: {INTERVAL} seconds\n")
    
    if not sensor:
        print("ERROR: No sensor available, exiting")
        return
    
    # Set sensor heater for better accuracy
    sensor.heater = False
    
    while True:
        try:
            # Read sensor
            temp, humidity = read_sensor()
            
            if temp is not None and humidity is not None:
                send_data(temp, humidity)
            else:
                print("Failed to read sensor")
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
