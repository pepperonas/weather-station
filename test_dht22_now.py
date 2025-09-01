#!/usr/bin/env python3
import time
import board
import adafruit_dht

print('TESTING DHT22 on GPIO4...')
print('Board.D4 =', board.D4)

# Try with different initialization methods
methods = [
    ('use_pulseio=False', {'use_pulseio': False}),
    ('use_pulseio=True', {'use_pulseio': True}),
    ('no params', {})
]

for method_name, params in methods:
    print(f'\nTrying with {method_name}...')
    try:
        dht = adafruit_dht.DHT22(board.D4, **params)
        print('  DHT22 object created')
        
        time.sleep(3)
        temp = dht.temperature
        hum = dht.humidity
        
        if temp is not None and hum is not None:
            print(f'  ✅ SUCCESS: {temp:.1f}°C, {hum:.1f}%')
            dht.exit()
            break
        else:
            print('  ❌ No data returned')
        
        dht.exit()
        
    except Exception as e:
        print(f'  ❌ ERROR: {e}')
    
    time.sleep(2)

print('\nTest complete')
