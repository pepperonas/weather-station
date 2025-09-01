#!/usr/bin/env python3
import time
import board
import adafruit_dht

print("=== DHT22 Alternative Methods Test ===")

# Test different initialization methods
methods = [
    {"name": "Standard (use_pulseio=False)", "params": {"use_pulseio": False}},
    {"name": "Default settings", "params": {}},
    {"name": "With pulseio=True", "params": {"use_pulseio": True}},
]

for i, method in enumerate(methods):
    print(f"\n--- Method {i+1}: {method['name']} ---")
    
    try:
        print("Initializing DHT22...")
        dht22 = adafruit_dht.DHT22(board.D4, **method["params"])
        print("✅ Initialization successful")
        
        # Try reading with longer delays
        for delay in [2, 3, 5]:
            print(f"Trying with {delay}s delay...")
            time.sleep(delay)
            
            try:
                temp = dht22.temperature
                hum = dht22.humidity
                
                if temp is not None and hum is not None:
                    print(f"  🎉 SUCCESS: {temp:.1f}°C, {hum:.1f}%")
                    dht22.exit()
                    print("DHT22 is working with this method!")
                    exit(0)
                else:
                    print(f"  ❌ No data with {delay}s delay")
            except Exception as e:
                print(f"  ❌ Error with {delay}s delay: {e}")
        
        dht22.exit()
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")

print("\n❌ All methods failed.")
