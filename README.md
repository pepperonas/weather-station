# Weather Station M5 Cardputer

Eine Python-basierte Wetterstation für Raspberry Pi mit M5 Cardputer Sensoren, die Temperatur-, Luftfeuchtigkeits- und Luftdruckdaten sammelt und an einen Server sendet.

## Features

- **M5 Cardputer Sensor Support**: SHT30 (Temperatur/Luftfeuchtigkeit) und QMP6988 (Luftdruck)
- **I2C Kommunikation**: Direkte Sensoransteuerung über I2C Bus
- **Automatisches Senden**: Kontinuierliche Datenübertragung an Remote-Server
- **PM2 Process Management**: Zuverlässige Prozessverwaltung mit Autostart
- **Konfigurierbar**: Umgebungsvariablen für einfache Anpassung
- **Logging**: Strukturierte Logs für Monitoring
- **Druck-Messung**: Zusätzliche Luftdruckdaten (optional)

## Hardware-Anforderungen

- Raspberry Pi (alle Modelle mit I2C Support)
- M5 Cardputer oder M5 Module mit folgenden Sensoren:
  - **SHT30**: Temperatur- und Luftfeuchtigkeitssensor (I2C: 0x44)
  - **QMP6988**: Luftdrucksensor (I2C: 0x70) - optional
- I2C Verbindung (Standard GPIO Pins: SDA=2, SCL=3)

## Installation

### 1. Repository klonen und Abhängigkeiten installieren

```bash
git clone https://github.com/pepperonas/weather-station.git
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. I2C aktivieren

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

### 3. Konfiguration anpassen

Bearbeite die `.env` Datei oder nutze die Standard-Werte in `config.py`:

```bash
# .env Datei
WEATHER_SERVER_URL=https://mrx3k1.de/weather-tracker/weather-tracker
WEATHER_REQUEST_TIMEOUT=10
```

### 4. PM2 Installation (falls nicht vorhanden)

```bash
npm install -g pm2
```

### 5. Anwendung starten

```bash
pm2 start ecosystem.config.js
pm2 save
```

### 6. Autostart einrichten

Der PM2 Autostart ist bereits als systemd Service konfiguriert:

```bash
sudo systemctl enable pm2-pi
sudo systemctl start pm2-pi
```

Die Anwendung startet automatisch nach jedem Reboot.

## Verwendung

### Verfügbare Skripte

#### M5 Cardputer Sensoren:
- **`m5_env_sender.py`**: Einmalige Messung von SHT30 + QMP6988 und Übertragung
- **`m5_continuous_sender.py`**: Kontinuierliche Überwachung (Standard für PM2)
- **`m5_sensor_sender.py`**: Alternative Sensor-Implementierung
- **`m5_sensor_test.py`**: Test-Skript für Sensor-Diagnostik

#### Legacy DHT22 Support:
- **`dht_22.py`**: Einfache DHT22 Sensorabfrage mit Ausgabe
- **`dht_22_sender.py`**: Einmalige DHT22 Messung und Übertragung
- **`continuous_sender.py`**: Kontinuierliche DHT22 Überwachung

### PM2 Befehle

```bash
# Status anzeigen
pm2 status

# Logs anzeigen
pm2 logs weather-station

# Neustart
pm2 restart weather-station

# Stoppen
pm2 stop weather-station

# Entfernen
pm2 delete weather-station

# Konfiguration speichern
pm2 save
```

### Systemd Service Verwaltung

```bash
# PM2 Service Status prüfen
sudo systemctl status pm2-pi

# PM2 Service neustarten
sudo systemctl restart pm2-pi

# PM2 Service Logs
journalctl -u pm2-pi -f
```

### Manuelle Tests

```bash
# Aktiviere Virtual Environment
source venv/bin/activate

# M5 Cardputer Einzelmessung
python m5_env_sender.py

# M5 Cardputer kontinuierlich
python m5_continuous_sender.py

