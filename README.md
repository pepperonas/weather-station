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
- **Barometric Pressure** — Atmospheric pressure tracking via ENV III (QMP6988)
- **Data Logging** — Continuous sensor data collection with timestamps
- **Remote Reporting** — Sends data to a central monitoring server
- **Robust Error Handling** — Automatic sensor recovery and retry logic

## Wiring Diagram

```
    Raspberry Pi 3B
    ┌──────────────┐
    │              │         M5Stack ENV III (Indoor)
    │              │         ┌──────────────────────┐
    │    SDA (I2C) ●─────────┤ SDA                  │
    │   GPIO 2     │         │                      │
    │   (Pin 3)    │         │  SHT30  (0x44) Temp/Hum
    │              │         │  QMP6988 (0x70) Pressure
    │    SCL (I2C) ●─────────┤ SCL                  │
    │   GPIO 3     │         │                      │
    │   (Pin 5)    │         │                      │
    │              │         │                      │
    │      3.3V ●──┼─────────┤ VCC                  │
    │   (Pin 1)    │         │                      │
    │              │         │                      │
    │      GND ●───┼─────────┤ GND                  │
    │   (Pin 9)    │         └──────────────────────┘
    │              │
    │              │         DHT22 Sensor (Outdoor)
    │              │         ┌──────────────────────┐
    │   GPIO 18 ●──┼─────────┤ DATA                 │
    │   (Pin 12)   │         │                      │
    │              │    ┌────┤ VCC ◄── 3.3V         │
    │      3.3V ●──┼────┘    │                      │
    │   (Pin 17)   │         │                      │
    │              │    ┌────┤ GND                   │
    │      GND ●───┼────┘    └──────────────────────┘
    │   (Pin 14)   │
    └──────────────┘
                         ┌─────────────────────────┐
                         │  10kΩ Pull-up Resistor   │
                         │  between DATA and VCC    │
                         └─────────────────────────┘

    Pin Mapping:
    ┌──────────┬──────────┬─────────────────────────────────┐
    │ Pi Pin   │ GPIO     │ Connection                      │
    ├──────────┼──────────┼─────────────────────────────────┤
    │ Pin 3    │ GPIO 2   │ I2C SDA → ENV III SDA           │
    │ Pin 5    │ GPIO 3   │ I2C SCL → ENV III SCL           │
    │ Pin 12   │ GPIO 18  │ DHT22 DATA                      │
    │ Pin 1/17 │ 3.3V     │ Sensor power                    │
    │ Pin 9/14 │ GND      │ Common ground                   │
    └──────────┴──────────┴─────────────────────────────────┘

    I2C Addresses: SHT30 = 0x44, QMP6988 = 0x70
```

> **Note:** Enable I2C via `raspi-config`. The DHT22 requires a 10kΩ pull-up resistor between DATA and VCC. Add `dtoverlay=dht22,gpiopin=18` to `/boot/firmware/config.txt`.

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

| Sensor | Interface | Address | Measurements |
|--------|-----------|---------|-------------|
| SHT30 (ENV III) | I2C | 0x44 | Temperature, humidity (indoor) |
| QMP6988 (ENV III) | I2C | 0x70 | Barometric pressure (indoor) |
| DHT22 | GPIO 18 | — | Temperature, humidity (outdoor) |

## Tech Stack

- **Language** — Python 3.11
- **Sensors** — M5Stack ENV III (SHT30 + QMP6988), DHT22
- **Communication** — I2C (smbus2), GPIO (adafruit-circuitpython-dht)
- **Process Manager** — PM2

## Author

**Martin Pfeffer** — [celox.io](https://celox.io)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
