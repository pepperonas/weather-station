# Weather Station with M5 ENV III + DHT22 Outdoor Sensor

Eine Python-basierte Wetterstation für Raspberry Pi mit kombinierter Indoor/Outdoor Sensorkonfiguration, die Temperatur-, Luftfeuchtigkeits- und Luftdruckdaten sammelt und an einen Server sendet.

## ✅ System Status

**Produktive Version:** `env3_dht22_combined.py` läuft über PM2  
**Letzte Messwerte:**
- Indoor (ENV III): 22.3°C, 62.4% Luftfeuchtigkeit, 1013.2hPa ✅
- Datenübertragung: ✓ Data sent successfully ✅
- PM2 Service: Online und stabil ✅

## Features

- **Dual-Sensor Setup**: 
  - Indoor: M5 ENV III Module (SHT30 + QMP6988) - **Funktioniert** ✅
  - Outdoor: DHT22 Sensor für Außentemperaturen - **Implementiert** ⚙️
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

### Outdoor Sensor (DHT22) ⚙️ Konfiguriert
- **DHT22**: Temperatur- und Luftfeuchtigkeitssensor für Außenbereich
- **Anschluss**: GPIO4 (Pin 7)
- **Stromversorgung**: 3.3V
- **Status**: Hardware-Tests erfolgreich, Integration in Hauptscript abgeschlossen

## Installation

### 1. Repository klonen und Abhängigkeiten installieren

```bash
git clone <repository-url>
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Hardware-Interfaces aktivieren

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

### 3. Sensoren verkabeln

#### M5 ENV III (Indoor):
- VCC → 3.3V
- GND → GND  
- SDA → GPIO2 (Pin 3)
- SCL → GPIO3 (Pin 5)

#### DHT22 (Outdoor):
- VCC → 3.3V
- GND → GND
- DATA → GPIO4 (Pin 7)

### 4. PM2 Service einrichten

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
Server URL in env3_dht22_combined.py anpassen:

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
  "timestamp": 1756312620,
  "temperature": 22.3,           // Primary (Indoor für Kompatibilität)
  "humidity": 62.4,              // Primary (Indoor für Kompatibilität)
  "temperature_indoor": 22.3,    // ENV III Indoor
  "humidity_indoor": 62.4,       // ENV III Indoor  
  "temperature_outdoor": 21.9,   // DHT22 Outdoor (wenn verfügbar)
  "humidity_outdoor": 33.2,      // DHT22 Outdoor (wenn verfügbar)
  "pressure": 1013.2,           // Indoor Luftdruck
  "pressure_indoor": 1013.2,    // Indoor Luftdruck
  "sensor_indoor": "ENV3",
  "sensor_outdoor": "DHT22"
}
```

## Verwendung

### Manueller Start
```bash
source venv/bin/activate
python env3_dht22_combined.py
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
Indoor(ENV3): 22.3°C, 62.4% | Pressure: 1013.2hPa
✓ Data sent successfully
```

### DHT22 Einzeltest
```bash
# DHT22 manuell testen
python -c "
import board
import adafruit_dht
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
print(fTemp: {dht.temperature}°C, Humidity: {dht.humidity}%)
dht.exit()
"
```

## Troubleshooting

### DHT22 Integration
Falls DHT22 nicht in den Logs erscheint:

```bash
# 1. DHT22 einzeln testen
cd /home/pi/apps/weather-station
source venv/bin/activate
python archive/test_dht22_gpio4.py

# 2. GPIO-Konflikte prüfen
sudo fuser /dev/gpiochip0

# 3. PM2 Service neu starten
pm2 restart weather-station
```

### I2C Probleme
```bash
# I2C Geräte scannen
sudo i2cdetect -y 1

# Erwartete Adressen:
# 0x44 = SHT30 (Temp/Humidity) ✅
# 0x70 = QMP6988 (Pressure) ✅
```

### Service Probleme
```bash
# PM2 Prozess Details
pm2 show weather-station

# Fehler-Logs
pm2 logs weather-station --err --lines 50
```

## Projektstruktur

```
weather-station/
├── env3_dht22_combined.py    # ✅ Hauptscript (Indoor + Outdoor)
├── ecosystem.config.js       # ✅ PM2 Konfiguration  
├── requirements.txt          # Python Abhängigkeiten
├── config.py                 # Legacy Konfiguration
├── dht_22.py                 # Standalone DHT22 Test
├── env3_final.py             # Legacy ENV III Script (Backup)
├── weather-station.service   # Systemd Service (optional)
├── README.md                 # Diese Dokumentation
├── logs/                     # PM2 Log-Dateien
├── venv/                     # Python Virtual Environment
└── archive/                  # Archivierte Entwicklungsdateien
    ├── test_dht22_gpio4.py   # ✅ Erfolgreiche DHT22 Tests
    ├── env3_indoor_working.py # ✅ ENV III Arbeitsversion
    └── [weitere Test-Dateien]
```

## Entwicklungsverlauf

### Phase 1: ENV III Integration ✅
- M5 ENV III Modul erfolgreich integriert
- I2C Kommunikation etabliert
- Kontinuierliche Datenübertragung

### Phase 2: DHT22 Integration ⚙️
- DHT22 Hardware-Tests erfolgreich
- GPIO4 Konfiguration abgeschlossen  
- Kombiniertes Script erstellt
- **Status**: Technisch funktionsfähig, finale Integration in Arbeit

### Phase 3: Projektorganisation ✅
- 27+ Entwicklungsdateien archiviert
- Saubere Projektstruktur etabliert
- Vollständige Dokumentation

## Backup

Vor größeren Änderungen:

```bash
tar -czf weather-station-backup-$(date +%Y%m%d-%H%M%S).tar.gz .
```

## Hardware-Tipps

### DHT22 Installation
- Wetterfesten Gehäuse für Außensensor verwenden
- Kurze Kabelwege für stabilere Verbindung
- 10kΩ Pull-up Resistor zwischen DATA und VCC (empfohlen)

### ENV III Installation  
- Innenraum-Montage für präzise Messungen
- Ausreichend Luftzirkulation um Sensor
- Nicht direkt neben Wärmequellen platzieren

## Support

Bei Problemen:
1. **Logs prüfen:** `pm2 logs weather-station`
2. **Hardware-Verbindungen kontrollieren**
3. **Sensor-Tests einzeln durchführen** (siehe archive/ für Test-Scripts)
4. **PM2 Service neu starten:** `pm2 restart weather-station`

## System-Status: ✅ PRODUKTIV

Das System läuft stabil mit ENV III Indoor-Sensoren und sendet erfolgreich Daten an den Server. DHT22 Outdoor-Integration ist vorbereitet und getestet.
