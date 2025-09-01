#!/usr/bin/env python3
import time
import board
import adafruit_dht

print('=== DHT22 Test on GPIO4 (Pin 7) ===')
print('Hardware: DHT22 Sensor')
print('GPIO: 4 (Physical Pin 7)')
print('Power: 3.3V')
print('')

try:
    print('Initializing DHT22...')
    dht22 = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    print('✅ DHT22 initialized successfully')
    
    print('\nWaiting 3 seconds for sensor stabilization...')
    time.sleep(3)
    
    print('\nStarting 5 reading attempts:')
    success_count = 0
    
    for attempt in range(1, 6):
        print(f'\nAttempt {attempt}/5:')
        try:
            # Read sensor
            temperature = dht22.temperature
            humidity = dht22.humidity
            
            if temperature is not None and humidity is not None:
                print(f'  ✅ SUCCESS: Temperature = {temperature:.1f}°C, Humidity = {humidity:.1f}%')
                success_count += 1
            else:
                print('  ❌ No data returned (None values)')
                
        except RuntimeError as e:
            print(f'  ❌ Runtime Error: {e}')
        except Exception as e:
            print(f'  ❌ Unexpected Error: {e}')
            
        # Wait between attempts
        if attempt < 5:
            time.sleep(2)
    
    print(f'\n=== Test Results ===')
    print(f'Successful readings: {success_count}/5')
    if success_count > 0:
        print('✅ DHT22 is working on GPIO4!')
    else:
        print('❌ DHT22 failed all attempts')
        print('Check:')
        print('- Wiring: VCC→3.3V, GND→GND, DATA→GPIO4')
        print('- Pull-up resistor: 10kΩ between DATA and VCC')
        print('- Sensor condition')
    
    print('\nCleaning up...')
    dht22.exit()
    print('DHT22 released')
    
except Exception as e:
    print(f'❌ INITIALIZATION ERROR: {e}')
    print('Possible causes:')
    print('- GPIO4 is busy (check with: sudo lsof /dev/gpiochip0)')
    print('- Missing permissions')
    print('- Hardware not connected')

print('\nTest completed.')
