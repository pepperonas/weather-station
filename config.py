import os

# DHT22 Sensor Configuration
SENSOR_TYPE = "DHT22"
GPIO_PIN = 18

# Server Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10

# Timing Configuration
SENSOR_READ_INTERVAL = 2.0  # seconds
CONTINUOUS_MODE_INTERVAL = 60.0  # seconds for continuous monitoring

# Environment Variables Override
SERVER_URL = os.getenv('WEATHER_SERVER_URL', SERVER_URL)
GPIO_PIN = int(os.getenv('WEATHER_GPIO_PIN', GPIO_PIN))
REQUEST_TIMEOUT = int(os.getenv('WEATHER_REQUEST_TIMEOUT', REQUEST_TIMEOUT))