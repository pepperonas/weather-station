#!/usr/bin/env python3
"""
Test DHT22 on alternative GPIO pins
"""

import subprocess
import time

def test_gpio(gpio_num):
    """Test DHT22 on specified GPIO"""
    print(f"\nTesting DHT22 on GPIO{gpio_num}...")
    
    venv_python = "/home/pi/apps/weather-station/venv/bin/python"
    
    # Map GPIO to board pin
    gpio_map = {
        4: "D4",
        17: "D17",
        27: "D27",
        22: "D22"
    }
    
    board_pin = gpio_map.get(gpio_num, f"D{gpio_num}")
    
    test_code = f"""
import board
import adafruit_dht
import time

try:
    dht = adafruit_dht.DHT22(board.{board_pin}, use_pulseio=False)
    time.sleep(2)
    
    for attempt in range(3):
        try:
            temp = dht.temperature
            hum = dht.humidity
            if temp is not None and hum is not None:
                print(f"SUCCESS:GPIO{gpio_num}:{{temp:.1f}}:{{hum:.1f}}")
                break
            else:
                print(f"Attempt {{attempt+1}}: No data")
        except RuntimeError as e:
            print(f"Attempt {{attempt+1}}: {{e}}")
        time.sleep(2)
    
    dht.exit()
except Exception as e:
    print(f"ERROR:GPIO{gpio_num}:{{e}}")
"""
    
    try:
        result = subprocess.run(
            [venv_python, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = result.stdout.strip() or result.stderr.strip()
        
        if "SUCCESS" in output:
            parts = output.split(":")
            print(f"✅ GPIO{gpio_num} WORKING!")
            print(f"   Temperature: {parts[2]}°C")
            print(f"   Humidity: {parts[3]}%")
            return True
        else:
            print(f"❌ GPIO{gpio_num} failed: {output}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ GPIO{gpio_num} timeout")
        return False
    except Exception as e:
        print(f"❌ GPIO{gpio_num} error: {e}")
        return False

def main():
    print("="*60)
    print("DHT22 ALTERNATIVE GPIO TEST")
    print("="*60)
    print("\nThis will test DHT22 on different GPIO pins")
    print("Make sure DHT22 is connected to the pin being tested!")
    
    # Test common GPIO pins
    gpio_pins = [4, 17, 27, 22]
    working_pins = []
    
    print("\nPin mapping reference:")
    print("  GPIO4  → Physical Pin 7")
    print("  GPIO17 → Physical Pin 11")
    print("  GPIO27 → Physical Pin 13")
    print("  GPIO22 → Physical Pin 15")
    
    for gpio in gpio_pins:
        if test_gpio(gpio):
            working_pins.append(gpio)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if working_pins:
        print(f"✅ Working GPIO pins: {', '.join(map(str, working_pins))}")
        print("\nTo use a different GPIO:")
        print(f"1. Edit /boot/firmware/config.txt")
        print(f"   Change: dtoverlay=dht22,gpiopin={working_pins[0]}")
        print(f"2. Update your code to use board.D{working_pins[0]}")
        print(f"3. Reboot: sudo reboot")
    else:
        print("❌ No working GPIO pins found")
        print("\nPossible issues:")
        print("- DHT22 sensor damaged")
        print("- Power supply issue")
        print("- Missing pull-up resistor")

if __name__ == "__main__":
    main()