# Sensor-Test
python m5_sensor_test.py
```

## Sensoren

### SHT30 Temperatur/Luftfeuchtigkeitssensor
- **I2C Adresse**: 0x44
- **Messbereich Temperatur**: -40°C bis +125°C
- **Messbereich Luftfeuchtigkeit**: 0% bis 100% RH
- **Genauigkeit**: ±0.2°C / ±2% RH

### QMP6988 Luftdrucksensor
- **I2C Adresse**: 0x70
- **Messbereich**: 300-1100 hPa
- **Genauigkeit**: ±1 hPa (optional, falls verfügbar)

## Konfiguration

### config.py

```python
# M5 Sensor Configuration
SENSOR_TYPE = "M5_CARDPUTER"
I2C_SHT30_ADDRESS = 0x44
I2C_QMP6988_ADDRESS = 0x70

# Server Configuration
SERVER_URL = "https://mrx3k1.de/weather-tracker/weather-tracker"
REQUEST_TIMEOUT = 10

# Timing Configuration
SENSOR_READ_INTERVAL = 2.0  # seconds
CONTINUOUS_MODE_INTERVAL = 60.0  # seconds for continuous monitoring
```

### Umgebungsvariablen

Die Anwendung unterstützt folgende Umgebungsvariablen:

- `WEATHER_SERVER_URL`: URL des Zielservers
- `WEATHER_REQUEST_TIMEOUT`: HTTP-Timeout in Sekunden

## Datenformat

Die Anwendung sendet JSON-Daten im folgenden Format:

```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "pressure": 1013.25,
  "timestamp": 1642694400
}
```

**Hinweis**: Das `pressure` Feld wird nur gesendet, wenn der QMP6988 Sensor verfügbar ist.

## I2C Troubleshooting

### I2C Geräte scannen
```bash
sudo i2cdetect -y 1
```

Erwartete Ausgabe:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- 44 -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 -- -- -- -- -- -- --
```

### I2C Berechtigungen
```bash
sudo usermod -a -G i2c pi
```

## Logs

Logs werden in folgende Dateien geschrieben:

- `logs/weather-station-out.log`: Standard-Ausgabe
- `logs/weather-station-error.log`: Fehler-Ausgabe
- `logs/weather-station-combined.log`: Kombinierte Logs

## Fehlerbehandlung

Die Anwendung behandelt folgende Fehlerszenarien:

- **I2C-Sensor-Fehler**: Retry-Mechanismus mit detaillierter Fehlermeldung
- **Netzwerkfehler**: Timeout-Behandlung und Fehlerprotokollierung
- **Server-Fehler**: HTTP-Statuscodes werden geloggt
- **Sensor-Ausfall**: Graceful degradation (weiterarbeiten ohne defekte Sensoren)

## Systemanforderungen

- Python 3.7+
- Raspberry Pi OS (oder kompatible Linux-Distribution)
- I2C aktiviert (`sudo raspi-config`)
- Internetverbindung für Datenübertragung
- Node.js und npm für PM2

## Abhängigkeiten

- `adafruit-circuitpython-busio`: I2C Kommunikation
- `adafruit-blinka`: CircuitPython Kompatibilitätslayer
- `requests`: HTTP-Client für Datenübertragung
- `RPi.GPIO`: GPIO-Zugriff für Raspberry Pi (Legacy DHT22 Support)

## Autostart-Architektur

Die Anwendung verwendet eine zweistufige Autostart-Architektur:

1. **systemd Service** (`pm2-pi.service`): Startet PM2 als systemd Service
2. **PM2 Process Manager**: Verwaltet die Weather Station Anwendung

Diese Architektur gewährleistet:
- Zuverlässiger Neustart nach Systemcrash
- Prozess-Monitoring und automatische Wiederherstellung
- Strukturierte Logs über systemd und PM2
- Einfache Verwaltung über PM2 Befehle

## Migration von DHT22

Falls du von DHT22 auf M5 Cardputer migrierst:

1. **Hardware ersetzen**: M5 Cardputer an I2C anschließen
2. **PM2 Konfiguration ändern**: `ecosystem.config.js` auf M5-Skripte umstellen
3. **Testen**: `python m5_env_sender.py` ausführen

## Autor

**Martin Pfeffer** - [pepperonas](https://github.com/pepperonas)

## Lizenz

MIT License

Copyright (c) 2025 Martin Pfeffer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.