"""
Sensor component specifications.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


def _make_i2c_sensor(name: str, voltage: float, address: int, properties: dict) -> ComponentSpec:
    """Create a generic I2C sensor spec."""
    pins = {
        "VCC": Pin(name="VCC", direction="power", voltage=voltage, description="Power supply"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
        "SDA": Pin(name="SDA", direction="bidirectional", voltage=voltage, description="I2C data"),
        "SCL": Pin(name="SCL", direction="input", voltage=voltage, description="I2C clock"),
    }
    return ComponentSpec(name=name, component_type=ComponentType.SENSOR, voltage=voltage, pins=pins, properties=properties)


def _make_analog_sensor(name: str, voltage: float, properties: dict) -> ComponentSpec:
    """Create a generic analog sensor spec."""
    pins = {
        "VCC": Pin(name="VCC", direction="power", voltage=voltage, description="Power supply"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
        "OUT": Pin(name="OUT", direction="output", voltage=voltage, is_adc_capable=True, description="Analog output"),
    }
    return ComponentSpec(name=name, component_type=ComponentType.SENSOR, voltage=voltage, pins=pins, properties=properties)


# I2C Sensors
SSD1306 = _make_i2c_sensor(
    "OLED Display SSD1306",
    voltage=3.3,
    address=0x3C,
    properties={"type": "oled_display", "resolution": "128x64", "interface": "I2C", "notes": "Common 0.96\" OLED display"},
)

BMP280 = _make_i2c_sensor(
    "BMP280 Barometric Pressure Sensor",
    voltage=3.3,
    address=0x76,
    properties={
        "type": "barometric_pressure",
        "interface": "I2C/SPI",
        "pressure_range": "300-1100 hPa",
        "temp_accuracy": "±1°C",
        "notes": "Also measures temperature",
    },
)

MPU6050 = _make_i2c_sensor(
    "MPU6050 6-Axis Gyroscope/Accelerometer",
    voltage=3.3,
    address=0x68,
    properties={
        "type": "imu",
        "interface": "I2C",
        "gyro_range": "±250 to ±2000 °/s",
        "accel_range": "±2g to ±16g",
        "notes": "6-axis IMU with built-in DMP",
    },
)

HC_SR04 = _make_analog_sensor(
    "HC-SR04 Ultrasonic Distance Sensor",
    voltage=5.0,
    properties={
        "type": "ultrasonic_distance",
        "range_cm": "2-400",
        "accuracy": "±3mm",
        "interface": "GPIO/analog",
        "notes": "Requires trigger + echo GPIO pins",
        "trigger_voltage": 5.0,
        "echo_output_voltage": 5.0,
    },
)

DHT22 = _make_analog_sensor(
    "DHT22 Temperature/Humidity Sensor",
    voltage=3.3,
    properties={
        "type": "temperature_humidity",
        "interface": "Single-wire digital",
        "temp_range": "-40 to 80°C",
        "humidity_range": "0-100% RH",
        "accuracy": "±0.5°C, ±2% RH",
        "notes": "Single-wire protocol; library required",
    },
)

SENSOR_DATABASE = {
    "ssd1306": SSD1306,
    "bmp280": BMP280,
    "mpu6050": MPU6050,
    "hc-sr04": HC_SR04,
    "hc_sr04": HC_SR04,
    "dht22": DHT22,
    "dht11": _make_analog_sensor(
        "DHT11 Temperature/Humidity Sensor",
        voltage=3.3,
        properties={
            "type": "temperature_humidity",
            "interface": "Single-wire digital",
            "temp_range": "0 to 50°C",
            "humidity_range": "20-90% RH",
            "accuracy": "±2°C, ±5% RH",
            "notes": "Lower cost than DHT22 but less accurate",
        },
    ),
}