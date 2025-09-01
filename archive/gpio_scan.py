#!/usr/bin/env python3
import time
import board
import adafruit_dht

# Common GPIO pins to test
test_pins = [4, 17, 18, 27, 22, 23, 24, 25]

for pin in test_pins:
    print(f'\nTesting GPIO {pin}...')
    try:
        dht = adafruit_dht.DHT22(getattr(board, f'D{pin}'), use_pulseio=False)
        time.sleep(1)
        temp = dht.temperature
        hum = dht.humidity
        
        if temp is not None and hum is not None:
            print(f'*** SUCCESS on GPIO {pin}: {temp:.1f}°C, {hum:.1f}% ***')
            dht.exit()
            break
        else:
            print(f'GPIO {pin}: No data')
        
        dht.exit()
    except Exception as e:
        print(f'GPIO {pin}: {type(e).__name__}: {e}')

print('\nGPIO scan completed')
