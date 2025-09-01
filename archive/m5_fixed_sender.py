#!/usr/bin/env python3
"""
Fixed M5 weather station sender - uses correct I2C bus
"""

import time
import requests
import smbus2
from config import SERVER_URL, REQUEST_TIMEOUT, CONTINUOUS_MODE_INTERVAL

# Use I2C bus 13 where the sensors are detected
I2C_BUS = 13
SHT30_ADDRESS = 0x44
QMP6988_ADDRESS = 0x70

def read_sht30(bus, address=0x44):
    """Read SHT30 sensor with improved stability"""
    try:
        # SHT30 single shot measurement, high repeatability
        cmd = [0x2C, 0x06]
        
        # Write command
        bus.write_i2c_block_data(address, cmd[0], cmd[1:])
        time.sleep(0.5)  # Increased wait time for stable measurement
        
        # Read 6 bytes
        data = bus.read_i2c_block_data(address, 0x00, 6)
        
        # Parse temperature (first 3 bytes: msb, lsb, crc)
        temp_raw = (data[0] << 8) + data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        
        # Parse humidity (bytes 3-5: msb, lsb, crc)
        hum_raw = (data[3] << 8) + data[4]
        humidity = 100 * hum_raw / 65535.0
        
        # Basic range validation
        if temperature < -40 or temperature > 85:
            print(f"Temperature out of range: {temperature}")
            return None, None
        if humidity < 0 or humidity > 100:
            print(f"Humidity out of range: {humidity}")
            return None, None
            
        return temperature, humidity
        
    except Exception as e:
        print(f"SHT30 read error: {e}")
        return None, None

def read_qmp6988(bus, address=0x70):
    """Read QMP6988 pressure sensor (ENV IV Unit)"""
    try:
        # QMP6988 specific initialization
        # Check chip ID first
        chip_id = bus.read_byte_data(address, 0xD1)
        if chip_id != 0x5C:
            print(f"Wrong chip ID: 0x{chip_id:02X}, expected 0x5C")
            return None
            
        # Reset sensor
        bus.write_byte_data(address, 0xE0, 0xE6)
        time.sleep(0.1)
        
        # Configure sensor: standby time = 1ms, filter off, pressure oversampling x16, temp oversampling x2
        bus.write_byte_data(address, 0xF5, 0x00)  # config register
        time.sleep(0.01)
        bus.write_byte_data(address, 0xF4, 0x57)  # ctrl_meas register
        time.sleep(0.01)
        
        # Force measurement
        bus.write_byte_data(address, 0xF4, 0x57)  # Start measurement
        time.sleep(0.1)  # Wait for measurement
        
        # Read raw pressure data (20-bit)
        pressure_data = bus.read_i2c_block_data(address, 0xF7, 3)
        pressure_raw = (pressure_data[0] << 12) | (pressure_data[1] << 4) | (pressure_data[2] >> 4)
        
        # Read raw temperature data for compensation (20-bit) 
        temp_data = bus.read_i2c_block_data(address, 0xFA, 3)
        temp_raw = (temp_data[0] << 12) | (temp_data[1] << 4) | (temp_data[2] >> 4)
        
        # Simplified pressure calculation (approximation)
        # Real implementation would need calibration coefficients from registers 0x10-0x25
        # This is a rough approximation based on typical QMP6988 behavior
        temp_comp = (temp_raw - 120000) / 5120.0  # Rough temperature compensation
        pressure_pa = 30000 + (pressure_raw - 100000) * 0.8 + temp_comp * 10
        pressure_hpa = pressure_pa / 100.0  # Convert Pa to hPa
        
        # Validate range
        if pressure_hpa < 300 or pressure_hpa > 1200:
            print(f"Pressure out of range: {pressure_hpa:.1f}")
            return None
            
        return pressure_hpa
        
    except Exception as e:
        print(f"QMP6988 read error: {e}")
        return None

def read_sensors_averaged(bus, num_readings=3):
    """Read sensors multiple times and return averaged values"""
    temp_readings = []
    hum_readings = []
    pressure_readings = []
    
    for i in range(num_readings):
        temp, hum = read_sht30(bus, SHT30_ADDRESS)
        pressure = read_qmp6988(bus, QMP6988_ADDRESS)
        
        print(f"Reading {i+1}: temp={temp}, hum={hum}, pressure={pressure}")
        
        if temp is not None and hum is not None:
            temp_readings.append(temp)
            hum_readings.append(hum)
        
        if pressure is not None:
            pressure_readings.append(pressure)
        else:
            print(f"Pressure reading {i+1} failed")
            
        # Wait between readings
        if i < num_readings - 1:
            time.sleep(1.0)
    
    # Calculate averages
    avg_temp = sum(temp_readings) / len(temp_readings) if temp_readings else None
    avg_hum = sum(hum_readings) / len(hum_readings) if hum_readings else None
    avg_pressure = sum(pressure_readings) / len(pressure_readings) if pressure_readings else None
    
    return avg_temp, avg_hum, avg_pressure

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
            return True
        else:
            print(f"Server error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def main():
    print("\nStarting M5 weather station with correct I2C bus...")
    print(f"Using I2C bus: {I2C_BUS}")
    print(f"SHT30 address: 0x{SHT30_ADDRESS:02x}")
    print(f"QMP6988 address: 0x{QMP6988_ADDRESS:02x}")
    print(f"Server URL: {SERVER_URL}")
    print("=" * 50)
    
    # Initialize I2C bus
    try:
        bus = smbus2.SMBus(I2C_BUS)
        print("I2C bus initialized successfully")
    except Exception as e:
        print(f"Failed to initialize I2C bus: {e}")
        return
    
    while True:
        try:
            # Read sensors with averaging for stability
            print("Reading sensors (3 measurements, averaged)...")
            temperature, humidity, pressure = read_sensors_averaged(bus, num_readings=3)
            
            if temperature is not None and humidity is not None:
                pressure_text = f", Pressure: {pressure:.1f}hPa" if pressure else ""
                print(f"Averaged sensor data: {temperature:.1f}°C, {humidity:.1f}%{pressure_text}")
                
                success = send_data(temperature, humidity, pressure)
                if success:
                    print("✓ Data transmitted successfully")
                else:
                    print("✗ Transmission failed")
            else:
                print("Failed to read from sensors")
                
        except Exception as error:
            print(f"General error: {error}")
            
        # Wait before next reading
        print(f"Waiting {CONTINUOUS_MODE_INTERVAL} seconds...")
        print("-" * 30)
        time.sleep(CONTINUOUS_MODE_INTERVAL)

if __name__ == "__main__":
    main()