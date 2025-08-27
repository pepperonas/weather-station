#!/usr/bin/env python3
import os
import time

# Set very slow I2C speed
os.system('sudo modprobe -r i2c_bcm2835')
os.system('sudo modprobe i2c_bcm2835 baudrate=1000')
time.sleep(1)

import smbus
bus = smbus.SMBus(1)

print('Testing ENV III at 1kHz I2C speed...')

for addr in [0x44, 0x45, 0x70, 0x71]:
    try:
        # Just try to read one byte
        data = bus.read_byte(addr)
        print(f'✓ Found device at {hex(addr)}: {hex(data)}')
    except Exception as e:
        print(f'✗ {hex(addr)}: {e}')

bus.close()

# Reset to normal speed
os.system('sudo modprobe -r i2c_bcm2835')
os.system('sudo modprobe i2c_bcm2835')
