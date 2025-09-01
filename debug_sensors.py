#!/usr/bin/env python3
"""
Comprehensive sensor debugging script for Raspberry Pi 3B
Tests I2C and DHT22 sensors with detailed diagnostics
"""

import sys
import os
import time
import subprocess

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_system_info():
    """Check basic system information"""
    print_header("SYSTEM INFORMATION")
    
    # Raspberry Pi Model
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip('\x00')
            print(f"Pi Model: {model}")
    except:
        print("Pi Model: Unable to detect")
    
    # Kernel version
    result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
    print(f"Kernel: {result.stdout.strip()}")
    
    # Check user groups
    result = subprocess.run(['groups'], capture_output=True, text=True)
    print(f"User groups: {result.stdout.strip()}")
    
    # Check Python version
    print(f"Python: {sys.version.split()[0]}")

def check_i2c_config():
    """Check I2C configuration"""
    print_header("I2C CONFIGURATION")
    
    # Check if I2C devices exist
    i2c_devices = []
    for i in range(10):
        if os.path.exists(f"/dev/i2c-{i}"):
            i2c_devices.append(f"i2c-{i}")
    
    if i2c_devices:
        print(f"I2C devices found: {', '.join(i2c_devices)}")
    else:
        print("❌ No I2C devices found in /dev/")
        return False
    
    # Check I2C kernel modules
    result = subprocess.run(['lsmod'], capture_output=True, text=True)
    if 'i2c_bcm2835' in result.stdout:
        print("✅ i2c_bcm2835 module loaded")
    else:
        print("❌ i2c_bcm2835 module NOT loaded")
    
    if 'i2c_dev' in result.stdout:
        print("✅ i2c_dev module loaded")
    else:
        print("❌ i2c_dev module NOT loaded")
    
    # Check boot config
    config_path = '/boot/firmware/config.txt'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = f.read()
            if 'dtparam=i2c_arm=on' in config:
                print("✅ I2C enabled in boot config")
                # Check baudrate
                if 'i2c_arm_baudrate=' in config:
                    for line in config.split('\n'):
                        if 'i2c_arm_baudrate=' in line and not line.strip().startswith('#'):
                            print(f"   Current setting: {line.strip()}")
            else:
                print("❌ I2C NOT enabled in boot config")
    
    return True

