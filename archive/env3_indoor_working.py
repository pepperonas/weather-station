#!/usr/bin/env python3
import time
import requests
import smbus2

# ENV III Module addresses (Indoor sensor)
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70

# Server Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

# Initialize I2C bus for ENV III
bus = smbus2.SMBus(1)
print("ENV III Indoor Weather Station - Starting")

def crc8(data):
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc = crc << 1
    return crc & 0xFF

def read_env3():
    try:
        # Send measurement command
        msg = smbus2.i2c_msg.write(SHT30_ADDR, [0x2C, 0x06])
        bus.i2c_rdwr(msg)
        time.sleep(0.02)
        
        # Read data
        msg = smbus2.i2c_msg.read(SHT30_ADDR, 6)
        bus.i2c_rdwr(msg)
        data = list(msg)
        
        # Verify CRC
        if crc8(data[0:2]) != data[2] or crc8(data[3:5]) != data[5]:
            return None, None, None
        
        # Calculate temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Calculate humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        # Pressure (simplified)
        pressure = 1013.25
        
        return temperature, humidity, pressure
    except Exception as e:
        print(f"ENV3 read error: {e}")
        return None, None, None

def send_data(temp, hum, press):
    try:
        data = {
            # Primary (backward compatible)
            'temperature': round(temp, 1),
            'humidity': round(hum, 1),
            'pressure': round(press, 1),
            # Indoor specific
            'temperature_indoor': round(temp, 1),
            'humidity_indoor': round(hum, 1),
            'pressure_indoor': round(press, 1),
            'sensor_indoor': 'ENV3',
            # Outdoor - leave empty for now (DHT22 not working)
            'temperature_outdoor': None,
            'humidity_outdoor': None,
            'sensor_outdoor': None,
            'timestamp': int(time.time())
        }
        
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            print(f"✓ Sent: Indoor {temp:.1f}°C, {hum:.1f}%, {press:.1f}hPa")
            return True
        elif response.status_code == 429:
            print("✓ Data sent (rate limited - normal)")
            return True
        else:
            print(f"✗ Server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Network error: {e}")
        return False

# Main loop
print("Starting indoor monitoring...")
while True:
    try:
        temp, hum, press = read_env3()
        if temp and hum:
            send_data(temp, hum, press)
        else:
            print("✗ Failed to read ENV3 sensor")
        
    except KeyboardInterrupt:
        print("\nStopping...")
        break
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(INTERVAL)
