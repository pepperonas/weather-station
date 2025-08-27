#!/usr/bin/env python3
import time
import sys

print("Testing ENV III on Raspberry Pi 5")
print("=====================================\n")

# Test different methods
methods = []

# Method 1: Try with smbus on bus 1
try:
    import smbus
    bus1 = smbus.SMBus(1)
    print("✓ SMBus on bus 1 available")
    methods.append(("bus1_smbus", bus1))
except Exception as e:
    print(f"✗ SMBus bus 1: {e}")

# Method 2: Try with smbus on bus 13  
try:
    import smbus
    bus13 = smbus.SMBus(13)
    print("✓ SMBus on bus 13 available")
    methods.append(("bus13_smbus", bus13))
except Exception as e:
    print(f"✗ SMBus bus 13: {e}")

# Method 3: Try with smbus2
try:
    import smbus2
    bus1_2 = smbus2.SMBus(1)
    print("✓ SMBus2 on bus 1 available")
    methods.append(("bus1_smbus2", bus1_2))
except Exception as e:
    print(f"✗ SMBus2 bus 1: {e}")

try:
    import smbus2
    bus13_2 = smbus2.SMBus(13)
    print("✓ SMBus2 on bus 13 available")
    methods.append(("bus13_smbus2", bus13_2))
except Exception as e:
    print(f"✗ SMBus2 bus 13: {e}")

print("\nTesting SHT30 (0x44) with different methods:\n")

for method_name, bus in methods:
    print(f"Testing with {method_name}:")
    
    # Test 1: Simple read
    try:
        data = bus.read_byte(0x44)
        print(f"  ✓ Read byte: 0x{data:02x}")
    except Exception as e:
        print(f"  ✗ Read byte failed: {e}")
    
    # Test 2: Status read
    try:
        bus.write_byte(0x44, 0xF3)
        time.sleep(0.01)
        data = bus.read_byte(0x44)
        print(f"  ✓ Status: 0x{data:02x}")
    except Exception as e:
        print(f"  ✗ Status failed: {e}")
    
    # Test 3: Measurement
    try:
        # Clear status register
        bus.write_i2c_block_data(0x44, 0x30, [0x41])
        time.sleep(0.01)
        
        # Start measurement
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        time.sleep(0.02)
        
        # Read result
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        temp_raw = (data[0] << 8) | data[1]
        temp = -45 + (175 * temp_raw / 65535.0)
        hum_raw = (data[3] << 8) | data[4]
        hum = 100 * hum_raw / 65535.0
        print(f"  ✓ Measurement: {temp:.1f}°C, {hum:.1f}%")
    except Exception as e:
        print(f"  ✗ Measurement failed: {e}")
    
    print()

# Close all buses
for _, bus in methods:
    try:
        bus.close()
    except:
        pass

print("\nDone!")
