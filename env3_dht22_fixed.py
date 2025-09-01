#!/usr/bin/env python3
import time
import requests
import smbus2
import struct
import os

# Try different DHT22 libraries
try:
    import board
    import adafruit_dht
    CIRCUITPYTHON_DHT = True
except ImportError:
    CIRCUITPYTHON_DHT = False
    try:
        import Adafruit_DHT
        ADAFRUIT_DHT = True
    except ImportError:
        ADAFRUIT_DHT = False

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

# Initialize DHT22
if CIRCUITPYTHON_DHT:
    print("Using CircuitPython DHT library")
    dht22 = adafruit_dht.DHT22(board.D4, use_pulseio=False)
elif ADAFRUIT_DHT:
    print("Using legacy Adafruit DHT library")
else:
    print("No DHT22 library available - using mock data")

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
        temp_data = data[0:2]
        temp_crc = data[2]
        if crc8(temp_data) != temp_crc:
            print("SHT30 temperature CRC error")
            return None, None
        
        # Check CRC for humidity
        hum_data = data[3:5]
        hum_crc = data[5]
        if crc8(hum_data) != hum_crc:
            print("SHT30 humidity CRC error")
            return None, None
        
        # Convert temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + 175 * temp_raw / 65535.0
        
        # Convert humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        return temperature, humidity
        
    except Exception as e:
        print(f"SHT30 read error: {e}")
        return None, None

def read_qmp6988():
    """Read QMP6988 pressure sensor from ENV III (Indoor)"""
    try:
        # Read calibration coefficients
        calib_data = []
        for addr in range(0xA0, 0xB0):
            data = bus.read_byte_data(QMP6988_ADDR, addr)
            calib_data.append(data)
        
        # Reset and configure
        bus.write_byte_data(QMP6988_ADDR, 0xE0, 0xB6)  # Reset
        time.sleep(0.01)
        
        # Configure oversampling and mode
        bus.write_byte_data(QMP6988_ADDR, 0xF4, 0x27)  # Ctrl meas
        bus.write_byte_data(QMP6988_ADDR, 0xF5, 0x00)  # Config
        
        time.sleep(0.1)  # Wait for measurement
        
        # Read pressure data
        data = bus.read_i2c_block_data(QMP6988_ADDR, 0xF7, 3)
        pressure_raw = (data[0] << 16) | (data[1] << 8) | data[2]
        pressure_raw = pressure_raw >> 4  # 20-bit value
        
        # Simple pressure conversion (approximate)
        pressure_hpa = pressure_raw / 16.0
        
        return pressure_hpa
        
    except Exception as e:
        print(f"QMP6988 read error: {e}")
        return None

def read_dht22():
    """Read DHT22 temperature and humidity sensor (Outdoor)"""
    if CIRCUITPYTHON_DHT:
        try:
            # Try multiple times
            for attempt in range(3):
                try:
                    temperature = dht22.temperature
                    humidity = dht22.humidity
                    
                    if temperature is not None and humidity is not None:
                        return temperature, humidity
                except RuntimeError as e:
                    if "DHT sensor not found" in str(e):
                        print(f"DHT22 attempt {attempt + 1}: Sensor not found")
                    else:
                        print(f"DHT22 attempt {attempt + 1}: {e}")
                    time.sleep(2)
            
            print("DHT22: All attempts failed")
            return None, None
            
        except Exception as e:
            print(f"DHT22 CircuitPython error: {e}")
            return None, None
    
    elif ADAFRUIT_DHT:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_GPIO)
            return temperature, humidity
        except Exception as e:
            print(f"DHT22 legacy library error: {e}")
            return None, None
    
    else:
        print("No DHT22 library available")
        return None, None

def send_data_to_server(indoor_temp, indoor_humidity, indoor_pressure, outdoor_temp, outdoor_humidity):
    """Send sensor data to the server"""
    try:
        data = {
            "indoor": {
                "temperature": round(indoor_temp, 1) if indoor_temp is not None else None,
                "humidity": round(indoor_humidity, 1) if indoor_humidity is not None else None,
                "pressure": round(indoor_pressure, 1) if indoor_pressure is not None else None
            },
            "outdoor": {
                "temperature": round(outdoor_temp, 1) if outdoor_temp is not None else None,
                "humidity": round(outdoor_humidity, 1) if outdoor_humidity is not None else None
            }
        }
        
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            print("✅ Data sent successfully")
            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    print("Starting Weather Station with ENV III (Indoor) + DHT22 (Outdoor)")
    print(f"Sending data to: {SERVER_URL}")
    
    while True:
        try:
            # Read indoor sensors (ENV III)
            indoor_temp, indoor_humidity = read_sht30()
            indoor_pressure = read_qmp6988()
            
            # Read outdoor sensor (DHT22)
            outdoor_temp, outdoor_humidity = read_dht22()
            
            # Display readings
            print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
            if indoor_temp is not None:
                print(f"🏠 Indoor: {indoor_temp:.1f}°C, {indoor_humidity:.1f}%, {indoor_pressure:.1f}hPa")
            else:
                print("🏠 Indoor: ENV III sensor error")
            
            if outdoor_temp is not None:
                print(f"🌤️  Outdoor: {outdoor_temp:.1f}°C, {outdoor_humidity:.1f}%")
            else:
                print("🌤️  Outdoor: DHT22 sensor error")
            
            # Send data to server
            send_data_to_server(indoor_temp, indoor_humidity, indoor_pressure, outdoor_temp, outdoor_humidity)
            
        except KeyboardInterrupt:
            print("\nShutting down weather station...")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
