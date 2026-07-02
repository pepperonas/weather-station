# Weather Station

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)
![Sensors](https://img.shields.io/badge/Sensors-ENV%20III%20%2B%20DHT22-orange?logo=arduino&logoColor=white)
![I2C](https://img.shields.io/badge/Bus-I2C%20%28smbus2%29-blue)
![Service](https://img.shields.io/badge/Service-systemd-informational?logo=linux&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-55%20passing-brightgreen?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Made with love](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red)

A Python-based weather station for Raspberry Pi that combines an **M5Stack ENV III** (indoor, I2C) and a **DHT22** (outdoor, GPIO) sensor to collect temperature, humidity, and barometric pressure data and POST it to a remote monitoring server every 60 seconds.

</div>

## Features

- **Dual Sensor Setup** — Indoor (M5 ENV III via I2C) and outdoor (DHT22 via GPIO) measurements
- **Temperature & Humidity** — Real-time readings from both sensors
- **Barometric Pressure** — Atmospheric pressure tracking via ENV III (QMP6988)
- **CRC Validation** — SHT30 data integrity verified with CRC-8/MAXIM on every read
- **Sensor Caching** — Stale sensor values re-used for up to 5 minutes on transient failures
- **Data Logging** — Continuous sensor data collection with Unix timestamps
- **Remote Reporting** — Sends JSON payload to a central monitoring server via HTTP POST
- **Robust Error Handling** — Automatic I2C bus reset, per-sensor retry logic, and graceful degradation
- **systemd Service** — Runs as a supervised system service (`weather-station.service`)

## Wiring Diagram

```
    Raspberry Pi 3B
    ┌──────────────┐
    │              │              M5Stack ENV III (Indoor)
    │              │              ┌──────────────────────┐
    │   SDA   (3) ─┼──────────────┤── SDA                │
    │   GPIO 2     │              │                      │
    │   SCL   (5) ─┼──────────────┤── SCL   SHT30  0x44 │
    │   GPIO 3     │              │         QMP6988 0x70 │
    │  3.3V   (1) ─┼──────────────┤── VCC                │
    │              │         ┌────┤── GND                │
    │   GND   (9) ─┼─────────┤    └──────────────────────┘
    │              │         │
    │              │         │    DHT22 Sensor (Outdoor)
    │              │         │    ┌──────────────────────┐
    │  GPIO24(18) ─┼─────────┼────┤── DATA  ──┐          │
    │              │         │    │          [10kΩ]      │
    │  3.3V  (17) ─┼─────────┼────┤── VCC   ──┘          │
    │              │         │    │                      │
    │   GND  (14) ─┼─────────┴────┤── GND                │
    │              │              └──────────────────────┘
    └──────────────┘

    ┌──────────┬──────────┬──────────────────────────────────┐
    │ Pi Pin   │ GPIO     │ Connection                       │
    ├──────────┼──────────┼──────────────────────────────────┤
    │ Pin 3    │ GPIO 2   │ I2C SDA → ENV III               │
    │ Pin 5    │ GPIO 3   │ I2C SCL → ENV III               │
    │ Pin 18   │ GPIO 24  │ DHT22 DATA (10kΩ pull-up)       │
    │ Pin 1/17 │ 3.3V     │ Sensor power                    │
    │ Pin 9/14 │ GND      │ Common ground                   │
    └──────────┴──────────┴──────────────────────────────────┘
```

> **Note:** Enable I2C via `raspi-config`. The DHT22 is on **GPIO24 (Pin 18), powered from 5 V**, and needs a 10kΩ pull-up resistor between DATA and VCC. Add `dtoverlay=dht22,gpiopin=24` to `/boot/firmware/config.txt`.

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

## Run as a systemd Service

```bash
# Copy and enable the service
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now weather-station

# Check logs
sudo journalctl -u weather-station -f
```

## Sensors

| Sensor | Interface | Address | Measurements |
|--------|-----------|---------|-------------|
| SHT30 (ENV III) | I2C | 0x44 | Temperature, humidity (indoor) |
| QMP6988 (ENV III) | I2C | 0x70 | Barometric pressure (indoor) |
| DHT22 | GPIO 24 | — | Temperature, humidity (outdoor) |

## Data Payload

Each 60-second cycle POSTs a JSON object to the configured `SERVER_URL`:

```json
{
  "timestamp": 1717000000,
  "temperature": 22.1,
  "humidity": 55.3,
  "temperature_indoor": 22.1,
  "humidity_indoor": 55.3,
  "sensor_indoor": "ENV3",
  "pressure": 1013.2,
  "pressure_indoor": 1013.2,
  "temperature_outdoor": 18.4,
  "humidity_outdoor": 70.0,
  "sensor_outdoor": "DHT22"
}
```

## Tech Stack

- **Language** — Python 3.11
- **Sensors** — M5Stack ENV III (SHT30 + QMP6988), DHT22
- **Communication** — I2C (`smbus2`), GPIO (`adafruit-circuitpython-dht`)
- **Process Manager** — systemd
- **Testing** — pytest

## Tests

Install dev dependencies and run the unit tests — no hardware required:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

The test suite (55 tests) covers pure weather-calculation logic:

- **CRC-8/MAXIM** — the checksum algorithm used by the SHT30 sensor, including the datasheet example vector
- **Temperature conversions** — °C ↔ °F (freezing, boiling, −40 identity point, body temperature, round-trip)
- **Pressure conversions** — hPa ↔ inHg (standard atmosphere, round-trip)
- **Wind-speed conversions** — m/s ↔ km/h (zero, 10 m/s, Beaufort-8 gale, round-trip)
- **Dew point** — Magnus formula (saturated air, dry air, typical indoor, sub-zero)
- **Heat index** — Steadman formula (hot/humid, extreme RH, humidity-monotonicity)
- **Wind chill** — Environment Canada formula (calm, strong wind, colder-temp monotonicity)
- **Compass direction** — 16-point mapping (N/S/E/W, NE/SW/NW, NNW, 360° wrap)
- **SHT30 raw-register conversion** — 16-bit → °C and %RH at min/max/midpoint
- **Sensor sanity checks** — valid/invalid temperature and humidity ranges
- **Payload assembly** — both sensors, indoor-only, outdoor-only, no sensors, rounding, pressure fields

## Author

**Martin Pfeffer** — [celox.io](https://celox.io)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
