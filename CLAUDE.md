# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a Raspberry Pi weather station that collects sensor data from indoor and outdoor sensors and sends it to `https://mrx3k1.de/weather-tracker/weather-tracker`. The system runs continuously via PM2 process manager.

## Current Production Setup

**Active Script**: `env3_dht22_combined.py` running via PM2  
**Sensors**:
- **Indoor**: M5 ENV III Module (I2C) - SHT30 (0x44) + QMP6988 (0x70)
- **Outdoor**: DHT22 on GPIO4 (Pin 7)
**Virtual Environment**: `/home/pi/apps/weather-station/venv/`

## Essential Commands

### Service Management
```bash
# Check status
pm2 status weather-station
pm2 logs weather-station --lines 50

# Restart service (after code changes)
pm2 restart weather-station

# Stop/Start service
pm2 stop weather-station
pm2 start ecosystem.config.js
```

### Testing & Diagnostics
```bash
# Test sensors with virtual environment
source venv/bin/activate
python env3_dht22_combined.py          # Run main script manually
python quick_test.py                   # Quick sensor test
deactivate

# Check I2C devices (should show 0x44 and 0x70)
sudo i2cdetect -y 1

# Monitor real-time output
mkdir -p logs  # Create logs directory if missing
tail -f logs/weather-station-out.log
```

### Development Workflow
```bash
# Virtual environment (ALWAYS use this)
source venv/bin/activate
# ... make changes and test ...
deactivate

# Git operations
git status
git add .
git commit -m "message"
git push origin main
```

## Architecture & Data Flow

### Sensor Reading Flow
1. **ENV III (Indoor)**:
   - SHT30 → I2C → `read_sht30()` → Temperature/Humidity
   - QMP6988 → I2C → `read_qmp6988()` → Pressure
   
2. **DHT22 (Outdoor)**:
   - GPIO4 → `read_dht22_simple()` → Temperature/Humidity via subprocess with venv Python

3. **Data Transmission**:
   - Collect readings → Format JSON → POST to server → 60-second interval

### JSON Payload Structure
```json
{
  "indoor": {
    "temperature": 20.5,
    "humidity": 66.1,
    "pressure": 1013.2
  },
  "outdoor": {
    "temperature": 27.5,
    "humidity": 63.3
  }
}
```

## Critical Configuration

### Boot Configuration (`/boot/firmware/config.txt`)
```
dtparam=i2c_arm=on,i2c_arm_baudrate=10000
dtoverlay=dht22,gpiopin=4
```
**WARNING**: Removing `dtoverlay=dht22,gpiopin=4` breaks DHT22 functionality

### PM2 Configuration (`ecosystem.config.js`)
- Uses venv interpreter: `/home/pi/apps/weather-station/venv/bin/python`
- Script: `env3_dht22_combined.py`
- Auto-restart enabled with 1GB memory limit
- Logs in `./logs/` directory

## Library Dependencies

### Virtual Environment (`venv/`)
```bash
# Core dependencies
adafruit-circuitpython-dht==4.0.9
Adafruit-Blinka==8.64.0  # DO NOT upgrade to 8.65.0
smbus2                   # I2C communication
requests==2.28.1         # HTTP requests
RPi.GPIO                 # GPIO control
```

### System Requirements
- I2C enabled via `raspi-config`
- User in `i2c` and `gpio` groups
- Python 3.11
- Node.js and PM2 for process management

## Common Issues & Solutions

### DHT22 "Sensor not found"
1. Check wiring: Pin 1 (VCC) → 3.3V, Pin 2 (DATA) → GPIO4 (Pin 7), Pin 4 (GND) → Ground
2. Verify device tree overlay exists in `/boot/firmware/config.txt`
3. Test with venv Python: `/home/pi/apps/weather-station/venv/bin/python -c "import board, adafruit_dht; dht = adafruit_dht.DHT22(board.D4, use_pulseio=False); print(f'DHT22: {dht.temperature}°C, {dht.humidity}%'); dht.exit()"`

### ENV III Not Responding
1. Check I2C: `sudo i2cdetect -y 1` (should show 0x44, 0x70)
2. Verify I2C enabled in boot config
3. Check physical connections: SDA→GPIO2, SCL→GPIO3

### Rate Limiting (HTTP 429)
- Server allows one reading per minute
- Normal behavior, will retry automatically

## Project Structure

```
weather-station/
├── env3_dht22_combined.py    # Main production script
├── ecosystem.config.js        # PM2 configuration
├── venv/                      # Virtual environment (critical)
├── logs/                      # Runtime logs
├── requirements.txt           # Python dependencies
├── archive/                   # Old test files
└── test_*.py                  # Various test scripts
```

## Hardware Pins Reference

**Raspberry Pi GPIO Usage**:
- Pin 1: 3.3V (Power for sensors)
- Pin 3: GPIO2/SDA (I2C Data)
- Pin 5: GPIO3/SCL (I2C Clock)
- Pin 7: GPIO4 (DHT22 Data)
- Pin 9: Ground

**Do not use other GPIO pins** - conflicts may occur with other services running on the Pi.