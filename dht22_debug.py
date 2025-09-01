#!/usr/bin/env python3
"""Debug script for DHT22 sensor issue"""
import sys
import time
import subprocess

print("DHT22 Debug Script")
print("=" * 50)

# Test 1: Try with subprocess method (same as main script)
print("\n1. Testing with subprocess method:")
try:
    result = subprocess.run(
        ['/home/pi/apps/weather-station/venv/bin/python', '-c', '''
import board
import adafruit_dht
import time
DHT22_GPIO = 4
try:
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    time.sleep(2)
    temp = dht.temperature
    hum = dht.humidity
    if temp is not None and hum is not None:
        print(f"{temp},{hum}")
    else:
        print("ERROR: None values")
    dht.exit()
except Exception as e:
    print(f"ERROR: {e}")
'''],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"  Stdout: {result.stdout.strip()}")
    print(f"  Stderr: {result.stderr.strip() if result.stderr else 'None'}")
    print(f"  Return code: {result.returncode}")
except Exception as e:
    print(f"  Subprocess failed: {e}")

# Test 2: Direct import test
print("\n2. Testing direct import:")
try:
    import board
    import adafruit_dht
    
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    attempts = 3
    for i in range(attempts):
        try:
            time.sleep(2)
            temp = dht.temperature
            hum = dht.humidity
            if temp is not None and hum is not None:
                print(f"  Attempt {i+1}: Success - Temp: {temp:.1f}°C, Humidity: {hum:.1f}%")
                break
            else:
                print(f"  Attempt {i+1}: Got None values")
        except RuntimeError as e:
            print(f"  Attempt {i+1}: Runtime error - {e}")
        except Exception as e:
            print(f"  Attempt {i+1}: Error - {e}")
    dht.exit()
except ImportError as e:
    print(f"  Import error: {e}")
except Exception as e:
    print(f"  Failed: {e}")

# Test 3: Check GPIO permissions
print("\n3. Checking permissions and groups:")
import os
print(f"  Current user: {os.getenv('USER', 'unknown')}")
print(f"  UID: {os.getuid()}, GID: {os.getgid()}")

try:
    groups_result = subprocess.run(['groups'], capture_output=True, text=True)
    print(f"  Groups: {groups_result.stdout.strip()}")
except:
    pass

# Test 4: Check GPIO export
print("\n4. Checking GPIO4 state:")
try:
    # Check if GPIO4 is exported
    gpio_path = "/sys/class/gpio/gpio4"
    if os.path.exists(gpio_path):
        print(f"  GPIO4 is exported")
        with open(f"{gpio_path}/direction", "r") as f:
            print(f"  Direction: {f.read().strip()}")
    else:
        print("  GPIO4 not exported in sysfs")
except Exception as e:
    print(f"  Error checking GPIO: {e}")

print("\n" + "=" * 50)
print("Debug complete")