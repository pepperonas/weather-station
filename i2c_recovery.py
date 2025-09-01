#!/usr/bin/env python3
"""
I2C Bus Recovery Tool
Attempts to reset and recover I2C communication
"""

import time
import subprocess
import sys
import os

print("I2C BUS RECOVERY TOOL")
print("=" * 40)

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

# 1. Stop the weather station service
print("\n1. Stopping weather station service...")
success, _, _ = run_command("pm2 stop weather-station")
if success:
    print("   ✓ Service stopped")
else:
    print("   ⚠️  Could not stop service")

# 2. Reset I2C module
print("\n2. Resetting I2C module...")
commands = [
    ("sudo modprobe -r i2c_bcm2835", "Removing I2C module"),
    ("sudo modprobe i2c_bcm2835", "Loading I2C module"),
]

for cmd, desc in commands:
    print(f"   {desc}...")
    success, _, error = run_command(cmd)
    if success:
        print(f"   ✓ {desc} successful")
    else:
        print(f"   ✗ {desc} failed: {error}")
        print("   Note: This script needs sudo privileges")

# 3. Check I2C device
print("\n3. Checking I2C device...")
if os.path.exists("/dev/i2c-1"):
    print("   ✓ /dev/i2c-1 exists")
else:
    print("   ✗ /dev/i2c-1 not found")

# 4. Scan I2C bus with different speeds
print("\n4. Testing different I2C speeds...")

def test_i2c_speed(speed):
    """Test I2C at a specific speed"""
    print(f"\n   Testing {speed} Hz...")
    
    # Create temporary config
    config_line = f"dtparam=i2c_arm=on,i2c_arm_baudrate={speed}"
    
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        
        devices_found = []
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                devices_found.append(hex(addr))
            except:
                pass
        
        bus.close()
        
        if devices_found:
            print(f"   ✓ Found devices at {speed} Hz: {', '.join(devices_found)}")
            return True
        else:
            print(f"   ✗ No devices found at {speed} Hz")
            return False
            
    except Exception as e:
        print(f"   ✗ Error at {speed} Hz: {e}")
        return False

# Test current speed
print("\n   Current configuration:")
test_i2c_speed(10000)

# 5. GPIO Reset for I2C pins
print("\n5. Resetting GPIO pins for I2C...")

gpio_reset_script = """
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Reset I2C pins (GPIO2/3)
pins = [2, 3]
for pin in pins:
    try:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        time.sleep(0.1)
        print(f"   ✓ GPIO{pin} reset to input with pull-up")
    except Exception as e:
        print(f"   ✗ GPIO{pin} reset failed: {e}")

GPIO.cleanup()
"""

try:
    exec(gpio_reset_script)
except Exception as e:
    print(f"   ✗ GPIO reset failed: {e}")
    print("   Note: GPIO access may require root privileges")

# 6. Power cycle recommendation
print("\n6. POWER CYCLE RECOMMENDATION")
print("-" * 40)
print("If sensors are still not detected:")
print("1. Shutdown the Raspberry Pi:")
print("   sudo shutdown -h now")
print("2. Disconnect power for 10 seconds")
print("3. Reconnect ENV III module ensuring:")
print("   - VCC → Pin 1 (3.3V)")
print("   - GND → Pin 9 (Ground)")
print("   - SDA → Pin 3 (GPIO2)")
print("   - SCL → Pin 5 (GPIO3)")
print("4. Power on and run:")
print("   ./fix_i2c_baudrate.sh")
print("   sudo reboot")
print("5. After reboot, test with:")
print("   python3 sensor_diagnostics.py")

# 7. Alternative I2C bus
print("\n7. ALTERNATIVE I2C BUS")
print("-" * 40)
print("If I2C-1 continues to fail, try I2C-0:")
print("1. Edit /boot/firmware/config.txt")
print("2. Add: dtparam=i2c_vc=on")
print("3. Reboot and test with bus 0")

# 8. Manual sensor test
print("\n8. MANUAL SENSOR TEST")
print("-" * 40)

manual_test = """
#!/usr/bin/env python3
import smbus2
import time

# Try to communicate with known addresses
addresses = [0x44, 0x70]  # SHT30, QMP6988
bus = None

try:
    bus = smbus2.SMBus(1)
    print("Testing direct I2C communication...")
    
    for addr in addresses:
        try:
            # Try to read one byte
            data = bus.read_byte(addr)
            print(f"✓ Device at {hex(addr)} responded with: {hex(data)}")
        except Exception as e:
            print(f"✗ Device at {hex(addr)} failed: {e}")
    
except Exception as e:
    print(f"✗ I2C bus error: {e}")
finally:
    if bus:
        bus.close()
"""

print("Running manual sensor test...")
exec(manual_test)

print("\n" + "=" * 40)
print("RECOVERY COMPLETE")
print("=" * 40)
print("\nNext steps:")
print("1. Run sensor diagnostics:")
print("   python3 sensor_diagnostics.py")
print("2. If sensors detected, restart service:")
print("   pm2 restart weather-station")
print("3. Check logs:")
print("   pm2 logs weather-station --lines 20")