#!/bin/bash

echo "====================================="
echo "FIXING RASPBERRY PI 3B CONFIGURATION"
echo "====================================="
echo ""
echo "This script will:"
echo "1. Change I2C baudrate from 10000 to 100000"
echo "2. Add I2C pull-up resistors"
echo "3. Try alternative GPIO for DHT22 if needed"
echo ""
echo "Run with: sudo ./fix_config.sh"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run with sudo"
   echo "   sudo ./fix_config.sh"
   exit 1
fi

# Backup current config
echo "Creating backup..."
cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d_%H%M%S)

# Fix I2C baudrate
echo "Fixing I2C baudrate..."
sed -i 's/dtparam=i2c_arm=on,i2c_arm_baudrate=10000/dtparam=i2c_arm=on,i2c_arm_baudrate=100000/' /boot/firmware/config.txt

# Check if pull-ups already configured
if ! grep -q "gpio=2,3=pu" /boot/firmware/config.txt; then
    echo "Adding I2C pull-up resistors..."
    # Add after the i2c_arm line
    sed -i '/dtparam=i2c_arm=on/a # Enable I2C pull-ups for better signal integrity\ngpio=2,3=pu' /boot/firmware/config.txt
fi

echo ""
echo "✅ Configuration updated!"
echo ""
echo "Current I2C settings:"
grep -E "i2c_arm|gpio=2,3" /boot/firmware/config.txt | grep -v "^#"
echo ""
echo "Current DHT22 settings:"
grep "dht22" /boot/firmware/config.txt | grep -v "^#"
echo ""
echo "⚠️  IMPORTANT: Reboot required!"
echo "   Run: sudo reboot"
echo ""
echo "After reboot, test with:"
echo "   python debug_sensors.py"