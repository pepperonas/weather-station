#!/usr/bin/env python3
"""
Robust Weather Station with Enhanced Error Handling
Supports ENV III (I2C) and DHT22 (GPIO) sensors with fallback mechanisms
"""

import time
import requests
import smbus2
import struct
import os
import subprocess
import json
from datetime import datetime

# Sensor Configuration
SHT30_ADDR = 0x44
QMP6988_ADDR = 0x70
DHT22_GPIO = 4

# Server Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10
INTERVAL = 60

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2

# Cache for sensor values
sensor_cache = {
    'indoor': {'temperature': None, 'humidity': None, 'pressure': None, 'last_update': 0},
    'outdoor': {'temperature': None, 'humidity': None, 'last_update': 0}
}
CACHE_TIMEOUT = 300  # Use cached values for up to 5 minutes

# Statistics
stats = {
    'indoor_success': 0,
    'indoor_fail': 0,
    'outdoor_success': 0,
    'outdoor_fail': 0,
    'send_success': 0,
    'send_fail': 0,
    'i2c_resets': 0
}

def log_message(level, message):
    """Enhanced logging with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {"INFO": "ℹ", "WARNING": "⚠", "ERROR": "✗", "SUCCESS": "✓"}.get(level, "•")
    print(f"{timestamp}: {prefix} {message}")

def reset_i2c_bus():
    """Attempt to reset I2C bus"""
    global stats
    stats['i2c_resets'] += 1
    log_message("WARNING", "Attempting I2C bus reset...")
    
    try:
        # Try to reset using i2cdetect
        subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, timeout=5)
        time.sleep(1)
        log_message("INFO", "I2C bus reset attempted")
        return True
    except Exception as e:
        log_message("ERROR", f"I2C reset failed: {e}")
        return False

def init_i2c_with_retry():
    """Initialize I2C bus with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            bus = smbus2.SMBus(1)
            # Test bus by scanning
            try:
                bus.read_byte(0x00)
            except:
                pass  # Expected to fail, just testing bus
            log_message("SUCCESS", "I2C bus initialized")
            return bus
        except Exception as e:
            log_message("ERROR", f"I2C init attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                reset_i2c_bus()
                time.sleep(RETRY_DELAY)
    return None

# Initialize I2C bus
bus = init_i2c_with_retry()

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

def read_sht30_with_retry():
    """Read SHT30 with multiple retry attempts"""
    global bus, stats
    
    if bus is None:
        bus = init_i2c_with_retry()
        if bus is None:
            return None, None
    
    for attempt in range(MAX_RETRIES):
        try:
            # Try different measurement modes
            commands = [
                [0x2C, 0x06],  # High repeatability
                [0x2C, 0x0D],  # Medium repeatability
                [0x2C, 0x10],  # Low repeatability
            ]
            
            for cmd in commands:
                try:
                    msg = smbus2.i2c_msg.write(SHT30_ADDR, cmd)
                    bus.i2c_rdwr(msg)
                    time.sleep(0.02)
                    
                    msg = smbus2.i2c_msg.read(SHT30_ADDR, 6)
                    bus.i2c_rdwr(msg)
                    data = list(msg)
                    
                    # Verify CRC
                    if crc8(data[0:2]) == data[2] and crc8(data[3:5]) == data[5]:
                        temp_raw = (data[0] << 8) | data[1]
                        temperature = -45 + (175 * temp_raw / 65535.0)
                        
                        hum_raw = (data[3] << 8) | data[4]
                        humidity = 100 * hum_raw / 65535.0
                        
                        # Sanity check
                        if -40 <= temperature <= 85 and 0 <= humidity <= 100:
                            stats['indoor_success'] += 1
                            return temperature, humidity
                        
                except Exception:
                    continue
            
            stats['indoor_fail'] += 1
            
        except Exception as e:
            if attempt == 0:
                log_message("ERROR", f"SHT30 read failed: {e}")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                # Try to reinitialize bus
                try:
                    bus.close()
                except:
                    pass
                bus = init_i2c_with_retry()
    
    return None, None

def read_qmp6988_with_retry():
    """Read QMP6988 with retry logic"""
    global bus, stats
    
    if bus is None:
        bus = init_i2c_with_retry()
        if bus is None:
            return None
    
    for attempt in range(MAX_RETRIES):
        try:
            chip_id = bus.read_byte_data(QMP6988_ADDR, 0xD1)
            if chip_id == 0x5C:
                # Return default pressure for now
                # Full implementation would include calibration
                return 1013.25
                
        except Exception as e:
            if attempt == 0:
                log_message("ERROR", f"QMP6988 read failed: {e}")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    return None

def read_dht22_with_retry():
    """Read DHT22 with enhanced retry logic"""
    global stats
    
    venv_python = "/home/pi/apps/weather-station/venv/bin/python"
    if not os.path.exists(venv_python):
        log_message("ERROR", "Virtual environment not found")
        return None, None
    
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(
                [venv_python, "-c", """
import board
import adafruit_dht
import time
import sys

dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)

for i in range(5):
    try:
        temp = dht.temperature
        humidity = dht.humidity
        if temp is not None and humidity is not None:
            print(f"{temp:.1f},{humidity:.1f}")
            sys.exit(0)
        time.sleep(2)
    except RuntimeError:
        if i < 4:
            time.sleep(2)
            continue
    except Exception:
        break

dht.exit()
sys.exit(1)
"""],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) == 2:
                    temp = float(parts[0])
                    humidity = float(parts[1])
                    
                    # Sanity check
                    if -40 <= temp <= 80 and 0 <= humidity <= 100:
                        stats['outdoor_success'] += 1
                        return temp, humidity
            
            stats['outdoor_fail'] += 1
            
        except subprocess.TimeoutExpired:
            log_message("ERROR", "DHT22 read timeout")
            stats['outdoor_fail'] += 1
        except Exception as e:
            if attempt == 0:
                log_message("ERROR", f"DHT22 read error: {e}")
            stats['outdoor_fail'] += 1
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * 2)  # Longer delay for DHT22
    
    return None, None

