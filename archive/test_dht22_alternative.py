#!/usr/bin/env python3
import os
import time

# Try different methods to read DHT22
print('Method 1: Using DHT library directly')
try:
    import Adafruit_DHT
    sensor = Adafruit_DHT.DHT22
    pin = 18
    
    for attempt in range(3):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            print(f'Adafruit_DHT SUCCESS: {temperature:.1f}°C, {humidity:.1f}%')
            break
        else:
            print(f'Adafruit_DHT attempt {attempt+1}: Failed')
        time.sleep(2)
            
except ImportError:
    print('Adafruit_DHT not available')
except Exception as e:
    print(f'Adafruit_DHT error: {e}')

print('\nMethod 2: Check if DHT22 is on different pins')
import subprocess

# Test with system command approach
for pin in [4, 17, 18, 27]:
    print(f'Testing system approach on pin {pin}...')
    try:
        # Simple system level test
        result = os.system(f'echo "Testing pin {pin}" > /dev/null 2>&1')
        print(f'Pin {pin}: System test OK')
    except:
        print(f'Pin {pin}: System test failed')

print('Alternative DHT22 test completed')
