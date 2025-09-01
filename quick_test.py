#!/usr/bin/env python3

import time

def test_env3():
    """Test ENV III sensors"""
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        
        # Test SHT30 - just try to communicate
        msg = smbus2.i2c_msg.write(0x44, [0x2C, 0x06])
        bus.i2c_rdwr(msg)
        time.sleep(0.02)
        
        msg = smbus2.i2c_msg.read(0x44, 6)
        bus.i2c_rdwr(msg)
        data = list(msg)
        
        # Simple conversion
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45 + 175 * temp_raw / 65535.0
        
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535.0
        
        print(f"✅ ENV III: {temperature:.1f}°C, {humidity:.1f}%")
        return True
        
    except Exception as e:
        print(f"❌ ENV III error: {e}")
        return False

def test_dht22():
    """Test DHT22 sensor"""
    try:
        import board
        import adafruit_dht
        
        dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        
        print("Testing DHT22...")
        temp = dht.temperature
        humidity = dht.humidity
        
        if temp is not None and humidity is not None:
            print(f"✅ DHT22: {temp:.1f}°C, {humidity:.1f}%")
            return True
        else:
            print("❌ DHT22: No data returned")
            return False
            
    except RuntimeError as e:
        if "DHT sensor not found" in str(e):
            print("❌ DHT22: Sensor not found - checking hardware connection")
        else:
            print(f"❌ DHT22: {e}")
        return False
    except Exception as e:
        print(f"❌ DHT22 error: {e}")
        return False

if __name__ == "__main__":
    print("=== Quick Sensor Test ===\n")
    
    env3_ok = test_env3()
    dht22_ok = test_dht22()
    
    print(f"\n=== Results ===")
    print(f"ENV III (Indoor): {'✅' if env3_ok else '❌'}")
    print(f"DHT22 (Outdoor):  {'✅' if dht22_ok else '❌'}")
    
    if env3_ok and not dht22_ok:
        print("\n💡 ENV III is working but DHT22 has issues.")
        print("   This suggests a DHT22 hardware or connection problem.")
    elif not env3_ok and dht22_ok:
        print("\n💡 DHT22 is working but ENV III has issues.")
        print("   This suggests an ENV III or I2C problem.")
    elif env3_ok and dht22_ok:
        print("\n🎉 Both sensors are working!")
    else:
        print("\n⚠️  Both sensors have issues - check connections.")
