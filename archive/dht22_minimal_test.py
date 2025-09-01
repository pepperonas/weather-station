#!/usr/bin/env python3
import time
import board
import adafruit_dht

print('Testing DHT22 on GPIO 18...')
print('Creating sensor object...')

try:
    dht = adafruit_dht.DHT22(board.D18, use_pulseio=False)
    print('Sensor object created successfully')
    
    for i in range(5):  # Try 5 times
        print(f'\nAttempt {i+1}/5:')
        try:
            time.sleep(2)
            temp = dht.temperature
            hum = dht.humidity
            
            if temp is not None and hum is not None:
                print(f'SUCCESS: Temperature: {temp:.1f}°C, Humidity: {hum:.1f}%')
                break
            else:
                print('Reading returned None values')
                
        except RuntimeError as e:
            print(f'Runtime error: {e}')
        except Exception as e:
            print(f'Other error: {e}')
    
    print('\nCleaning up...')
    dht.exit()
    print('Test completed')
    
except Exception as e:
    print(f'Failed to create sensor: {e}')
