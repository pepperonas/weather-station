#!/bin/bash
# Script to fix I2C baudrate for ENV III sensor compatibility

echo "Fixing I2C baudrate from 100kHz to 10kHz for ENV III sensor..."
echo "This requires sudo privileges."

# Backup current config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup

# Fix the baudrate
sudo sed -i 's/i2c_arm_baudrate=100000/i2c_arm_baudrate=10000/' /boot/firmware/config.txt

echo "I2C baudrate changed. Please reboot for changes to take effect."
echo "Run: sudo reboot"