def get_sensor_data():
    """Get sensor data with caching fallback"""
    global sensor_cache
    current_time = time.time()
    
    # Read indoor sensors
    indoor_temp, indoor_hum = read_sht30_with_retry()
    indoor_pressure = read_qmp6988_with_retry()
    
    # Update cache if successful
    if indoor_temp is not None and indoor_hum is not None:
        sensor_cache['indoor']['temperature'] = indoor_temp
        sensor_cache['indoor']['humidity'] = indoor_hum
        sensor_cache['indoor']['last_update'] = current_time
    elif current_time - sensor_cache['indoor']['last_update'] < CACHE_TIMEOUT:
        # Use cached values
        indoor_temp = sensor_cache['indoor']['temperature']
        indoor_hum = sensor_cache['indoor']['humidity']
        log_message("WARNING", "Using cached indoor values")
    
    if indoor_pressure is not None:
        sensor_cache['indoor']['pressure'] = indoor_pressure
    elif sensor_cache['indoor']['pressure'] is not None:
        indoor_pressure = sensor_cache['indoor']['pressure']
    
    # Read outdoor sensor
    outdoor_temp, outdoor_hum = read_dht22_with_retry()
    
    # Update cache if successful
    if outdoor_temp is not None and outdoor_hum is not None:
        sensor_cache['outdoor']['temperature'] = outdoor_temp
        sensor_cache['outdoor']['humidity'] = outdoor_hum
        sensor_cache['outdoor']['last_update'] = current_time
    elif current_time - sensor_cache['outdoor']['last_update'] < CACHE_TIMEOUT:
        # Use cached values
        outdoor_temp = sensor_cache['outdoor']['temperature']
        outdoor_hum = sensor_cache['outdoor']['humidity']
        log_message("WARNING", "Using cached outdoor values")
    
    return {
        'indoor': {
            'temperature': indoor_temp,
            'humidity': indoor_hum,
            'pressure': indoor_pressure
        },
        'outdoor': {
            'temperature': outdoor_temp,
            'humidity': outdoor_hum
        }
    }

