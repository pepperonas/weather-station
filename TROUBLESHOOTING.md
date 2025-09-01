# Weather Station Troubleshooting Guide

## Current Issues & Solutions

### 1. ENV III Shows High Temperature (~30°C instead of ~22°C)

**Symptoms:**
- Indoor temperature readings 5-10°C too high
- Humidity readings seem correct

**Causes:**
- Temporary sensor drift after power cycle
- Self-heating from electronics
- I2C communication errors

**Solution:**
- Restart PM2 service: `pm2 restart weather-station`
- Wait 2-3 minutes for sensor to stabilize
- Normal indoor temperature should be 20-25°C

### 2. DHT22 Not Responding

**Symptoms:**
- "DHT sensor not found, check wiring" error
- Timeout when reading DHT22
- GPIO4 busy error

**Possible Causes:**
1. **Hardware connection issue** (most likely)
   - Loose dupont wires
   - Corroded pins
   - Damaged DHT22 sensor
   
2. **Software conflicts**
   - GPIO4 used by another process
   - Missing device tree overlay

**Diagnostics:**
```bash
# Check if device tree overlay is loaded
cat /boot/firmware/config.txt | grep dht22
# Should show: dtoverlay=dht22,gpiopin=4

# Test DHT22 directly (stop PM2 first)
pm2 stop weather-station
/home/pi/apps/weather-station/venv/bin/python -c "
import board, adafruit_dht
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
print(f'Temp: {dht.temperature}°C')
dht.exit()
"
```

**Hardware Check:**
- Pin 1 (VCC): 3.3V power
- Pin 2 (DATA): GPIO4 (Physical Pin 7)  
- Pin 3: Not connected
- Pin 4 (GND): Ground

**Recommendation:** 
Replace DHT22 with more reliable sensor like BME280 (I2C)

### 3. QMP6988 I/O Error

**Symptoms:**
- "ENV III QMP6988 error: [Errno 121] Remote I/O error"
- Pressure readings missing

**Cause:**
- QMP6988 enters sleep mode
- I2C address 0x70 not always visible

**Solution:**
- This is non-critical - temperature/humidity still work
- Pressure sensor requires initialization sequence

### 4. Both Sensors Show Wrong Values

**If ENV III shows high temp AND DHT22 fails:**
1. Check power supply - unstable 3.3V can cause issues
2. Verify I2C speed: `i2c_arm_baudrate=10000` in `/boot/firmware/config.txt`
3. Check for electromagnetic interference near sensors

## Quick Fix Procedure

```bash
# 1. Stop service
pm2 stop weather-station

# 2. Test sensors individually  
python3 /home/pi/apps/weather-station/debug_sensors.py

# 3. If sensors work, restart service
pm2 start weather-station

# 4. Monitor logs
pm2 logs weather-station --lines 30
```

## System Health Check

```bash
# Check all I2C devices
sudo i2cdetect -y 1

# Expected output:
# 0x44 = SHT30 (ENV III temperature/humidity)
# 0x70 = QMP6988 (ENV III pressure) - may be missing

# Check service status
pm2 status weather-station

# View recent data sent
tail -f logs/weather-station-out-*.log | grep "Sending:"
```

## When to Replace Hardware

Consider hardware replacement if:
- DHT22 consistently fails after checking wiring
- ENV III temperature off by >5°C after stabilization
- I2C devices not detected at expected addresses

## Recommended Improvements

1. **Replace DHT22 with BME280** (I2C, more reliable)
2. **Add pull-up resistors** (4.7kΩ) on I2C lines if unstable
3. **Shield sensors** from direct sunlight and heat sources
4. **Use shielded cables** for outdoor sensor connections