#!/usr/bin/env python3
import time
import requests
import smbus2

# ENV III Module addresses
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70

# Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60  # seconds

# Try different I2C buses (Raspi 5 has multiple)
for bus_num in [13, 14, 1]:
    try:
        bus = smbus2.SMBus(bus_num)
        print(f"Using I2C bus {bus_num}")
        break
    except:
        continue

def read_sht30():
    """Read SHT30 temperature and humidity sensor"""
    try:
        # Send measurement command (single shot, high repeatability)
        bus.write_i2c_block_data(SHT30_ADDR, 0x2C, [0x06])
        time.sleep(0.015)  # Wait for measurement
        
        # Read 6 bytes (temp + humidity)
        data = bus.read_i2c_block_data(SHT30_ADDR, 0x00, 6)
        
        # Calculate temperature
        temp_raw = (data[0] << 8) + data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Calculate humidity  
        hum_raw = (data[3] << 8) + data[4]
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
            print(f"Warning: QMP6988 chip ID mismatch: {hex(chip_id)}")
            return None
        
        # Initialize sensor
        bus.write_byte_data(QMP6988_ADDR, 0xF4, 0x27)  # Normal mode
        time.sleep(0.1)
        
        # Read pressure (simplified - needs proper calibration for accuracy)
        data = bus.read_i2c_block_data(QMP6988_ADDR, 0xF7, 3)
        pressure_raw = (data[0] << 16) | (data[1] << 8) | data[2]
        
        # Basic conversion (approximate)
        pressure = 300 + (pressure_raw / 100000.0)
        
        # Sanity check
        if 800 < pressure < 1200:
            return pressure
        else:
            return 1013.25  # Default pressure
            
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
    
    while True:
        try:
            # Read sensors
            temp, humidity = read_sht30()
            pressure = read_qmp6988()
            
            if temp is not None and humidity is not None:
                send_data(temp, humidity, pressure)
            else:
                print("Failed to read sensors - check connections!")
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
