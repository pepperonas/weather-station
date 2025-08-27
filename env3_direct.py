#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# GPIO Pins für I2C
SDA_PIN = 2  # GPIO2
SCL_PIN = 3  # GPIO3

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Reset I2C Bus manually
print("Resetting I2C bus manually...")
GPIO.setup(SDA_PIN, GPIO.OUT)
GPIO.setup(SCL_PIN, GPIO.OUT)

# Generate stop condition
GPIO.output(SDA_PIN, 0)
GPIO.output(SCL_PIN, 1)
time.sleep(0.001)
GPIO.output(SDA_PIN, 1)
time.sleep(0.001)

# Generate 9 clock pulses to clear bus
for _ in range(9):
    GPIO.output(SCL_PIN, 0)
    time.sleep(0.001)
    GPIO.output(SCL_PIN, 1)
    time.sleep(0.001)

# Set pins back to input (high impedance)
GPIO.setup(SDA_PIN, GPIO.IN)
GPIO.setup(SCL_PIN, GPIO.IN)

print("I2C bus reset complete")

# Now try I2C again
import smbus
bus = smbus.SMBus(1)

print("Scanning I2C bus 1 after reset...")
found = []
for addr in range(0x03, 0x77):
    try:
        bus.read_byte(addr)
        found.append(hex(addr))
    except:
        pass

if found:
    print(f"Found devices at: {', '.join(found)}")
else:
    print("No devices found")

bus.close()
GPIO.cleanup()
