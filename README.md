# Weather Station

<div align="center">

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A.svg?logo=raspberrypi&logoColor=white)

A Python-based weather station for Raspberry Pi combining M5Stack ENV III (indoor) and DHT22 (outdoor) sensors for temperature, humidity, and barometric pressure monitoring.

</div>

## Features

- **Dual Sensor Setup** — Indoor (M5 ENV III via I2C) and outdoor (DHT22 via GPIO) measurements
- **Temperature & Humidity** — Real-time readings from both sensors
- **Barometric Pressure** — Atmospheric pressure tracking via ENV III (BMP280)
- **Data Logging** — Continuous sensor data collection with timestamps
- **Remote Reporting** — Sends data to a central monitoring server
- **Robust Error Handling** — Automatic sensor recovery and retry logic

## Quick Start

```bash
# Clone the repository
git clone https://github.com/pepperonas/weather-station.git
cd weather-station

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure sensors in config.py
# Start the station
python env3_dht22_combined.py
```

## Sensors

| Sensor | Interface | Measurements |
|--------|-----------|-------------|
| M5Stack ENV III | I2C | Temperature, humidity, pressure (indoor) |
| DHT22 | GPIO | Temperature, humidity (outdoor) |

## Tech Stack

- **Language** — Python 3.11
- **Sensors** — M5Stack ENV III (SHT30 + BMP280), DHT22
- **Communication** — I2C, GPIO
- **Process Manager** — PM2

## Author

**Martin Pfeffer** — [celox.io](https://celox.io)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
