#!/usr/bin/env python3
import time
import os

def read_dht22_direct():
    """Direct GPIO bit-banging DHT22 read"""
    try:
        import RPi.GPIO as GPIO
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT)
        
        # Send start signal
        GPIO.output(4, GPIO.LOW)
        time.sleep(0.018)  # 18ms low
        
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        time.sleep(0.00004)  # 40us
        
        # Read response
        data = []
        j = 0
        while GPIO.input(4) == GPIO.LOW:
            continue
        while GPIO.input(4) == GPIO.HIGH:
            continue
        
        # Read 40 bits of data
        for i in range(40):
            j = 0
            while GPIO.input(4) == GPIO.LOW:
                continue
            while GPIO.input(4) == GPIO.HIGH:
                j += 1
                if j > 100:
                    break
            if j > 8:
                data.append(1)
            else:
                data.append(0)
        
        GPIO.cleanup()
        
        # Convert to bytes
        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        check_bit = data[32:40]
        
        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0
        
        for i in range(8):
            humidity += humidity_bit[i] * 2 ** (7-i)
            humidity_point += humidity_point_bit[i] * 2 ** (7-i)
            temperature += temperature_bit[i] * 2 ** (7-i)
            temperature_point += temperature_point_bit[i] * 2 ** (7-i)
            check += check_bit[i] * 2 ** (7-i)
        
        tmp = humidity + humidity_point + temperature + temperature_point
        if check == tmp:
            humidity = humidity + humidity_point / 10.0
            temperature = temperature + temperature_point / 10.0
            return temperature, humidity
        else:
            return None, None
        
    except Exception as e:
        print(f"Direct GPIO error: {e}")
        return None, None

if __name__ == "__main__":
    print("Testing DHT22 with direct GPIO access...")
    
    for attempt in range(3):
        temp, humidity = read_dht22_direct()
        if temp is not None:
            print(f"✅ DHT22: {temp:.1f}°C, {humidity:.1f}%")
            break
        else:
            print(f"Attempt {attempt + 1} failed")
            time.sleep(2)
    else:
        print("❌ All direct GPIO attempts failed")
