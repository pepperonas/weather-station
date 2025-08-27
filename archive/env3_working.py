#!/usr/bin/env python3
import time
import requests
import smbus2
import struct

# ENV III Module addresses
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70

# Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

# Use I2C bus 13 (where we found the devices)
bus = smbus2.SMBus(13)
print("Using I2C bus 13")

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
    """Read SHT30 temperature and humidity sensor"""
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
            print("CRC error in temperature data")
            return None, None
            
        # Check CRC for humidity
        if crc8(data[3:5]) != data[5]:
            print("CRC error in humidity data")
            return None, None
        
        # Calculate temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Calculate humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        return temperature, humidity
    except Exception as e:
        print(f"SHT30 error: {e}")
        return None, None

def read_qmp6988():
    """Read QMP6988 pressure sensor (simplified)"""
    try:
        # For now, just return a default pressure value
        # Full QMP6988 implementation requires complex calibration
        return 1013.25
    except Exception as e:
        print(f"QMP6988 error: {e}")
        return None

def send_data(temp, humidity, pressure):
    """Send data to server"""
    try:
        data = {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'timestamp': int(time.time())
        }
        
        if pressure:
            data['pressure'] = round(pressure, 1)
        
        print(f"Sending: Temp={data['temperature']}°C, Humidity={data['humidity']}%" + 
              (f", Pressure={data.get('pressure', 'N/A')}hPa" if pressure else ""))
        
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            print(f"✓ Data sent successfully: {response.text}")
            return True
        else:
            print(f"✗ Server error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Network error: {e}")
        return False

def main():
    print("ENV III Weather Station - Starting")
    print(f"Server: {SERVER_URL}")
    print(f"Interval: {INTERVAL} seconds")
    print(f"SHT30 addr: {hex(SHT30_ADDR)}, QMP6988 addr: {hex(QMP6988_ADDR)}\n")
    
    # Store last values for smoothing
    last_temp = None
    last_hum = None
    
    while True:
        try:
            # Read sensors
            temp, humidity = read_sht30()
            pressure = read_qmp6988()
            
            if temp is not None and humidity is not None:
                # Smooth out big jumps
                if last_temp is not None:
                    if abs(temp - last_temp) > 10:
                        print(f"Temperature jump too high ({temp:.1f} vs {last_temp:.1f}), using average")
                        temp = (temp + last_temp) / 2
                    if abs(humidity - last_hum) > 20:
                        print(f"Humidity jump too high ({humidity:.1f} vs {last_hum:.1f}), using average")
                        humidity = (humidity + last_hum) / 2
                
                last_temp = temp
                last_hum = humidity
                send_data(temp, humidity, pressure)
            else:
                print("Failed to read sensors")
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
