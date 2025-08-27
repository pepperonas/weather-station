#!/usr/bin/env python3
import time
import smbus2
import requests

# ENV III addresses
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70
bus = smbus2.SMBus(1)

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
        
        # Check CRC
        if crc8(data[0:2]) != data[2]:
            return None, None
        if crc8(data[3:5]) != data[5]:
            return None, None
        
        # Calculate values
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        return temperature, humidity
    except Exception as e:
        print(f'ENV3 Error: {e}')
        return None, None

print('Testing ENV3 Indoor Sensor...')
for i in range(3):
    temp, hum = read_env3()
    if temp and hum:
        print(f'ENV3 SUCCESS: {temp:.1f}°C, {hum:.1f}%')
        
        # Test sending to server
        data = {
            'temperature': round(temp, 1),
            'humidity': round(hum, 1),
            'temperature_indoor': round(temp, 1),
            'humidity_indoor': round(hum, 1),
            'sensor_indoor': 'ENV3',
            'timestamp': int(time.time())
        }
        
        try:
            response = requests.post(
                'https://mrx3k1.de/weather-tracker/weather-tracker',
                json=data,
                timeout=10
            )
            print(f'Server response: {response.status_code}')
            break
        except Exception as e:
            print(f'Network error: {e}')
    else:
        print(f'ENV3 attempt {i+1}: Failed')
    time.sleep(1)

print('ENV3 test completed')
