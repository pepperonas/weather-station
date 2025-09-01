#!/usr/bin/env python3
"""Debug script to identify sensor issues"""
import time
import smbus2
import subprocess

# Test ENV III (I2C)
print("=== Testing ENV III (I2C) ===")
try:
    bus = smbus2.SMBus(1)
    
    # Read SHT30
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.02)
    data = bus.read_i2c_block_data(0x44, 0x00, 6)
    temp_raw = (data[0] << 8) | data[1]
    hum_raw = (data[3] << 8) | data[4]
    temp = -45 + (175 * temp_raw / 65535.0)
    hum = 100 * hum_raw / 65535.0
    print(f"ENV III (0x44): {temp:.1f}°C, {hum:.1f}% RH")
    print(f"  Raw values: temp_raw={temp_raw}, hum_raw={hum_raw}")
    
    # Check if this could be outdoor (higher temp)
    if temp > 25:
        print("  -> This seems like OUTDOOR sensor (too warm for indoor)")
    else:
        print("  -> This seems like INDOOR sensor")
        
    bus.close()
except Exception as e:
    print(f"ENV III Error: {e}")

print("\n=== Testing DHT22 (GPIO4) ===")
# Test with different methods
methods = [
    ("Direct adafruit_dht", """
import board, adafruit_dht
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
try:
    temp = dht.temperature
    hum = dht.humidity
    if temp and hum:
        print(f'DHT22: {temp:.1f}°C, {hum:.1f}% RH')
        if temp < 25:
            print('  -> This seems like INDOOR sensor')
        else:
            print('  -> This seems like OUTDOOR sensor')
    else:
        print('DHT22: No reading')
except Exception as e:
    print(f'DHT22 Error: {e}')
finally:
    dht.exit()
"""),
    ("Alternative GPIO test", """
# Test if GPIO4 is accessible
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
state = GPIO.input(4)
print(f'GPIO4 state: {state} (0=LOW, 1=HIGH)')
GPIO.cleanup()
""")
]

for method_name, code in methods:
    print(f"\nTrying {method_name}:")
    try:
        result = subprocess.run(
            ['/home/pi/apps/weather-station/venv/bin/python', '-c', code],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(f"Stderr: {result.stderr.strip()}")
    except Exception as e:
        print(f"Failed: {e}")

print("\n=== Physical Check Recommendation ===")
print("1. ENV III Module should be connected to I2C pins:")
print("   - VCC to 3.3V (Pin 1)")
print("   - GND to Ground (Pin 9)")
print("   - SDA to GPIO2 (Pin 3)")
print("   - SCL to GPIO3 (Pin 5)")
print("")
print("2. DHT22 should be connected to:")
print("   - VCC to 3.3V (Pin 1)")
print("   - DATA to GPIO4 (Pin 7)")
print("   - GND to Ground (Pin 9)")
print("")
print("3. Check if sensors are physically swapped:")
print("   - Indoor sensor should show ~20°C")
print("   - Outdoor sensor should show current outside temp")