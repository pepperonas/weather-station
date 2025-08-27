import time
import requests
import board
import adafruit_dht
from config import SENSOR_TYPE, GPIO_PIN, SERVER_URL, REQUEST_TIMEOUT

# Sensor setup
dht = adafruit_dht.DHT22(getattr(board, f'D{GPIO_PIN}'))

# Server URL
url = SERVER_URL

def send_data(temp, humidity):
    try:
        data = {
            'temperature': temp,
            'humidity': humidity,
            'timestamp': int(time.time())
        }
        response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            print(f"Data sent successfully: {temp:.1f}°C, {humidity:.1f}%")
        else:
            print(f"Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")

try:
    humidity = dht.humidity
    temperature = dht.temperature
    
    if humidity is not None and temperature is not None:
        print(f"Temp: {temperature:.1f}°C    Humidity: {humidity:.1f}%")
        send_data(temperature, humidity)
    else:
        print("Failed to read from sensor")
except RuntimeError as error:
    print(f"Reading from DHT failure: {error.args[0]}")