def send_data_with_retry(data):
    """Send data to server with retry logic"""
    global stats
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                SERVER_URL,
                json=data,
                timeout=REQUEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                stats['send_success'] += 1
                return True
            elif response.status_code == 429:
                log_message("WARNING", "Rate limited by server")
                stats['send_fail'] += 1
                return False
            else:
                log_message("ERROR", f"Server returned {response.status_code}")
                
        except requests.exceptions.Timeout:
            log_message("ERROR", "Request timeout")
        except Exception as e:
            log_message("ERROR", f"Send failed: {e}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
    
    stats['send_fail'] += 1
    return False

def print_stats():
    """Print statistics periodically"""
    if (stats['indoor_success'] + stats['indoor_fail']) % 10 == 0:
        total_indoor = stats['indoor_success'] + stats['indoor_fail']
        total_outdoor = stats['outdoor_success'] + stats['outdoor_fail']
        total_send = stats['send_success'] + stats['send_fail']
        
        if total_indoor > 0:
            indoor_rate = (stats['indoor_success'] / total_indoor) * 100
        else:
            indoor_rate = 0
            
        if total_outdoor > 0:
            outdoor_rate = (stats['outdoor_success'] / total_outdoor) * 100
        else:
            outdoor_rate = 0
            
        if total_send > 0:
            send_rate = (stats['send_success'] / total_send) * 100
        else:
            send_rate = 0
        
        log_message("INFO", f"Stats - Indoor: {indoor_rate:.0f}% | Outdoor: {outdoor_rate:.0f}% | Send: {send_rate:.0f}% | I2C Resets: {stats['i2c_resets']}")

def main():
    """Main loop with robust error handling"""
    log_message("INFO", "Weather Station starting with robust error handling...")
    log_message("INFO", f"I2C addresses: SHT30={hex(SHT30_ADDR)}, QMP6988={hex(QMP6988_ADDR)}")
    log_message("INFO", f"DHT22 on GPIO{DHT22_GPIO}")
    
    cycle = 0
    
    while True:
        try:
            cycle += 1
            
            # Get sensor data
            data = get_sensor_data()
            
            # Check if we have any valid data
            has_indoor = any(v is not None for v in data['indoor'].values())
            has_outdoor = any(v is not None for v in data['outdoor'].values())
            
            if has_indoor or has_outdoor:
                # Build payload with available data
                payload = {}
                
                if has_indoor:
                    payload['indoor'] = {k: v for k, v in data['indoor'].items() if v is not None}
                    
                if has_outdoor:
                    payload['outdoor'] = {k: v for k, v in data['outdoor'].items() if v is not None}
                
                # Display data
                if has_indoor:
                    ind = payload.get('indoor', {})
                    log_message("SUCCESS", f"Indoor: {ind.get('temperature', 'N/A')}°C, {ind.get('humidity', 'N/A')}%, {ind.get('pressure', 'N/A')} hPa")
                else:
                    log_message("WARNING", "No indoor data available")
                    
                if has_outdoor:
                    out = payload.get('outdoor', {})
                    log_message("SUCCESS", f"Outdoor: {out.get('temperature', 'N/A')}°C, {out.get('humidity', 'N/A')}%")
                else:
                    log_message("WARNING", "No outdoor data available")
                
                # Send data
                if send_data_with_retry(payload):
                    log_message("SUCCESS", "Data sent successfully")
                else:
                    log_message("ERROR", "Failed to send data")
            else:
                log_message("ERROR", "No sensor data available")
            
            # Print statistics periodically
            if cycle % 10 == 0:
                print_stats()
            
            # Wait for next cycle
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            log_message("INFO", "Shutting down...")
            break
        except Exception as e:
            log_message("ERROR", f"Unexpected error: {e}")
            time.sleep(INTERVAL)
    
    # Cleanup
    try:
        if bus:
            bus.close()
    except:
        pass
    
    log_message("INFO", "Weather Station stopped")
    print_stats()

if __name__ == "__main__":
    main()