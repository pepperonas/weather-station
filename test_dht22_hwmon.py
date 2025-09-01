#!/usr/bin/env python3

import time
import glob
import os

def read_dht22_hwmon():
    """Try to read DHT22 via hwmon interface"""
    try:
        # Look for hwmon devices
        hwmon_paths = glob.glob('/sys/class/hwmon/hwmon*/name')
        
        for path in hwmon_paths:
            with open(path, 'r') as f:
                name = f.read().strip()
                print(f'Found hwmon device: {name} at {os.path.dirname(path)}')
                
                if 'dht22' in name.lower():
                    hwmon_dir = os.path.dirname(path)
                    
                    # Try to read temperature
                    temp_file = os.path.join(hwmon_dir, 'temp1_input')
                    humidity_file = os.path.join(hwmon_dir, 'humidity1_input')
                    
                    if os.path.exists(temp_file):
                        with open(temp_file, 'r') as f:
                            temp_raw = f.read().strip()
                            temp_celsius = float(temp_raw) / 1000.0
                            print(f'Temperature: {temp_celsius:.1f}°C')
                    
                    if os.path.exists(humidity_file):
                        with open(humidity_file, 'r') as f:
                            humidity_raw = f.read().strip()
                            humidity_percent = float(humidity_raw) / 1000.0
                            print(f'Humidity: {humidity_percent:.1f}%')
                    
                    return True
        
        print('No DHT22 hwmon device found')
        return False
        
    except Exception as e:
        print(f'Error reading hwmon: {e}')
        return False

def test_legacy_gpio_method():
    """Test with Adafruit library as fallback"""
    try:
        import board
        import adafruit_dht
        
        print('Testing DHT22 with Adafruit library on GPIO4...')
        dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        
        for attempt in range(3):
            try:
                temperature = dht.temperature
                humidity = dht.humidity
                
                if temperature is not None and humidity is not None:
                    print(f'✅ DHT22 reading successful!')
                    print(f'Temperature: {temperature:.1f}°C')
                    print(f'Humidity: {humidity:.1f}%')
                    return True
                    
            except RuntimeError as e:
                print(f'Attempt {attempt + 1}: {e}')
                time.sleep(2)
        
        print('❌ All attempts failed')
        return False
        
    except ImportError:
        print('Adafruit DHT library not available')
        return False
    except Exception as e:
        print(f'Error with Adafruit library: {e}')
        return False

if __name__ == '__main__':
    print('=== DHT22 Hardware Monitor Test ===')
    
    # First try hwmon interface
    success = read_dht22_hwmon()
    
    if not success:
        print('\n=== Fallback to GPIO Method ===')
        success = test_legacy_gpio_method()
    
    if success:
        print('\n🎉 DHT22 is working!')
    else:
        print('\n❌ DHT22 not responding through any method')
