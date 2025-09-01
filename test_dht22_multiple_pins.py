#!/usr/bin/env python3
import time
import board
import adafruit_dht

print("=== DHT22 Multi-Pin Test ===")
print("Suche DHT22 auf verschiedenen GPIO Pins...")

# Test common GPIO pins for DHT22
gpio_pins = [
    (4, "D4", "Pin 7"),
    (17, "D17", "Pin 11"), 
    (18, "D18", "Pin 12"),
    (22, "D22", "Pin 15"),
    (23, "D23", "Pin 16"),
    (24, "D24", "Pin 18"),
    (25, "D25", "Pin 22"),
    (27, "D27", "Pin 13")
]

for gpio_num, board_pin, physical_pin in gpio_pins:
    print(f"\n--- Testing GPIO{gpio_num} ({physical_pin}) ---")
    
    try:
        pin = getattr(board, board_pin)
        dht22 = adafruit_dht.DHT22(pin, use_pulseio=False)
        print(f"✅ DHT22 initialized on GPIO{gpio_num}")
        
        time.sleep(3)
        
        try:
            temp = dht22.temperature
            hum = dht22.humidity
            
            if temp is not None and hum is not None:
                print(f"🎉 FOUND DHT22: GPIO{gpio_num} = {temp:.1f}°C, {hum:.1f}%")
                dht22.exit()
                exit(0)
            else:
                print(f"❌ GPIO{gpio_num}: No data")
                
        except RuntimeError as e:
            print(f"❌ GPIO{gpio_num}: {e}")
        except Exception as e:
            print(f"❌ GPIO{gpio_num}: Unexpected error: {e}")
            
        dht22.exit()
        
    except Exception as e:
        print(f"❌ GPIO{gpio_num}: Cannot initialize: {e}")

print("\n❌ DHT22 not found on any tested GPIO pin")
print("Check physical wiring!")
