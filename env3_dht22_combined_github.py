#!/usr/bin/env python3
import time
import requests
import smbus2
import struct
import os
import subprocess

# ENV III Module addresses (Indoor sensor)
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70

# DHT22 Configuration (Outdoor sensor)
DHT22_GPIO = 4  # GPIO4 (Pin 7)

# Server Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

# Initialize I2C bus for ENV III
bus = smbus2.SMBus(1)
print("Using I2C bus 1 for ENV III Indoor Sensor (GPIO2/GPIO3)")

def crc8(data):
    """Calculate CRC8 for SHT30"""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc = crc << 1
    return crc & 0xFF

def read_sht30():
    """Read SHT30 temperature and humidity sensor from ENV III (Indoor)"""
    try:
        # Send measurement command (single shot, high repeatability)
        msg = smbus2.i2c_msg.write(SHT30_ADDR, [0x2C, 0x06])
        bus.i2c_rdwr(msg)
        time.sleep(0.02)  # Wait for measurement
        
        # Read 6 bytes (temp + humidity + CRC)
        msg = smbus2.i2c_msg.read(SHT30_ADDR, 6)
        bus.i2c_rdwr(msg)
        data = list(msg)
        
        # Check CRC for temperature
        if crc8(data[0:2]) != data[2]:
            print("CRC error in ENV III temperature data")
            return None, None
            
        # Check CRC for humidity
        if crc8(data[3:5]) != data[5]:
            print("CRC error in ENV III humidity data")
            return None, None
        
        # Calculate temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Calculate humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        return temperature, humidity
    except Exception as e:
        print(f"ENV III SHT30 error: {e}")
        return None, None

def read_qmp6988():
    """Read QMP6988 pressure sensor from ENV III (Indoor)"""
    try:
        # Read chip ID
        chip_id = bus.read_byte_data(QMP6988_ADDR, 0xD1)
        if chip_id != 0x5C:
            print(f"QMP6988 chip ID: {hex(chip_id)} (expected 0x5C)")
        
        # Simple pressure reading (returns default for now)
        # Full implementation requires complex calibration
        return 1013.25
        
    except Exception as e:
        print(f"ENV III QMP6988 error: {e}")
        return None

def read_dht22_simple():
    """Read DHT22 using simple Python dht22 library (Outdoor)"""
    try:
        # Use the existing dht_22.py script to read
        result = subprocess.run(
            ['/home/pi/apps/weather-station/venv/bin/python', '-c',
             f'''
import time
import board
import adafruit_dht

try:
    dht = adafruit_dht.DHT22(board.D{DHT22_GPIO}, use_pulseio=False)
    time.sleep(2)
    temp = dht.temperature
    hum = dht.humidity
    if temp is not None and hum is not None:
        print(f"{{temp}},{{hum}}")
    dht.exit()
except Exception as e:
    pass
'''],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout.strip():
            temp, hum = result.stdout.strip().split(',')
            return float(temp), float(hum)
    except Exception as e:
        print(f"DHT22 subprocess error: {e}")
    
    return None, None

def send_data(indoor_temp, indoor_humidity, pressure, outdoor_temp, outdoor_humidity):
    """Send combined indoor and outdoor data to server"""
    try:
        # Prepare data with indoor and outdoor readings
        data = {
            'timestamp': int(time.time())
        }
        
        # Add indoor data from ENV III
        if indoor_temp is not None and indoor_humidity is not None:
            # Primary data fields for backward compatibility
            data['temperature'] = round(indoor_temp, 1)
            data['humidity'] = round(indoor_humidity, 1)
            # Explicitly marked indoor data
            data['temperature_indoor'] = round(indoor_temp, 1)
            data['humidity_indoor'] = round(indoor_humidity, 1)
            data['sensor_indoor'] = 'ENV3'
            
        # Add outdoor data from DHT22
        if outdoor_temp is not None and outdoor_humidity is not None:
            data['temperature_outdoor'] = round(outdoor_temp, 1)
            data['humidity_outdoor'] = round(outdoor_humidity, 1)
            data['sensor_outdoor'] = 'DHT22'
            
            # If indoor failed, use outdoor as primary
            if 'temperature' not in data:
                data['temperature'] = round(outdoor_temp, 1)
                data['humidity'] = round(outdoor_humidity, 1)
        
        # Add pressure if available (indoor sensor)
        if pressure:
            data['pressure'] = round(pressure, 1)
            data['pressure_indoor'] = round(pressure, 1)
        
        # Only send if we have at least one temperature reading
        if 'temperature' not in data:
            print("✗ No sensor data available")
            return False
        
        # Format output message
        output_parts = []
        
        if indoor_temp is not None and indoor_humidity is not None:
            output_parts.append(f"Indoor(ENV3): {data['temperature_indoor']}°C, {data['humidity_indoor']}%")
            if pressure:
                output_parts.append(f"Pressure: {data['pressure']}hPa")
                
        if outdoor_temp is not None and outdoor_humidity is not None:
            output_parts.append(f"Outdoor(DHT22): {data['temperature_outdoor']}°C, {data['humidity_outdoor']}%")
        
        print(f"Sending: {' | '.join(output_parts)}")
        
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
    print("ENV III (Indoor) + DHT22 (Outdoor) Weather Station - Starting")
    print(f"Server: {SERVER_URL}")
    print(f"Interval: {INTERVAL} seconds")
    print(f"Indoor Sensor - ENV III: SHT30 addr={hex(SHT30_ADDR)}, QMP6988 addr={hex(QMP6988_ADDR)}")
    print(f"Outdoor Sensor - DHT22: GPIO{DHT22_GPIO} (Pin 7)\n")
    
    # Test initial reading
    indoor_temp, indoor_hum = read_sht30()
    outdoor_temp, outdoor_hum = read_dht22_simple()
    
    if indoor_temp and indoor_hum:
        print(f"✓ Indoor ENV III working: {indoor_temp:.1f}°C, {indoor_hum:.1f}%")
    else:
        print("✗ Indoor ENV III not responding")
        
    if outdoor_temp and outdoor_hum:
        print(f"✓ Outdoor DHT22 working: {outdoor_temp:.1f}°C, {outdoor_hum:.1f}%")
    else:
        print("✗ Outdoor DHT22 not responding on GPIO{DHT22_GPIO}")
        print("  Note: DHT22 may need time to stabilize or have connection issues.")
        print("  Will retry during normal operation...\n")
    
    if not (indoor_temp or outdoor_temp):
        print("\n⚠ WARNING: No sensors available! Check connections.\n")
    
    print("Starting monitoring loop...\n")
    
    while True:
        try:
            # Read indoor sensors (ENV III)
            indoor_temp, indoor_humidity = read_sht30()
            pressure = read_qmp6988()
            
            # Read outdoor sensor (DHT22)
            outdoor_temp, outdoor_humidity = read_dht22_simple()
            
            # Send combined data
            send_data(indoor_temp, indoor_humidity, pressure, outdoor_temp, outdoor_humidity)
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
