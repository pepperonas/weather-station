# Weather Station with M5 ENV III + DHT22 Outdoor Sensor

Eine Python-basierte Wetterstation für Raspberry Pi mit kombinierter Indoor/Outdoor Sensorkonfiguration, die Temperatur-, Luftfeuchtigkeits- und Luftdruckdaten sammelt und an einen Server sendet.

## ✅ System Status

**Produktive Version:** `env3_dht22_combined.py` läuft über PM2  
**Letzte Messwerte (28.08.2025 11:41 Uhr):**
- Indoor (ENV III): 20.8°C, 79.6% Luftfeuchtigkeit, 1013.2hPa ✅
- Outdoor (DHT22): 21.0°C, 58.0% Luftfeuchtigkeit ✅
- Datenübertragung: ✓ Data sent successfully ✅
- PM2 Service: Online und stabil ✅

## Features

- **Dual-Sensor Setup**: 
  - Indoor: M5 ENV III Module (SHT30 + QMP6988) - **Funktioniert** ✅
  - Outdoor: DHT22 Sensor für Außentemperaturen - **Funktioniert** ✅
- **I2C + GPIO Kommunikation**: Direkte Sensoransteuerung 
- **Automatisches Senden**: Kontinuierliche Datenübertragung mit Indoor/Outdoor Kennzeichnung
- **PM2 Process Management**: Zuverlässige Prozessverwaltung mit Autostart
- **Redundanz**: Fallback zwischen Sensoren bei Ausfällen
- **Strukturierte Daten**: Getrennte Indoor/Outdoor Werte für Server
- **Logging**: Strukturierte Logs für Monitoring mit automatischer Rotation

## Hardware-Setup

### Indoor Sensoren (M5 ENV III) ✅ Funktioniert
- **SHT30**: Temperatur- und Luftfeuchtigkeitssensor (I2C: 0x44)
- **QMP6988**: Luftdrucksensor (I2C: 0x70)
- **Anschluss**: I2C Bus 1 (GPIO2=SDA, GPIO3=SCL)

### Outdoor Sensor (DHT22) ✅ Funktioniert
- **DHT22**: Temperatur- und Luftfeuchtigkeitssensor für Außenbereich
- **Anschluss**: GPIO4 (Pin 7)
- **Stromversorgung**: 3.3V
- **Status**: Voll funktionsfähig mit verbesserter Zuverlässigkeit (Retry-Logik + Caching)

## Installation

### 1. Repository klonen und Abhängigkeiten installieren

```bash
git clone https://github.com/pepperonas/weather-station.git
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install smbus2 adafruit-blinka==8.64.0 adafruit-circuitpython-dht==4.0.9
```

**WICHTIG**: Verwende genau Blinka Version 8.64.0 - neuere Versionen verursachen Konflikte!

### 2. Hardware-Interfaces aktivieren

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

### 3. Boot-Konfiguration für DHT22

Füge folgende Zeile zu `/boot/firmware/config.txt` hinzu:
```
dtoverlay=dht22,gpiopin=4
```

### 4. Sensoren verkabeln

#### M5 ENV III (Indoor):
- VCC → Pin 1 (3.3V)
- GND → Pin 9 (GND)  
- SDA → Pin 3 (GPIO2)
- SCL → Pin 5 (GPIO3)

#### DHT22 (Outdoor):
```
DHT22 Pin 1 (VCC) → Raspberry Pi Pin 1 (3.3V)
DHT22 Pin 2 (DATA) → Raspberry Pi Pin 7 (GPIO4)
DHT22 Pin 3 (NC) → Nicht verbinden
DHT22 Pin 4 (GND) → Raspberry Pi Pin 9 (GND)
```

### 5. PM2 Service einrichten

```bash
# PM2 installieren (falls nicht vorhanden)
sudo npm install -g pm2

# Service starten
pm2 start ecosystem.config.js

# Autostart einrichten
pm2 startup
pm2 save
```

## Konfiguration

### Server-Konfiguration
Server URL in `env3_dht22_combined.py` anpassen:

```python
SERVER_URL = "https://your-server.com/weather-endpoint"
```

### GPIO-Konfiguration
Falls andere GPIO Pins verwendet werden sollen:

```python
DHT22_GPIO = 4  # Aktueller Pin für DHT22
```

## Datenformat

Das Script sendet folgende JSON-Struktur an den Server:

```json
{
  "indoor": {
    "temperature": 20.5,
    "humidity": 79.9,
    "pressure": 1013.2
  },
  "outdoor": {
    "temperature": 27.5,
    "humidity": 63.3
  }
}
```

## Verwendung

### Manueller Start
```bash
cd /home/pi/apps/weather-station
/home/pi/apps/weather-station/venv/bin/python env3_dht22_combined.py
```

### PM2 Management
```bash
# Status prüfen
pm2 status weather-station

# Live-Logs anzeigen
pm2 logs weather-station --lines 50

# Service neu starten
pm2 restart weather-station

# Service stoppen
pm2 stop weather-station
```

## Monitoring

### Aktuelle Live-Ausgabe
```
Indoor(ENV3): 20.8°C, 79.6% | Pressure: 1013.2hPa | Outdoor(DHT22): 21.0°C, 58.0%
✓ Data sent successfully
```

