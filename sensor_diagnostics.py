#!/usr/bin/env python3
"""
Comprehensive sensor diagnostic tool for Raspberry Pi Weather Station
Tests I2C sensors (ENV III) and DHT22 GPIO sensor
"""

import time
import sys
import os
import subprocess
import smbus2

print("=" * 60)
print("WEATHER STATION SENSOR DIAGNOSTICS")
print("=" * 60)

# Check if running as root for GPIO access
if os.geteuid() != 0:
    print("⚠️  Not running as root. Some GPIO tests may fail.")
    print("   Consider running: sudo python3 sensor_diagnostics.py")
    print()

# 1. Check I2C Configuration
print("\n1. I2C CONFIGURATION CHECK")
print("-" * 40)

# Check if I2C is enabled
try:
    result = subprocess.run(['ls', '/dev/i2c-*'], capture_output=True, text=True, shell=True)
    if '/dev/i2c-1' in result.stdout:
        print("✓ I2C-1 device found")
    else:
        print("✗ I2C-1 device not found")
except Exception as e:
    print(f"✗ Error checking I2C devices: {e}")

# Check I2C permissions
try:
    with open('/dev/i2c-1', 'r'):
        print("✓ I2C-1 accessible")
except PermissionError:
    print("✗ Permission denied for I2C-1. Add user to i2c group:")
    print("   sudo usermod -a -G i2c $USER")
except Exception as e:
    print(f"✗ Error accessing I2C-1: {e}")

# 2. Scan I2C Bus
print("\n2. I2C BUS SCAN")
print("-" * 40)

def scan_i2c_bus():
    """Scan I2C bus for devices"""
    devices = []
    try:
        bus = smbus2.SMBus(1)
        print("Scanning I2C bus 1...")
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                devices.append(hex(addr))
                print(f"  Found device at: {hex(addr)}")
            except:
                pass
        bus.close()
        
        if not devices:
            print("✗ No I2C devices found!")
            print("\nPossible issues:")
            print("  1. Wiring problem - check connections:")
            print("     - SDA (ENV III) → GPIO2 (Pin 3)")
            print("     - SCL (ENV III) → GPIO3 (Pin 5)")
            print("     - VCC → 3.3V (Pin 1)")
            print("     - GND → Ground (Pin 9)")
            print("  2. Sensor not powered")
            print("  3. I2C baudrate too high")
        else:
            print(f"\n✓ Found {len(devices)} device(s): {', '.join(devices)}")
            
            # Check for expected addresses
            if '0x44' in devices:
                print("✓ SHT30 sensor detected at 0x44")
            else:
                print("✗ SHT30 sensor NOT found (expected at 0x44)")
                
            if '0x70' in devices:
                print("✓ QMP6988 sensor detected at 0x70")
            else:
                print("✗ QMP6988 sensor NOT found (expected at 0x70)")
                
    except Exception as e:
        print(f"✗ Error scanning I2C bus: {e}")
    
    return devices

devices = scan_i2c_bus()

# 3. Test ENV III Sensors
print("\n3. ENV III SENSOR TESTS")
print("-" * 40)

def test_sht30():
    """Test SHT30 temperature/humidity sensor"""
    SHT30_ADDR = 0x44
    try:
        bus = smbus2.SMBus(1)
        print("Testing SHT30 sensor...")
        
        # Try different measurement commands
        commands = [
            ([0x2C, 0x06], "High repeatability"),
            ([0x2C, 0x0D], "Medium repeatability"),
            ([0x2C, 0x10], "Low repeatability"),
            ([0x24, 0x00], "No clock stretching")
        ]
        
        for cmd, desc in commands:
            try:
                msg = smbus2.i2c_msg.write(SHT30_ADDR, cmd)
                bus.i2c_rdwr(msg)
                time.sleep(0.02)
                
                msg = smbus2.i2c_msg.read(SHT30_ADDR, 6)
                bus.i2c_rdwr(msg)
                data = list(msg)
                
                # Calculate temperature
                temp_raw = (data[0] << 8) | data[1]
                temperature = -45 + (175 * temp_raw / 65535.0)
                
                # Calculate humidity
                hum_raw = (data[3] << 8) | data[4]
                humidity = 100 * hum_raw / 65535.0
                
                print(f"  ✓ {desc}: Temp={temperature:.1f}°C, Humidity={humidity:.1f}%")
                bus.close()
                return True
                
            except Exception as e:
                print(f"  ✗ {desc} failed: {e}")
                continue
        
        bus.close()
        return False
        
    except Exception as e:
        print(f"  ✗ SHT30 test failed: {e}")
        return False

def test_qmp6988():
    """Test QMP6988 pressure sensor"""
    QMP6988_ADDR = 0x70
    try:
        bus = smbus2.SMBus(1)
        print("\nTesting QMP6988 sensor...")
        
        # Read chip ID
        chip_id = bus.read_byte_data(QMP6988_ADDR, 0xD1)
        print(f"  Chip ID: {hex(chip_id)} (expected 0x5C)")
        
        if chip_id == 0x5C:
            print("  ✓ QMP6988 chip ID verified")
        else:
            print("  ✗ Unexpected chip ID")
            
        bus.close()
        return chip_id == 0x5C
        
    except Exception as e:
        print(f"  ✗ QMP6988 test failed: {e}")
        return False

if '0x44' in devices:
    test_sht30()
else:
    print("⚠️  Skipping SHT30 test - device not detected")

if '0x70' in devices:
    test_qmp6988()
