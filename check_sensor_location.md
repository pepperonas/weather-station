# Sensor-Standort Überprüfung

## Aktuelle Messwerte:
- **ENV III (I2C)**: 22-23°C, ~71% Luftfeuchtigkeit
- **DHT22 (GPIO4)**: Nicht erkannt / defekt

## Frage zur Überprüfung:
1. **Wo ist der ENV III physisch montiert?**
   - [ ] Im Wohnzimmer (Indoor)
   - [ ] Draußen (Outdoor)

2. **Wo ist der DHT22 physisch montiert?**
   - [ ] Im Wohnzimmer (Indoor)  
   - [ ] Draußen (Outdoor)

## Hinweise:
- 22-23°C und 71% Luftfeuchtigkeit sind typische Werte für Innenräume
- Falls der ENV III draußen ist und es dort aktuell 22-23°C hat, wäre das plausibel
- Der DHT22 scheint ein Hardware-Problem zu haben (Kabel prüfen oder Sensor ersetzen)

## Nächste Schritte:
1. DHT22 Verkabelung prüfen:
   - Pin 1 (links): 3.3V Power
   - Pin 2: Daten → GPIO4 (Pin 7)
   - Pin 3: Nicht verbunden
   - Pin 4 (rechts): Ground
   
2. Falls DHT22 weiterhin nicht funktioniert:
   - Kabel auf Bruch prüfen
   - Anderen GPIO Pin testen
   - Sensor austauschen