def scan_i2c_bus(bus_num=1):
    """Scan I2C bus for devices"""
    print_header(f"I2C BUS {bus_num} SCAN")
    
    try:
        # Try using i2cdetect command first
        result = subprocess.run(['i2cdetect', '-y', str(bus_num)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            
            devices_found = []
            # Parse output to find devices
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) > 1:
                    for part in parts[1:]:
                        if part != '--' and part != 'UU':
                            devices_found.append(f"0x{part}")
            
            if devices_found:
                print(f"\n✅ Devices found: {', '.join(devices_found)}")
                if '0x44' in devices_found:
                    print("   → 0x44: SHT30 Temperature/Humidity sensor detected")
                if '0x70' in devices_found:
                    print("   → 0x70: QMP6988 Pressure sensor detected")
            else:
                print("\n❌ No I2C devices found!")
                print("\nPossible causes:")
                print("1. Sensors not powered (check 3.3V connection)")
                print("2. SDA/SCL connections incorrect")
                print("3. I2C baudrate incompatibility")
                print("4. Damaged sensors or cables")
            
            return devices_found
        else:
            print(f"Error running i2cdetect: {result.stderr}")
            return []
            
    except FileNotFoundError:
        print("i2cdetect command not found. Install with: sudo apt-get install i2c-tools")
        return []
    except Exception as e:
        print(f"❌ Error scanning I2C bus: {e}")
        return []

def test_sht30_with_smbus():
    """Test SHT30 sensor directly using smbus2"""
    print_header("SHT30 SENSOR TEST (smbus2)")
    
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        
        # Send measurement command (single shot, high repeatability)
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        time.sleep(0.02)  # Wait for measurement
        
        # Read 6 bytes
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        
        # Calculate temperature
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + 175 * temp_raw / 65535
        
        # Calculate humidity
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535
        
        bus.close()
        
        print(f"✅ SHT30 Working!")
        print(f"   Temperature: {temperature:.1f}°C")
        print(f"   Humidity: {humidity:.1f}%")
        return True
        
    except ImportError:
        print("❌ smbus2 not installed. Install with: pip install smbus2")
        return False
    except Exception as e:
        print(f"❌ SHT30 test failed: {e}")
        return False

def check_gpio_dht22():
    """Check GPIO4 configuration for DHT22"""
    print_header("DHT22 GPIO CONFIGURATION")
    
    # Check if DHT22 overlay is loaded
    config_path = '/boot/firmware/config.txt'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = f.read()
            if 'dtoverlay=dht22' in config or 'dtoverlay=w1-gpio' in config:
                print("✅ DHT22 overlay configured in boot config")
                for line in config.split('\n'):
                    if 'dht22' in line and not line.strip().startswith('#'):
                        print(f"   Current setting: {line.strip()}")
            else:
                print("❌ DHT22 overlay NOT configured")
                print("   Add to /boot/firmware/config.txt: dtoverlay=dht22,gpiopin=4")
    
    # Check GPIO4 export
    gpio_path = '/sys/class/gpio/gpio4'
    if os.path.exists(gpio_path):
        print("✅ GPIO4 is exported")
    else:
        print("ℹ️ GPIO4 not exported (normal for kernel driver)")
    
    return True

def test_dht22_simple():
    """Test DHT22 using subprocess with venv Python"""
    print_header("DHT22 SENSOR TEST")
    
    venv_python = "/home/pi/apps/weather-station/venv/bin/python"
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found")
        return False
    
    test_code = """
import board
import adafruit_dht
import time

try:
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    time.sleep(2)
    
    for attempt in range(3):
        try:
            temp = dht.temperature
            hum = dht.humidity
            if temp is not None and hum is not None:
                print(f"OK:{temp:.1f}:{hum:.1f}")
                break
        except RuntimeError as e:
            if attempt == 2:
                print(f"ERROR:{e}")
        time.sleep(2)
    
    dht.exit()
except Exception as e:
    print(f"ERROR:{e}")
"""
    
    try:
        result = subprocess.run(
            [venv_python, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = result.stdout.strip() or result.stderr.strip()
        
        if output.startswith("OK:"):
            parts = output.split(":")
            print(f"✅ DHT22 Working!")
            print(f"   Temperature: {parts[1]}°C")
            print(f"   Humidity: {parts[2]}%")
            return True
        else:
            print(f"❌ DHT22 test failed: {output}")
            print("\nPossible causes:")
            print("1. Wrong GPIO pin (should be GPIO4, physical pin 7)")
            print("2. Power issue (needs 3.3V or 5V)")
            print("3. Pull-up resistor missing (10kΩ between data and VCC)")
            print("4. Damaged sensor")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ DHT22 test timeout")
        return False
    except Exception as e:
        print(f"❌ DHT22 test error: {e}")
        return False

def suggest_fixes(i2c_devices, dht_working):
    """Suggest fixes based on test results"""
    print_header("RECOMMENDED ACTIONS")
    
    if not i2c_devices:
        print("\n🔧 I2C FIXES:")
        print("1. Test with standard baudrate:")
        print("   - Edit /boot/firmware/config.txt")
        print("   - Change: dtparam=i2c_arm=on,i2c_arm_baudrate=10000")
        print("   - To:     dtparam=i2c_arm=on,i2c_arm_baudrate=100000")
        print("   - Reboot: sudo reboot")
        print("")
        print("2. Enable I2C pull-ups:")
        print("   - Add to /boot/firmware/config.txt:")
        print("   - gpio=2,3=pu")
        print("")
        print("3. Check connections:")
        print("   - ENV III VCC → Pin 1 (3.3V)")
        print("   - ENV III GND → Pin 9 (Ground)")
        print("   - ENV III SDA → Pin 3 (GPIO2)")
        print("   - ENV III SCL → Pin 5 (GPIO3)")
    
    if not dht_working:
        print("\n🔧 DHT22 FIXES:")
        print("1. Check connections:")
        print("   - DHT22 Pin 1 → Pin 1 (3.3V) or Pin 2 (5V)")
        print("   - DHT22 Pin 2 → Pin 7 (GPIO4)")
        print("   - DHT22 Pin 4 → Pin 9 (Ground)")
        print("")
        print("2. Add pull-up resistor:")
        print("   - 10kΩ resistor between data pin and VCC")
        print("")
        print("3. Try alternative GPIO:")
        print("   - Change to GPIO17 (Pin 11)")
        print("   - Update /boot/firmware/config.txt:")
        print("   - dtoverlay=dht22,gpiopin=17")
        print("   - Update code to use board.D17")

def main():
    print("\n" + "🔍 RASPBERRY PI SENSOR DIAGNOSTIC TOOL 🔍".center(60))
    print("Testing I2C and DHT22 sensors...\n")
    
    # System info
    check_system_info()
    
    # I2C checks
    if check_i2c_config():
        i2c_devices = scan_i2c_bus(1)
        
        # Test SHT30 if found
        if '0x44' in [d.lower() for d in i2c_devices]:
            test_sht30_with_smbus()
    else:
        i2c_devices = []
    
    # GPIO/DHT22 checks
    check_gpio_dht22()
    dht_working = test_dht22_simple()
    
    # Suggestions
    suggest_fixes(i2c_devices, dht_working)
    
    # Summary
    print_header("SUMMARY")
    if i2c_devices and dht_working:
        print("✅ All sensors working correctly!")
    elif i2c_devices:
        print("⚠️ I2C sensors working, DHT22 needs attention")
    elif dht_working:
        print("⚠️ DHT22 working, I2C sensors need attention")
    else:
        print("❌ Both sensor systems need attention")

if __name__ == "__main__":
    main()