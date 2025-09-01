#!/usr/bin/env python3
import time

def test_gpio_pin(pin):
    """Test if a GPIO pin is available"""
    try:
        # Export GPIO
        with open('/sys/class/gpio/export', 'w') as f:
            f.write(str(pin))
        
        time.sleep(0.1)
        
        # Set as output
        with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
            f.write('out')
        
        # Set high
        with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
            f.write('1')
        
        # Read value
        with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
            val = f.read().strip()
        
        # Cleanup
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(str(pin))
        
        return val == '1'
        
    except Exception as e:
        print(f"GPIO{pin}: {e}")
        return False

if __name__ == "__main__":
    print("Testing available GPIO pins...")
    
    # Test common GPIO pins used for sensors
    test_pins = [4, 17, 18, 22, 23, 24, 25]
    
    available_pins = []
    for pin in test_pins:
        if test_gpio_pin(pin):
            available_pins.append(pin)
            print(f"✅ GPIO{pin}: Available")
        else:
            print(f"❌ GPIO{pin}: Not available")
    
    print(f"\nAvailable GPIO pins: {available_pins}")
    
    if available_pins:
        print(f"\n💡 Suggestion: Try connecting DHT22 to GPIO{available_pins[0]} instead of GPIO4")
