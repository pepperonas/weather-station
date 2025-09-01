# RASPBERRY PI 3B SENSOR FIX INSTRUCTIONS

## 🔴 PROBLEM IDENTIFIED

Both sensor systems are not working on Raspberry Pi 3B:
- **I2C sensors (ENV III)**: Not detected at all (0x44, 0x70 missing)
- **DHT22 sensor**: "Sensor not found" error

## 🛠️ SOLUTION STEPS

### Step 1: Fix I2C Configuration
The I2C baudrate is set too low (10000) for reliable communication on Pi 3B.

```bash
# Run the fix script with sudo
sudo ./fix_config.sh

# This will:
# - Change I2C baudrate from 10000 to 100000
# - Add I2C pull-up resistors (gpio=2,3=pu)
# - Create a backup of your config

# Then reboot
sudo reboot
```

### Step 2: After Reboot - Test Sensors
```bash
# Test with the debug script
python debug_sensors.py
```

### Step 3: If DHT22 Still Fails
The DHT22 might need a different GPIO pin on Pi 3B.

```bash
# Test alternative GPIO pins
python test_alternative_gpio.py
```

If GPIO17 works better than GPIO4:
1. Edit `/boot/firmware/config.txt`:
   ```
   # Change from:
   dtoverlay=dht22,gpiopin=4
   # To:
   dtoverlay=dht22,gpiopin=17
   ```

2. Move DHT22 data wire from Pin 7 (GPIO4) to Pin 11 (GPIO17)

3. Update code to use `board.D17` instead of `board.D4`

### Step 4: Hardware Checks

#### ENV III Module Connections:
```
ENV III → Raspberry Pi
VCC (red) → Pin 1 (3.3V)
GND (black) → Pin 9 (Ground)
SDA (yellow) → Pin 3 (GPIO2/SDA)
SCL (white) → Pin 5 (GPIO3/SCL)
```

#### DHT22 Connections:
```
DHT22 → Raspberry Pi
Pin 1 (VCC) → Pin 1 (3.3V) or Pin 2 (5V)
Pin 2 (Data) → Pin 7 (GPIO4) or Pin 11 (GPIO17)
Pin 3 (NC) → Not connected
Pin 4 (GND) → Pin 9 (Ground)

⚠️ Add 10kΩ pull-up resistor between Data and VCC
```

## 📊 EXPECTED RESULTS

After fixes, `python debug_sensors.py` should show:
- ✅ I2C devices: 0x44 (SHT30), 0x70 (QMP6988)
- ✅ DHT22: Temperature and humidity readings

## 🆘 IF STILL NOT WORKING

### Power Issues:
- Try powering sensors separately
- Use 5V for DHT22 (with level shifter if needed)
- Check if Pi 3B provides enough current

### Cable Issues:
- Replace jumper wires
- Use shorter cables
- Solder connections directly

### Compatibility Issues:
The Pi 3B uses different hardware than Pi 5:
- Different GPIO controller (BCM2837 vs BCM2712)
- Different I2C timing
- May need kernel parameter adjustments

### Last Resort:
```bash
# Try legacy GPIO access
echo "4" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio4/direction

# Or use different Python library
pip install RPi.GPIO
# Then use RPi.GPIO instead of Blinka
```

## 📝 NOTES

The code worked on Pi 5 but not Pi 3B because:
1. **I2C timing differences** - Pi 3B needs standard baudrate (100000)
2. **GPIO differences** - Different hardware controllers
3. **Power differences** - Pi 3B provides less current on GPIO
4. **Kernel differences** - Newer kernel may handle devices differently

## ✅ QUICK CHECKLIST

- [ ] Run `sudo ./fix_config.sh`
- [ ] Reboot with `sudo reboot`
- [ ] Test with `python debug_sensors.py`
- [ ] If I2C works but DHT22 doesn't, try GPIO17
- [ ] Check all physical connections
- [ ] Add pull-up resistor to DHT22 if missing