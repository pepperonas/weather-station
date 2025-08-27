import time
import requests
import board
import busio
from config import SERVER_URL, REQUEST_TIMEOUT, CONTINUOUS_MODE_INTERVAL

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

def read_sht30_raw(address=0x44):
    """Read SHT30 sensor (common in M5 modules)"""
    try:
        # SHT30 single shot measurement, high repeatability
        cmd = [0x2C, 0x06]
        
        # Write command
        i2c.writeto(address, bytes(cmd))
        time.sleep(0.5)  # Wait for measurement
        
        # Read 6 bytes
        data = bytearray(6)
        i2c.readfrom_into(address, data)
        
        # Parse temperature (first 3 bytes: msb, lsb, crc)
        temp_raw = (data[0] << 8) + data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Parse humidity (bytes 3-5: msb, lsb, crc)
        hum_raw = (data[3] << 8) + data[4]
        humidity = 100 * hum_raw / 65535.0
        
        return temperature, humidity
        
    except Exception as e:
        print(f"SHT30 read error: {e}")
        return None, None

def send_data(temp, humidity, pressure=None):
    try:
        data = {
            'temperature': temp,
            'humidity': humidity,
            'timestamp': int(time.time())
        }
        if pressure is not None:
            data['pressure'] = pressure
            
        response = requests.post(SERVER_URL, json=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            pressure_text = f", {pressure:.1f}hPa" if pressure else ""
            print(f"Data sent: {temp:.1f}°C, {humidity:.1f}%{pressure_text}")
        else:
            print(f"Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

def main():
    print("\nStarting continuous M5 weather station monitoring...")
    
    while True:
        try:
            # Read temperature and humidity
            temperature, humidity = read_sht30_raw()
            
            if temperature is not None and humidity is not None:
                print(f"Temp: {temperature:.1f}°C    Humidity: {humidity:.1f}%")
                send_data(temperature, humidity)
            else:
                print("Failed to read from sensor")
                
        except Exception as error:
            print(f"General error: {error}")
            
        # Wait before next reading
        time.sleep(CONTINUOUS_MODE_INTERVAL)

if __name__ == "__main__":
    main()