import time
import board
import busio
import struct

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

def scan_i2c():
    print("Scanning I2C bus...")
    devices = i2c.scan()
    for device in devices:
        print(f"Found device at address: 0x{device:02x}")
    return devices

def read_sht4x_raw(i2c_address=0x44):
    """Read SHT4x sensor raw data"""
    try:
        # SHT4x command: Measure T & RH with high precision
        cmd = bytearray([0xFD])
        
        with i2c as bus:
            bus.writeto(i2c_address, cmd)
            time.sleep(0.01)  # Wait for measurement
            
            # Read 6 bytes: temp_msb, temp_lsb, temp_crc, hum_msb, hum_lsb, hum_crc
            data = bytearray(6)
            bus.readfrom_into(i2c_address, data)
            
        print(f"Raw data: {[hex(b) for b in data]}")
        
        # Parse temperature
        temp_raw = (data[0] << 8) | data[1]
        temp_c = -45 + 175 * temp_raw / 65535.0
        
        # Parse humidity
        hum_raw = (data[3] << 8) | data[4]
        hum_rh = -6 + 125 * hum_raw / 65535.0
        hum_rh = max(0, min(100, hum_rh))  # Clamp to 0-100%
        
        print(f"Temperature: {temp_c:.2f}°C")
        print(f"Humidity: {hum_rh:.2f}%")
        
        return temp_c, hum_rh
        
    except Exception as e:
        print(f"SHT4x error: {e}")
        return None, None

def test_bmp_addresses():
    """Test different BMP280 addresses"""
    addresses = [0x70, 0x76, 0x77]
    
    for addr in addresses:
        try:
            print(f"\nTesting BMP280 at address 0x{addr:02x}...")
            
            # Read chip ID register (0xD0)
            cmd = bytearray([0xD0])
            result = bytearray(1)
            
            with i2c as bus:
                bus.writeto(addr, cmd)
                bus.readfrom_into(addr, result)
                
            chip_id = result[0]
            print(f"Chip ID: 0x{chip_id:02x}")
            
            if chip_id == 0x58:
                print("BMP280 detected!")
            elif chip_id == 0x60:
                print("BME280 detected!")
            else:
                print(f"Unknown chip ID: 0x{chip_id:02x}")
                
        except Exception as e:
            print(f"No device at 0x{addr:02x}: {e}")

if __name__ == "__main__":
    devices = scan_i2c()
    
    if 0x44 in devices:
        print("\n=== Testing SHT4x ===")
        temp, hum = read_sht4x_raw()
    
    print("\n=== Testing BMP280/BME280 ===")
    test_bmp_addresses()