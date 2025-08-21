import time
import board
import adafruit_dht
from config import GPIO_PIN, SENSOR_READ_INTERVAL

# Sensor setup
dht = adafruit_dht.DHT22(getattr(board, f'D{GPIO_PIN}'))

while True:
    try:
        humidity = dht.humidity
        temperature = dht.temperature
        if humidity is not None and temperature is not None:
            print(f"Temp: {temperature:.1f} C    Humidity: {humidity:.1f}%")
        else:
            print("Failed to read from sensor")
    except RuntimeError as error:
        print(f"Reading from DHT failure: {error.args[0]}")
    time.sleep(SENSOR_READ_INTERVAL)
