import board
import busio
import time

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

def test_qmp6988(address=0x70):
    """Test QMP6988 pressure sensor"""
    try:
        print(f"Testing QMP6988 at address 0x{address:02x}")
        
        # Try to read chip ID
        result = bytearray(1)
        i2c.writeto_then_readfrom(address, bytes([0xD1]), result)
        chip_id = result[0]
        print(f"Chip ID: 0x{chip_id:02x}")
        
        if chip_id != 0x5C:
            print(f"ERROR: Expected chip ID 0x5C, got 0x{chip_id:02x}")
            return False
            
        print("Chip ID correct, initializing sensor...")
        
        # Initialize QMP6988 - set to normal mode
        i2c.writeto(address, bytes([0xF4, 0x27]))  # CTRL_MEAS: normal mode, temp and pressure oversampling
        time.sleep(0.1)
        
        # Set config register
        i2c.writeto(address, bytes([0xF5, 0x00]))  # CONFIG: no filtering, no SPI
        time.sleep(0.1)
        
        print("Sensor initialized, reading pressure...")
        
        # Wait for measurement
        time.sleep(0.5)
        
        # Try to read pressure data
        data = bytearray(6)
        i2c.writeto_then_readfrom(address, bytes([0xF7]), data)  # Pressure MSB register
        print(f"Raw pressure data: {[hex(b) for b in data]}")
        
        # Simple raw pressure calculation
        pressure_raw = (data[0] << 16) | (data[1] << 8) | data[2]
        pressure = pressure_raw / 100.0  # Rough conversion
        
        print(f"Calculated pressure: {pressure:.1f} hPa")
        
        return pressure
        
    except Exception as e:
        print(f"QMP6988 error: {e}")
        return None

if __name__ == "__main__":
    print("Testing pressure sensor...")
    result = test_qmp6988()
    if result:
        print(f"SUCCESS: Pressure reading: {result:.1f} hPa")
    else:
        print("FAILED: Could not read pressure sensor")