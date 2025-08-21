# Weather Station DHT22

Eine Python-basierte Wetterstation für Raspberry Pi mit DHT22 Sensor, die Temperatur- und Luftfeuchtigkeitsdaten sammelt und an einen Server sendet.

## Features

- **DHT22 Sensor Support**: Liest Temperatur und Luftfeuchtigkeit
- **Automatisches Senden**: Kontinuierliche Datenübertragung an Remote-Server
- **PM2 Process Management**: Zuverlässige Prozessverwaltung mit Autostart
- **Konfigurierbar**: Umgebungsvariablen für einfache Anpassung
- **Logging**: Strukturierte Logs für Monitoring

## Hardware-Anforderungen

- Raspberry Pi (alle Modelle)
- DHT22 Temperatur-/Luftfeuchtigkeitssensor
- Verbindungskabel (Standard GPIO Pin 18)

## Installation

### 1. Repository klonen und Abhängigkeiten installieren

```bash
git clone https://github.com/pepperonas/weather-station.git
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Konfiguration anpassen

Bearbeite die `.env` Datei oder nutze die Standard-Werte in `config.py`:

```bash
# .env Datei
WEATHER_SERVER_URL=https://mrx3k1.de/weather-tracker/weather-tracker
WEATHER_GPIO_PIN=18
WEATHER_REQUEST_TIMEOUT=10
```

### 3. PM2 Installation (falls nicht vorhanden)

```bash
npm install -g pm2
```

### 4. Anwendung starten

```bash
pm2 start ecosystem.config.js
pm2 save
```

### 5. Autostart einrichten

Der PM2 Autostart ist bereits als systemd Service konfiguriert:

```bash
sudo systemctl enable pm2-pi
sudo systemctl start pm2-pi
```

Die Anwendung startet automatisch nach jedem Reboot.

## Verwendung

### Verfügbare Skripte

- **`dht_22.py`**: Einfache Sensorabfrage mit Ausgabe
- **`dht_22_sender.py`**: Einmalige Messung und Übertragung
- **`continuous_sender.py`**: Kontinuierliche Überwachung (Standard für PM2)

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

# Einzelne Messung
python dht_22_sender.py

# Kontinuierliche Überwachung
python continuous_sender.py
```

## Konfiguration

### config.py

```python
# DHT22 Sensor Configuration
SENSOR_TYPE = "DHT22"
GPIO_PIN = 18

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
- `WEATHER_GPIO_PIN`: GPIO-Pin für DHT22 Sensor
- `WEATHER_REQUEST_TIMEOUT`: HTTP-Timeout in Sekunden

## Datenformat

Die Anwendung sendet JSON-Daten im folgenden Format:

```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "timestamp": 1642694400
}
```

## Logs

Logs werden in folgende Dateien geschrieben:

- `logs/weather-station-out.log`: Standard-Ausgabe
- `logs/weather-station-error.log`: Fehler-Ausgabe
- `logs/weather-station-combined.log`: Kombinierte Logs

## Fehlerbehandlung

Die Anwendung behandelt folgende Fehlerszenarien:

- **Sensor-Lesefehler**: Retry-Mechanismus mit Fehlermeldung
- **Netzwerkfehler**: Timeout-Behandlung und Fehlerprotokollierung
- **Server-Fehler**: HTTP-Statuscodes werden geloggt

## Systemanforderungen

- Python 3.7+
- Raspberry Pi OS (oder kompatible Linux-Distribution)
- GPIO-Zugriff (User muss in `gpio` Gruppe sein)
- Internetverbindung für Datenübertragung
- Node.js und npm für PM2

## Abhängigkeiten

- `adafruit-circuitpython-dht`: Moderne DHT-Sensor-Bibliothek
- `requests`: HTTP-Client für Datenübertragung
- `RPi.GPIO`: GPIO-Zugriff für Raspberry Pi

## Autostart-Architektur

Die Anwendung verwendet eine zweistufige Autostart-Architektur:

1. **systemd Service** (`pm2-pi.service`): Startet PM2 als systemd Service
2. **PM2 Process Manager**: Verwaltet die Weather Station Anwendung

Diese Architektur gewährleistet:
- Zuverlässiger Neustart nach Systemcrash
- Prozess-Monitoring und automatische Wiederherstellung
- Strukturierte Logs über systemd und PM2
- Einfache Verwaltung über PM2 Befehle

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