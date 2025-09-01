#!/usr/bin/env python3
import time
import os

def test_gpio_basic():
    """Test basic GPIO functionality"""
    try:
        # Check if GPIO4 can be controlled
        print("Testing GPIO4 basic control...")
        
        # Export GPIO4
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('4')
        
        time.sleep(0.1)
        
        # Set as output and toggle
        with open('/sys/class/gpio/gpio4/direction', 'w') as f:
            f.write('out')
        
        # Set high
        with open('/sys/class/gpio/gpio4/value', 'w') as f:
            f.write('1')
        
        time.sleep(0.1)
        
        # Read value
        with open('/sys/class/gpio/gpio4/value', 'r') as f:
            val_high = f.read().strip()
        
        # Set low
        with open('/sys/class/gpio/gpio4/value', 'w') as f:
            f.write('0')
        
        time.sleep(0.1)
        
        # Read value
        with open('/sys/class/gpio/gpio4/value', 'r') as f:
            val_low = f.read().strip()
        
        print(f"GPIO4 High: {val_high}, Low: {val_low}")
        
        if val_high == '1' and val_low == '0':
            print("✅ GPIO4 basic control working")
            return True
        else:
            print("❌ GPIO4 control problem")
            return False
            
    except Exception as e:
        print(f"❌ GPIO test error: {e}")
        return False
    finally:
        try:
            # Cleanup - unexport GPIO
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write('4')
        except:
            pass

def test_dht22_protocol():
    """Test DHT22 with protocol timing"""
    try:
        import subprocess
        
        # Try different DHT22 approaches
        print("\nTesting DHT22 with different methods...")
        
        # Method 1: Via device tree overlay (if configured)
        try:
            result = subprocess.run(['cat', '/sys/bus/iio/devices/iio:device*/in_temp_input'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                temp_raw = int(result.stdout.strip())
                temp = temp_raw / 1000.0
                print(f"✅ Device tree method: {temp}°C")
                return True
        except:
            pass
        
        # Method 2: Check hwmon DHT22 device
        hwmon_dirs = ['/sys/class/hwmon/hwmon0', '/sys/class/hwmon/hwmon1', 
                      '/sys/class/hwmon/hwmon2', '/sys/class/hwmon/hwmon3']
        
        for hwmon_dir in hwmon_dirs:
            try:
                with open(f'{hwmon_dir}/name', 'r') as f:
                    name = f.read().strip()
                if 'dht' in name.lower():
                    print(f"Found DHT device at {hwmon_dir}: {name}")
                    # Try to read temperature
                    with open(f'{hwmon_dir}/temp1_input', 'r') as f:
                        temp_raw = f.read().strip()
                        temp = float(temp_raw) / 1000.0
                        print(f"✅ hwmon method: {temp}°C")
                        return True
            except:
                continue
        
        print("❌ No working DHT22 method found")
        return False
        
    except Exception as e:
        print(f"❌ DHT22 protocol test error: {e}")
        return False

if __name__ == "__main__":
    print("=== DHT22 Hardware Diagnostic ===\n")
    
    gpio_ok = test_gpio_basic()
    dht_ok = test_dht22_protocol()
    
    print(f"\n=== Hardware Diagnostic Results ===")
    print(f"GPIO4 Control: {'✅ OK' if gpio_ok else '❌ FAILED'}")
    print(f"DHT22 Response: {'✅ OK' if dht_ok else '❌ FAILED'}")
    
    if gpio_ok and not dht_ok:
        print("\n💡 GPIO is working but DHT22 is not responding.")
        print("   Possible causes:")
        print("   - DHT22 sensor hardware failure")
        print("   - Loose wiring connection")
        print("   - Power supply issue (DHT22 needs stable 3.3V)")
        print("   - DHT22 sensor may need replacement")
        
        # Try power cycle suggestion
        print("\n🔧 Try this manual fix:")
        print("   1. Disconnect DHT22 power for 10 seconds")
        print("   2. Reconnect DHT22 power")
        print("   3. Wait 2 seconds for sensor to stabilize")
        print("   4. Run test again")
    elif not gpio_ok:
        print("\n⚠️  GPIO4 control issue detected - may be system-level problem")
    else:
        print("\n🎉 All hardware tests passed!")
