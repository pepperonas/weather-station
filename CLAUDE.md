# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based weather station for Raspberry Pi that collects temperature, humidity, and pressure data from sensors and sends it to a remote server. The project supports two sensor architectures:

1. **M5 Cardputer Sensors** (current/preferred): SHT30 (temperature/humidity) + QMP6988 (pressure) via I2C
2. **Legacy DHT22** (deprecated): Single sensor via GPIO

## Architecture

### Sensor Implementation Layers
- **Raw I2C Communication**: Direct sensor communication using `adafruit-blinka` and `busio`
- **Sensor Reading Functions**: Hardware-specific functions (`read_sht30_raw()`, `read_qmp6988_raw()`)
- **Data Transmission**: HTTP POST to remote API endpoint with JSON payload
- **Process Management**: PM2 for continuous operation with auto-restart

### Key Components
- `config.py`: Centralized configuration with environment variable overrides (Note: defaults to DHT22 but overridden by PM2)
- `ecosystem.config.js`: PM2 process configuration
- `m5_env_continuous_sender.py`: Main production script for M5 sensors
- `weather-station.service`: Legacy systemd service (not actively used)

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Enable I2C (required for M5 sensors)
sudo raspi-config  # Interface Options -> I2C -> Enable
```

### Process Management
```bash
# Start weather station
pm2 start ecosystem.config.js
pm2 save

# Monitor status and logs
pm2 status
pm2 logs weather-station
pm2 logs weather-station --lines 20

# Restart/stop
pm2 restart weather-station
pm2 stop weather-station

# Configuration changes require delete/recreate
pm2 delete weather-station
pm2 start ecosystem.config.js
```

### Testing and Diagnostics
```bash
# Test M5 sensors (single reading)
python m5_env_sender.py

# Test continuous monitoring (Ctrl+C to stop)
python m5_env_continuous_sender.py

# Sensor diagnostics
python m5_sensor_test.py

# Pressure sensor testing
python pressure_test.py
python debug_pressure.py

# Scan I2C devices
sudo i2cdetect -y 1
# Expected: 0x44 (SHT30), 0x70 (QMP6988)

# Check systemd PM2 service
sudo systemctl status pm2-pi
journalctl -u pm2-pi -f
```

## Script Categories

### M5 Cardputer Scripts (Current)
- `m5_env_sender.py`: Single measurement with pressure support
- `m5_env_continuous_sender.py`: Production continuous monitoring (used by PM2)
- `m5_continuous_sender.py`: Continuous monitoring without pressure
- `m5_sensor_sender.py`: Alternative sensor implementation
- `m5_sensor_test.py`: Diagnostics and testing

### Legacy DHT22 Scripts (Deprecated)
- `dht_22_sender.py`: Single measurement
- `continuous_sender.py`: Continuous monitoring
- `dht_22.py`: Basic sensor reading

### Development/Testing Scripts
- `mock_sender.py`: Generates fake data for testing
- `m5_fixed_sender.py`: Fixed test data
- `pressure_test.py`: QMP6988 pressure sensor testing
- `debug_pressure.py`: Pressure sensor debugging

## Data Format

```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "pressure": 1013.25,
  "timestamp": 1642694400
}
```

The `pressure` field is optional and only included when QMP6988 sensor is available.

## Configuration Management

### Primary Configuration (`config.py`)
- Default sensor type: DHT22 (legacy)
- GPIO pin for DHT22: 18
- Server URL and timeout settings
- Environment variable overrides for all settings

### PM2 Configuration (`ecosystem.config.js`)
- Script: `m5_env_continuous_sender.py` (overrides config.py default)
- Process settings and auto-restart
- Environment variables for production
- Log file locations

### Environment Variables
- `WEATHER_SERVER_URL`: API endpoint (default: https://mrx3k1.de/weather-tracker/weather-tracker)
- `WEATHER_GPIO_PIN`: DHT22 GPIO pin (legacy)
- `WEATHER_REQUEST_TIMEOUT`: HTTP timeout (default: 10)

## Switching Between Sensor Types

To change from DHT22 to M5 sensors or vice versa:

1. Update `ecosystem.config.js` args field with appropriate script
2. Delete and recreate PM2 process: `pm2 delete weather-station && pm2 start ecosystem.config.js`
3. Verify with `pm2 logs weather-station`

## Log Management

Logs are written to:
- `logs/weather-station-out.log`: Standard output
- `logs/weather-station-error.log`: Error output  
- `logs/weather-station-combined.log`: Combined logs

PM2 automatically rotates logs and provides structured logging.

## I2C Sensor Addresses

- **SHT30** (Temperature/Humidity): `0x44`
- **QMP6988** (Pressure): `0x70`

Always verify sensor detection with `sudo i2cdetect -y 1` before troubleshooting code issues.

## Dependencies

From `requirements.txt`:
- `adafruit-circuitpython-dht`: DHT sensor support
- `requests==2.28.1`: HTTP client for API communication
- `RPi.GPIO`: GPIO access for Raspberry Pi

Additional dependencies used by M5 scripts (installed via adafruit-circuitpython-dht):
- `adafruit-blinka`: CircuitPython compatibility layer
- `busio`: I2C bus communication

## Troubleshooting

### I2C Issues
- Verify I2C is enabled: `sudo raspi-config`
- Check sensor detection: `sudo i2cdetect -y 1`
- Ensure user has I2C permissions: `sudo usermod -a -G i2c pi`

### Sensor Reading Issues
- Use `m5_sensor_test.py` for diagnostics
- Check pressure with `pressure_test.py` or `debug_pressure.py`
- Verify wiring and power supply

### Process Management Issues
- Check PM2 status: `pm2 status`
- View logs: `pm2 logs weather-station`
- Restart PM2 daemon: `pm2 kill && pm2 resurrect`