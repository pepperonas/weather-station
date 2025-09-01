#!/usr/bin/env python3

import subprocess
import time
import json

def read_dht22_via_dtoverlay():
    """Try to read DHT22 using device tree overlay method"""
    try:
        # The DHT22 device tree overlay should create files in /sys/bus/iio/devices/
        # or make the sensor accessible via standard GPIO tools
        
        # Method 1: Try to use gpio readall to check if GPIO4 is configured correctly
        result = subprocess.run(['gpio', 'readall'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print('GPIO Status:')
            lines = result.stdout.split('\n')
            for line in lines:
                if ' 4 |' in line:  # GPIO4 line
                    print(f'GPIO4: {line}')
        
        # Method 2: Try direct sysfs GPIO access
        # Export GPIO4 if not already exported
        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write('4')
        except:
            pass  # Already exported or permission issue
        
        # Check if GPIO4 directory exists
        import os
        if os.path.exists('/sys/class/gpio/gpio4'):
            print('GPIO4 is accessible via sysfs')
            
            # Set as input
            with open('/sys/class/gpio/gpio4/direction', 'w') as f:
                f.write('in')
            
            # Read value multiple times
            values = []
            for i in range(10):
                with open('/sys/class/gpio/gpio4/value', 'r') as f:
                    val = f.read().strip()
                    values.append(val)
                time.sleep(0.1)
            
            print(f'GPIO4 readings: {values}')
            
            # Check for any pattern changes (DHT22 communication)
            if len(set(values)) > 1:
                print('✅ GPIO4 shows signal changes - DHT22 might be responding')
                return True
            else:
                print('❌ GPIO4 shows static signal - no DHT22 communication detected')
        
        return False
        
    except Exception as e:
        print(f'Error in device tree method: {e}')
        return False

def read_dht22_via_subprocess():
    """Use subprocess to call a DHT22 reading command"""
    try:
        # Try different DHT22 reading approaches
        commands = [
            ['python3', '-c', 'import Adafruit_DHT; sensor = Adafruit_DHT.DHT22; pin = 4; humidity, temperature = Adafruit_DHT.read_retry(sensor, pin); print(f"temp={temperature},humidity={humidity}")'],
            ['dht22', '4'],  # If dht22 command exists
        ]
        
        for cmd in commands:
            try:
                print(f'Trying command: {" ".join(cmd[:3])}...')
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f'✅ Success: {result.stdout.strip()}')
                    return True
                else:
                    print(f'❌ Failed: {result.stderr.strip() if result.stderr else "No output"}')
                    
            except subprocess.TimeoutExpired:
                print('❌ Command timed out')
            except FileNotFoundError:
                print('❌ Command not found')
                
        return False
        
    except Exception as e:
        print(f'Error in subprocess method: {e}')
        return False

if __name__ == '__main__':
    print('=== DHT22 Working Test ===')
    
    print('\n1. Testing Device Tree Overlay Method...')
    dt_success = read_dht22_via_dtoverlay()
    
    print('\n2. Testing Subprocess Method...')
    subprocess_success = read_dht22_via_subprocess()
    
    if dt_success or subprocess_success:
        print('\n🎉 DHT22 communication detected!')
    else:
        print('\n❌ No DHT22 communication detected')
        
        # Final diagnostic
        print('\n=== Diagnostic Info ===')
        try:
            result = subprocess.run(['cat', '/boot/firmware/config.txt'], capture_output=True, text=True)
            if 'dht22' in result.stdout:
                print('✓ DHT22 device tree overlay is configured')
            else:
                print('❌ No DHT22 device tree overlay found in config.txt')
        except:
            print('Could not read boot config')
