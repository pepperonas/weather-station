"""
Unit tests for pure weather-station logic.

All hardware-touching imports (smbus2, board, adafruit_dht, RPi.GPIO, requests)
are stubbed out via sys.modules so these tests run on any machine — no Pi, no
sensors, no network required.
"""

import sys
import types
import math

# ---------------------------------------------------------------------------
# Stub out hardware / network modules before any project code is imported
# ---------------------------------------------------------------------------

def _make_stub(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod

for _mod_name in (
    "smbus2", "board", "adafruit_dht",
    "RPi", "RPi.GPIO", "requests",
):
    if _mod_name not in sys.modules:
        _make_stub(_mod_name)

# smbus2 needs SMBus and i2c_msg attributes
smbus2_stub = sys.modules["smbus2"]
smbus2_stub.SMBus = type("SMBus", (), {"__init__": lambda self, *a, **kw: None})
smbus2_stub.i2c_msg = type("i2c_msg", (), {
    "write": staticmethod(lambda *a, **kw: None),
    "read": staticmethod(lambda *a, **kw: None),
})

# requests needs a post stub
requests_stub = sys.modules["requests"]
requests_stub.post = lambda *a, **kw: None

# RPi.GPIO sub-module
rpigpio = _make_stub("RPi.GPIO")
sys.modules["RPi"].GPIO = rpigpio

# ---------------------------------------------------------------------------
# Pure helper implementations (extracted inline so tests don't import
# hardware-initialising module-level code from env3_dht22_combined.py)
# ---------------------------------------------------------------------------

def crc8(data: list) -> int:
    """CRC-8 / MAXIM — same algorithm used by SHT30 sensor."""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc = crc << 1
    return crc & 0xFF


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def hpa_to_inhg(hpa: float) -> float:
    return hpa * 0.02953


def inhg_to_hpa(inhg: float) -> float:
    return inhg / 0.02953


def ms_to_kmh(ms: float) -> float:
    return ms * 3.6


def kmh_to_ms(kmh: float) -> float:
    return kmh / 3.6


def dew_point(temp_c: float, humidity_rh: float) -> float:
    """Magnus formula dew point (°C)."""
    a, b = 17.27, 237.7
    gamma = (a * temp_c / (b + temp_c)) + math.log(humidity_rh / 100.0)
    return b * gamma / (a - gamma)


def heat_index(temp_c: float, humidity_rh: float) -> float:
    """Steadman heat index (°C). Valid for T ≥ 27°C and RH ≥ 40%."""
    T = celsius_to_fahrenheit(temp_c)
    R = humidity_rh
    HI = (
        -42.379
        + 2.04901523 * T
        + 10.14333127 * R
        - 0.22475541 * T * R
        - 0.00683783 * T * T
        - 0.05481717 * R * R
        + 0.00122874 * T * T * R
        + 0.00085282 * T * R * R
        - 0.00000199 * T * T * R * R
    )
    return fahrenheit_to_celsius(HI)


def wind_chill(temp_c: float, wind_kmh: float) -> float:
    """Environment Canada / NWS wind-chill index (°C). Valid T ≤ 10°C, v ≥ 4.8 km/h."""
    return (
        13.12
        + 0.6215 * temp_c
        - 11.37 * wind_kmh ** 0.16
        + 0.3965 * temp_c * wind_kmh ** 0.16
    )


def degrees_to_compass(degrees: float) -> str:
    """Convert wind direction in degrees to 16-point compass label."""
    dirs = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    idx = int((degrees % 360 + 11.25) / 22.5) % 16
    return dirs[idx]


def sht30_raw_to_celsius(raw: int) -> float:
    """Convert a raw 16-bit SHT30 temperature register value to °C."""
    return -45 + 175 * raw / 65535.0


def sht30_raw_to_humidity(raw: int) -> float:
    """Convert a raw 16-bit SHT30 humidity register value to %RH."""
    return 100 * raw / 65535.0


def round_sensor(value: float, decimals: int = 1) -> float:
    return round(value, decimals)


def sanity_check_temp(temp_c: float) -> bool:
    """Plausible indoor/outdoor temperature (-40 … 85 °C)."""
    return -40 <= temp_c <= 85


def sanity_check_humidity(rh: float) -> bool:
    return 0 <= rh <= 100


def build_payload(indoor_temp, indoor_humidity, pressure,
                  outdoor_temp, outdoor_humidity) -> dict:
    """
    Assemble the dict that would be POSTed to the server.
    Pure function — mirrors the logic in env3_dht22_combined.py::send_data().
    """
    import time as _time
    data: dict = {}

    if indoor_temp is not None and indoor_humidity is not None:
        data["temperature"] = round_sensor(indoor_temp)
        data["humidity"] = round_sensor(indoor_humidity)
        data["temperature_indoor"] = round_sensor(indoor_temp)
        data["humidity_indoor"] = round_sensor(indoor_humidity)
        data["sensor_indoor"] = "ENV3"

    if outdoor_temp is not None and outdoor_humidity is not None:
        data["temperature_outdoor"] = round_sensor(outdoor_temp)
        data["humidity_outdoor"] = round_sensor(outdoor_humidity)
        data["sensor_outdoor"] = "DHT22"
        if "temperature" not in data:
            data["temperature"] = round_sensor(outdoor_temp)
            data["humidity"] = round_sensor(outdoor_humidity)

    if pressure is not None:
        data["pressure"] = round_sensor(pressure)
        data["pressure_indoor"] = round_sensor(pressure)

    return data


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCrc8:
    def test_known_zero_byte(self):
        # CRC8 of [0x00] with init 0xFF and poly 0x31 = 0xAC
        assert crc8([0x00]) == 0xAC

    def test_empty_returns_ff(self):
        assert crc8([]) == 0xFF

    def test_sht30_example(self):
        # SHT30 datasheet example: [0xBE, 0xEF] → CRC = 0x92
        assert crc8([0xBE, 0xEF]) == 0x92

    def test_consistency(self):
        data = [0x12, 0x34, 0x56]
        assert crc8(data) == crc8(data)


class TestTemperatureConversions:
    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_boiling_point(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_body_temp(self):
        assert abs(celsius_to_fahrenheit(37) - 98.6) < 0.05

    def test_negative_celsius(self):
        assert celsius_to_fahrenheit(-40) == -40.0  # identity point

    def test_roundtrip(self):
        original = 23.5
        assert abs(fahrenheit_to_celsius(celsius_to_fahrenheit(original)) - original) < 1e-9

    def test_fahrenheit_to_celsius_freezing(self):
        assert fahrenheit_to_celsius(32) == 0.0

    def test_fahrenheit_to_celsius_boiling(self):
        assert fahrenheit_to_celsius(212) == 100.0


class TestPressureConversions:
    def test_standard_atmosphere(self):
        # 1013.25 hPa ≈ 29.92 inHg
        result = hpa_to_inhg(1013.25)
        assert abs(result - 29.921) < 0.01

    def test_inhg_to_hpa_roundtrip(self):
        original = 1013.25
        assert abs(inhg_to_hpa(hpa_to_inhg(original)) - original) < 0.01

    def test_low_pressure(self):
        # 980 hPa → ~28.94 inHg
        assert abs(hpa_to_inhg(980) - 28.94) < 0.05


class TestWindSpeedConversions:
    def test_zero_wind(self):
        assert ms_to_kmh(0) == 0.0

    def test_ten_ms(self):
        assert abs(ms_to_kmh(10) - 36.0) < 1e-9

    def test_roundtrip(self):
        original = 7.5
        assert abs(kmh_to_ms(ms_to_kmh(original)) - original) < 1e-9

    def test_gale_force(self):
        # Beaufort 8 = 17.2–20.7 m/s ≈ 62–74.5 km/h
        kmh = ms_to_kmh(18.0)
        assert 64 < kmh < 65.5


class TestDewPoint:
    def test_saturated_air(self):
        # At 100% RH dew point equals air temperature
        temp = 20.0
        assert abs(dew_point(temp, 100.0) - temp) < 0.1

    def test_dry_air(self):
        # At low humidity dew point is well below air temp
        assert dew_point(20, 30) < 5

    def test_typical_indoor(self):
        # 22 °C / 50% RH → dew point ≈ 11.1 °C
        dp = dew_point(22, 50)
        assert 10 < dp < 12.5

    def test_cold_outside(self):
        # −5 °C / 70% RH → dew point < −5 °C
        assert dew_point(-5, 70) < -5


class TestHeatIndex:
    def test_hot_humid(self):
        # 35 °C / 70% RH → feels much hotter
        hi = heat_index(35, 70)
        assert hi > 40

    def test_very_high_humidity(self):
        # 38 °C / 90% RH → extreme heat index
        hi = heat_index(38, 90)
        assert hi > 50

    def test_same_temp_diff_humidity(self):
        # Higher humidity → higher perceived temperature
        assert heat_index(34, 80) > heat_index(34, 50)


class TestWindChill:
    def test_calm_no_effect(self):
        # Very low wind → close to actual temperature
        wc = wind_chill(0, 5)
        assert wc < 0

    def test_strong_wind_colder(self):
        # 0 °C at 50 km/h should feel colder than actual temperature
        wc = wind_chill(0, 50)
        assert wc < 0          # definitely feels sub-zero
        assert wc < -7         # noticeably colder (formula gives ~-8.1 °C)

    def test_lower_temp_lower_chill(self):
        assert wind_chill(-15, 30) < wind_chill(-5, 30)


class TestCompassDirection:
    def test_north(self):
        assert degrees_to_compass(0) == "N"
        assert degrees_to_compass(360) == "N"

    def test_east(self):
        assert degrees_to_compass(90) == "E"

    def test_south(self):
        assert degrees_to_compass(180) == "S"

    def test_west(self):
        assert degrees_to_compass(270) == "W"

    def test_northeast(self):
        assert degrees_to_compass(45) == "NE"

    def test_southwest(self):
        assert degrees_to_compass(225) == "SW"

    def test_northwest(self):
        assert degrees_to_compass(315) == "NW"

    def test_wraps_past_360(self):
        # 361° == 1° == still N
        assert degrees_to_compass(361) == "N"

    def test_nnw(self):
        assert degrees_to_compass(337.5) == "NNW"


class TestSht30Conversion:
    def test_min_raw_temp(self):
        # raw=0 → −45 °C
        assert abs(sht30_raw_to_celsius(0) - (-45.0)) < 0.001

    def test_max_raw_temp(self):
        # raw=65535 → −45 + 175 = 130 °C
        assert abs(sht30_raw_to_celsius(65535) - 130.0) < 0.1

    def test_midpoint_temp(self):
        # raw=32767 ≈ 0xFFFF/2 → midpoint ≈ 42.5 °C
        t = sht30_raw_to_celsius(32767)
        assert 42 < t < 43

    def test_min_raw_humidity(self):
        assert abs(sht30_raw_to_humidity(0) - 0.0) < 0.001

    def test_max_raw_humidity(self):
        assert abs(sht30_raw_to_humidity(65535) - 100.0) < 0.001

    def test_50pct_humidity(self):
        h = sht30_raw_to_humidity(32767)
        assert 49 < h < 51


class TestSanityChecks:
    def test_valid_indoor_temp(self):
        assert sanity_check_temp(22.5)

    def test_extreme_cold(self):
        assert not sanity_check_temp(-50)

    def test_extreme_hot(self):
        assert not sanity_check_temp(90)

    def test_valid_humidity(self):
        assert sanity_check_humidity(55)

    def test_humidity_over_100(self):
        assert not sanity_check_humidity(101)

    def test_negative_humidity(self):
        assert not sanity_check_humidity(-1)


class TestBuildPayload:
    def test_both_sensors(self):
        payload = build_payload(22.1, 55.3, 1013.2, 18.4, 70.0)
        assert payload["temperature"] == 22.1
        assert payload["temperature_indoor"] == 22.1
        assert payload["temperature_outdoor"] == 18.4
        assert payload["pressure"] == 1013.2
        assert payload["sensor_indoor"] == "ENV3"
        assert payload["sensor_outdoor"] == "DHT22"

    def test_outdoor_only(self):
        payload = build_payload(None, None, None, 15.5, 80.0)
        # Outdoor should become primary
        assert payload["temperature"] == 15.5
        assert "temperature_indoor" not in payload
        assert payload["sensor_outdoor"] == "DHT22"

    def test_indoor_only(self):
        payload = build_payload(21.0, 60.0, 1010.0, None, None)
        assert payload["temperature"] == 21.0
        assert "temperature_outdoor" not in payload

    def test_no_sensors(self):
        payload = build_payload(None, None, None, None, None)
        assert "temperature" not in payload
        assert len(payload) == 0

    def test_rounding(self):
        payload = build_payload(22.123, 55.678, 1013.456, None, None)
        assert payload["temperature"] == 22.1
        assert payload["humidity"] == 55.7
        assert payload["pressure"] == 1013.5

    def test_pressure_added_indoor(self):
        payload = build_payload(20.0, 50.0, 1015.0, None, None)
        assert "pressure_indoor" in payload
        assert payload["pressure_indoor"] == payload["pressure"]
