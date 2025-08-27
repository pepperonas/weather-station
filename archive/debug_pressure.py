import time
import board
import busio

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

def debug_qmp6988(address=0x70):
    """Debug QMP6988 pressure sensor step by step"""
    try:
        print(f"1. Testing QMP6988 at address 0x{address:02x}")
        
        # Check chip ID
        result = bytearray(1)
        i2c.writeto_then_readfrom(address, bytes([0xD1]), result)
        chip_id = result[0]
        print(f"2. Chip ID: 0x{chip_id:02x} (expected 0x5C)")
        
        if chip_id != 0x5C:
            print(f"ERROR: Wrong chip ID!")
            return None
            
        print("3. Initializing sensor...")
        # Initialize QMP6988
        i2c.writeto(address, bytes([0xF4, 0x27]))  # CTRL_MEAS
        time.sleep(0.1)
        i2c.writeto(address, bytes([0xF5, 0x00]))  # CONFIG
        time.sleep(0.1)
        
        print("4. Waiting for measurement...")
        time.sleep(0.5)
            
        print("5. Reading pressure data...")
        # Read pressure data
        data = bytearray(6)
        i2c.writeto_then_readfrom(address, bytes([0xF7]), data)
        print(f"6. Raw data: {[hex(b) for b in data]}")
        
        # Calculate pressure
        pressure_raw = (data[0] << 16) | (data[1] << 8) | data[2]
        print(f"7. Raw pressure value: {pressure_raw}")
        
        pressure = pressure_raw / 100.0
        print(f"8. Calculated pressure: {pressure:.1f} hPa")
        
        # Check range
        if 800 <= pressure <= 1200:
            print(f"9. SUCCESS: Pressure in valid range")
            return pressure
        else:
            print(f"9. ERROR: Pressure {pressure:.1f} outside valid range (800-1200 hPa)")
            return None
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    result = debug_qmp6988()
    print(f"\nFinal result: {result}")