else:
    print("⚠️  Skipping QMP6988 test - device not detected")

# 4. Test DHT22 Sensor
print("\n4. DHT22 SENSOR TEST")
print("-" * 40)

def test_dht22():
    """Test DHT22 sensor on GPIO4"""
    print("Testing DHT22 on GPIO4...")
    
    # Check if virtual environment exists
    venv_python = "/home/pi/apps/weather-station/venv/bin/python"
    if not os.path.exists(venv_python):
        print("✗ Virtual environment not found")
        return False
    
    # Test DHT22 using subprocess
    test_code = """
import board
import adafruit_dht
import time

try:
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    time.sleep(2)
    
    # Try multiple reads
    for i in range(3):
        try:
            temp = dht.temperature
            humidity = dht.humidity
            if temp is not None and humidity is not None:
                print(f"SUCCESS:{temp:.1f}:{humidity:.1f}")
                break
        except RuntimeError as e:
            if i < 2:
                time.sleep(2)
                continue
            else:
                print(f"ERROR:{str(e)}")
        except Exception as e:
            print(f"ERROR:{str(e)}")
            break
    
    dht.exit()
except Exception as e:
    print(f"ERROR:{str(e)}")
"""
    
    try:
        result = subprocess.run(
            [venv_python, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = result.stdout.strip()
        if output.startswith("SUCCESS"):
            parts = output.split(":")
            temp = float(parts[1])
            humidity = float(parts[2])
            print(f"  ✓ DHT22 working: Temp={temp}°C, Humidity={humidity}%")
            return True
        elif output.startswith("ERROR"):
            error_msg = output.split(":", 1)[1]
            print(f"  ✗ DHT22 error: {error_msg}")
        else:
            print(f"  ✗ Unexpected output: {output}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("  ✗ DHT22 test timeout")
    except Exception as e:
        print(f"  ✗ DHT22 test failed: {e}")
    
    return False

test_dht22()

# 5. GPIO Pin Status
print("\n5. GPIO PIN STATUS")
print("-" * 40)

def check_gpio_pins():
    """Check status of relevant GPIO pins"""
    pins = {
        2: "I2C SDA",
        3: "I2C SCL", 
        4: "DHT22 Data"
    }
    
    try:
        for pin, desc in pins.items():
            gpio_path = f"/sys/class/gpio/gpio{pin}"
            if os.path.exists(gpio_path):
                with open(f"{gpio_path}/direction", 'r') as f:
                    direction = f.read().strip()
                with open(f"{gpio_path}/value", 'r') as f:
                    value = f.read().strip()
                print(f"  GPIO{pin} ({desc}): direction={direction}, value={value}")
            else:
                print(f"  GPIO{pin} ({desc}): not exported")
    except Exception as e:
        print(f"  Note: GPIO status check requires root or gpio group membership")

check_gpio_pins()

# 6. System Configuration
print("\n6. SYSTEM CONFIGURATION")
print("-" * 40)

# Check boot config
print("Checking /boot/firmware/config.txt...")
try:
    with open('/boot/firmware/config.txt', 'r') as f:
        config = f.read()
        
    if 'dtparam=i2c_arm=on' in config:
        print("  ✓ I2C enabled")
        
        # Check baudrate
        if 'i2c_arm_baudrate=10000' in config:
            print("  ✓ I2C baudrate set to 10kHz (correct for ENV III)")
        elif 'i2c_arm_baudrate=100000' in config:
            print("  ✗ I2C baudrate set to 100kHz (too fast for ENV III)")
            print("    Run: ./fix_i2c_baudrate.sh")
        else:
            print("  ⚠️  I2C baudrate not explicitly set")
    else:
        print("  ✗ I2C not enabled in config")
        
    if 'dtoverlay=dht22,gpiopin=4' in config:
        print("  ✓ DHT22 overlay configured for GPIO4")
    else:
        print("  ✗ DHT22 overlay not configured")
        
except Exception as e:
    print(f"  ✗ Error reading config: {e}")

# Check user groups
print("\nChecking user groups...")
result = subprocess.run(['groups'], capture_output=True, text=True)
groups = result.stdout.strip()
print(f"  Current user groups: {groups}")

if 'i2c' not in groups:
    print("  ✗ User not in i2c group")
if 'gpio' not in groups:
    print("  ✗ User not in gpio group")

# 7. Summary and Recommendations
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

if not devices:
    print("\n⚠️  CRITICAL: No I2C devices detected!")
    print("\nRecommended actions:")
    print("1. Check physical connections:")
    print("   - Ensure ENV III module is properly connected")
    print("   - Verify 3.3V power supply")
    print("   - Check SDA/SCL connections (GPIO2/GPIO3)")
    print("\n2. Fix I2C baudrate:")
    print("   ./fix_i2c_baudrate.sh")
    print("   sudo reboot")
    print("\n3. Test connections with multimeter:")
    print("   - 3.3V between VCC and GND")
    print("   - Continuity on SDA/SCL lines")
    print("\n4. Try different I2C bus speed:")
    print("   - Edit /boot/firmware/config.txt")
    print("   - Try baudrates: 10000, 50000, 100000")
else:
    print("\n✓ I2C communication established")
    if '0x44' not in devices or '0x70' not in devices:
        print("⚠️  Some ENV III sensors not detected")
    else:
        print("✓ All ENV III sensors detected")

print("\nFor immediate testing after fixes:")
print("  python3 sensor_diagnostics.py")
print("\nTo restart the weather station:")
print("  pm2 restart weather-station")