### Sensor Tests

#### ENV III Test
```bash
python3 -c "
import smbus2, time
bus = smbus2.SMBus(1)
msg = smbus2.i2c_msg.write(0x44, [0x2C, 0x06])
bus.i2c_rdwr(msg)
time.sleep(0.02)
msg = smbus2.i2c_msg.read(0x44, 6)
bus.i2c_rdwr(msg)
data = list(msg)
temp = -45 + 175 * ((data[0] << 8) | data[1]) / 65535.0
hum = 100 * ((data[3] << 8) | data[4]) / 65535.0
print(f'ENV III: {temp:.1f}°C, {hum:.1f}%')
"
```

#### DHT22 Test
```bash
/home/pi/apps/weather-station/venv/bin/python -c "
import board, adafruit_dht, time
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)
print(f'DHT22: {dht.temperature:.1f}°C, {dht.humidity:.1f}%')
dht.exit()
"
```

## Troubleshooting

### DHT22 "Sensor not found"
1. **Verkabelung prüfen**: Alle 4 Pins korrekt verbunden?
2. **Boot-Config prüfen**: `dtoverlay=dht22,gpiopin=4` in `/boot/firmware/config.txt`?
3. **Virtual Environment nutzen**: Immer venv Python verwenden, nicht System-Python!
4. **Neustart**: Nach Config-Änderungen `sudo reboot`
5. **Timing-Probleme**: Der verbesserte Code enthält nun Retry-Logik und 30s Caching

### ENV III Probleme
```bash
# I2C Geräte scannen
sudo i2cdetect -y 1
# Erwartete Adressen:
# 0x44 = SHT30 (Temp/Humidity)
# 0x70 = QMP6988 (Pressure)
```

### Service Probleme
```bash
# PM2 Prozess Details
pm2 show weather-station

# Fehler-Logs
pm2 logs weather-station --err --lines 50

# PM2 neu starten
pm2 kill && pm2 resurrect
```

### Library-Konflikte
```bash
# System-Libraries entfernen (falls Konflikte)
sudo pip3 uninstall adafruit-blinka adafruit-circuitpython-dht --break-system-packages

# Nur venv verwenden
/home/pi/apps/weather-station/venv/bin/pip list | grep -i adafruit
```

## Projektstruktur

```
weather-station/
├── env3_dht22_combined.py    # ✅ Hauptscript (Indoor + Outdoor)
├── ecosystem.config.js       # ✅ PM2 Konfiguration  
├── requirements.txt          # Python Abhängigkeiten
├── CLAUDE.md                 # Dokumentation für Claude AI
├── README.md                 # Diese Dokumentation
├── logs/                     # PM2 Log-Dateien
├── venv/                     # Python Virtual Environment (kritisch!)
└── archive/                  # Archivierte Entwicklungsdateien
```

## Entwicklungsverlauf

### Phase 1: ENV III Integration ✅
- M5 ENV III Modul erfolgreich integriert
- I2C Kommunikation etabliert
- Kontinuierliche Datenübertragung

### Phase 2: DHT22 Integration ✅
- DHT22 Hardware erfolgreich angeschlossen
- GPIO4 Konfiguration mit Device Tree Overlay
- Kombiniertes Script mit Subprocess-Methode
- Verbesserte Zuverlässigkeit: Retry-Logik, längere Delays, 30s Cache
- **Status**: Voll funktionsfähig mit ~100% Erfolgsrate

### Phase 3: Projektorganisation ✅
- Saubere Projektstruktur etabliert
- PM2 Process Management
- Vollständige Dokumentation
- GitHub Repository gepflegt

## Wichtige Hinweise

### Virtual Environment ist kritisch!
Das System funktioniert NUR mit dem Virtual Environment unter `/home/pi/apps/weather-station/venv/`. System-Python wird NICHT funktionieren!

### Device Tree Overlay
Die Zeile `dtoverlay=dht22,gpiopin=4` in `/boot/firmware/config.txt` ist ESSENTIELL für DHT22. Nicht entfernen!

### Library-Versionen
- Blinka: 8.64.0 (NICHT upgraden auf 8.65.0!)
- adafruit-circuitpython-dht: 4.0.9

## Backup

Vor größeren Änderungen:
```bash
tar -czf weather-station-backup-$(date +%Y%m%d-%H%M%S).tar.gz .
```

## System-Status: ✅ VOLL FUNKTIONSFÄHIG

Das System läuft stabil mit:
- ENV III Indoor-Sensoren (Temperatur, Luftfeuchtigkeit, Luftdruck)
- DHT22 Outdoor-Sensor (Temperatur, Luftfeuchtigkeit)
- Kontinuierliche Datenübertragung an Server
- PM2 Process Management mit Auto-Restart

Letzte erfolgreiche Messung: 28.08.2025 11:41 Uhr

### Letzte Verbesserung (28.08.2025)
- DHT22 Timing-Probleme behoben
- Retry-Logik mit 3 Versuchen implementiert
- 30-Sekunden Cache für DHT22-Werte hinzugefügt
- Sensor-Delays von 2s auf 2.5s erhöht
- Erfolgsrate von ~50% auf ~100% verbessert