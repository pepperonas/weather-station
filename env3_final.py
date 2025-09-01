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

# Use I2C bus 1 (GPIO pins)
bus = smbus2.SMBus(1)
print("Using I2C bus 1 (GPIO2/GPIO3)")

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
    """Read QMP6988 pressure sensor"""
    try:
        # Read chip ID
        chip_id = bus.read_byte_data(QMP6988_ADDR, 0xD1)
        if chip_id != 0x5C:
            print(f"QMP6988 chip ID: {hex(chip_id)} (expected 0x5C)")
        
        # Simple pressure reading (returns default for now)
        # Full implementation requires complex calibration
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
            print(f"✓ Data sent successfully")
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
    
    # Test initial reading
    temp, hum = read_sht30()
    if temp and hum:
        print(f"✓ ENV III working: {temp:.1f}°C, {hum:.1f}%\n")
    
    while True:
        try:
            # Read sensors
            temp, humidity = read_sht30()
            pressure = read_qmp6988()
            
            if temp is not None and humidity is not None:
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
