import time
import requests
import board
import busio
import adafruit_sht4x
import adafruit_bmp280
from config import SERVER_URL, REQUEST_TIMEOUT

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# Sensor setup - try both sensors
sht = None
bmp = None

try:
    sht = adafruit_sht4x.SHT4x(i2c)
    print("SHT4x sensor found at 0x44")
except Exception as e:
    print(f"SHT4x not found: {e}")

try:
    bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x70)
    print("BMP280 sensor found at 0x70")
except Exception as e:
    print(f"BMP280 not found: {e}")

# Server URL
url = SERVER_URL

def send_data(temp, humidity, pressure):
    try:
        data = {
            'temperature': temp,
            'humidity': humidity,
            'timestamp': int(time.time())
        }
        # Add pressure if available
        if pressure is not None:
            data['pressure'] = pressure
            
        response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            pressure_text = f", {pressure:.1f}hPa" if pressure else ""
            print(f"Data sent successfully: {temp:.1f}°C, {humidity:.1f}%{pressure_text}")
        else:
            print(f"Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

try:
    temperature = None
    humidity = None
    pressure = None
    
    # Read from SHT4x (Temperature & Humidity)
    if sht:
        try:
            temperature = sht.temperature
            humidity = sht.relative_humidity
            print(f"SHT4x: {temperature:.1f}°C, {humidity:.1f}%")
        except Exception as e:
            print(f"SHT4x read error: {e}")
    
    # Read from BMP280 (Pressure & Temperature)
    if bmp:
        try:
            bmp_temp = bmp.temperature
            pressure = bmp.pressure
            print(f"BMP280: {bmp_temp:.1f}°C, {pressure:.1f}hPa")
            
            # Use BMP temperature if SHT not available
            if temperature is None:
                temperature = bmp_temp
        except Exception as e:
            print(f"BMP280 read error: {e}")
    
    # Send data if we have temperature
    if temperature is not None:
        # Use dummy humidity if not available
        if humidity is None:
            humidity = 50.0  # Default value
            
        send_data(temperature, humidity, pressure)
    else:
        print("No temperature data available")
        
except Exception as error:
    print(f"General error: {error}")