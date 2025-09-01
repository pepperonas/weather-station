#!/usr/bin/env python3
import time
import board
import adafruit_dht

print('Testing DHT22 on GPIO 4 (your actual connection)...')

try:
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    print('DHT22 object created')
    
    for i in range(5):
        print(f'\nAttempt {i+1}:')
        try:
            time.sleep(3)  # Longer delay for DHT22
            temp = dht.temperature
            hum = dht.humidity
            
            if temp is not None and hum is not None:
                print(f'*** DHT22 SUCCESS: {temp:.1f}°C, {hum:.1f}% ***')
                break
            else:
                print('No data received')
                
        except RuntimeError as e:
            print(f'Runtime error: {e}')
        except Exception as e:
            print(f'Other error: {e}')
    
    dht.exit()
    print('DHT22 test completed')
    
except Exception as e:
    print(f'Failed to create DHT22: {e}')
