"""
ESP32 DevKit V1 component specification.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


def get_esp32_spec() -> ComponentSpec:
    """Return the ESP32 DevKit V1 component specification."""
    pins = {
        # General purpose GPIO (all 3.3V)
        "GPIO0": Pin(name="GPIO0", pin_number=0, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description="Boot strapping pin"),
        "GPIO1": Pin(name="GPIO1", pin_number=1, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description="TX pin"),
        "GPIO2": Pin(name="GPIO2", pin_number=2, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description="Built-in LED"),
        "GPIO3": Pin(name="GPIO3", pin_number=3, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description="RX pin"),
        "GPIO4": Pin(name="GPIO4", pin_number=4, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO5": Pin(name="GPIO5", pin_number=5, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        # GPIO6-11: reserved for SPI Flash
        "GPIO12": Pin(name="GPIO12", pin_number=12, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description=""),
        "GPIO13": Pin(name="GPIO13", pin_number=13, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description=""),
        "GPIO14": Pin(name="GPIO14", pin_number=14, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description=""),
        "GPIO15": Pin(name="GPIO15", pin_number=15, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description=""),
        "GPIO16": Pin(name="GPIO16", pin_number=16, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO17": Pin(name="GPIO17", pin_number=17, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO18": Pin(name="GPIO18", pin_number=18, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO19": Pin(name="GPIO19", pin_number=19, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO21": Pin(name="GPIO21", pin_number=21, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO22": Pin(name="GPIO22", pin_number=22, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        "GPIO23": Pin(name="GPIO23", pin_number=23, direction="bidirectional", voltage=3.3, current_limit=40, is_pwm_capable=True, description=""),
        # PWM-capable: GPIO25, GPIO26, GPIO27 recommended for motor control
        "GPIO25": Pin(name="GPIO25", pin_number=25, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description="Recommended for PWM/motor control"),
        "GPIO26": Pin(name="GPIO26", pin_number=26, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description="Recommended for PWM/motor control"),
        "GPIO27": Pin(name="GPIO27", pin_number=27, direction="bidirectional", voltage=3.3, current_limit=40, is_adc_capable=True, is_pwm_capable=True, description=""),
        # Input-only pins (34-39) - cannot output PWM or drive HIGH
        "GPIO34": Pin(name="GPIO34", pin_number=34, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY - cannot output PWM"),
        "GPIO35": Pin(name="GPIO35", pin_number=35, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY"),
        "GPIO36": Pin(name="GPIO36", pin_number=36, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY"),
        "GPIO37": Pin(name="GPIO37", pin_number=37, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY"),
        "GPIO38": Pin(name="GPIO38", pin_number=38, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY"),
        "GPIO39": Pin(name="GPIO39", pin_number=39, direction="input", voltage=3.3, current_limit=0, is_adc_capable=True, description="INPUT ONLY"),
        # I2C default pins
        "GPIO21": Pin(name="GPIO21", pin_number=21, direction="bidirectional", voltage=3.3, current_limit=40, description="Default I2C SDA"),
        "GPIO22": Pin(name="GPIO22", pin_number=22, direction="bidirectional", voltage=3.3, current_limit=40, description="Default I2C SCL"),
        # SPI pins
        "GPIO18": Pin(name="GPIO18", pin_number=18, direction="bidirectional", voltage=3.3, current_limit=40, description="SPI MOSI"),
        "GPIO19": Pin(name="GPIO19", pin_number=19, direction="bidirectional", voltage=3.3, current_limit=40, description="SPI MISO"),
        "GPIO23": Pin(name="GPIO23", pin_number=23, direction="bidirectional", voltage=3.3, current_limit=40, description="SPI CLK"),
        # Power pins
        "3V3": Pin(name="3V3", pin_number=None, direction="power", voltage=3.3, current_limit=1000, description="3.3V power output (max 1A)"),
        "GND": Pin(name="GND", pin_number=None, direction="ground", voltage=0, description="Ground"),
        "VIN": Pin(name="VIN", pin_number=None, direction="power", voltage=5, description="5V input or output from USB"),
    }

    return ComponentSpec(
        name="ESP32 DevKit V1",
        component_type=ComponentType.MICROCONTROLLER,
        manufacturer="Espressif",
        model="ESP32-WROOM-32",
        voltage=3.3,  # Logic voltage
        current_limit=0.040,  # 40mA per GPIO
        power_rating=0.5,  # Total chip dissipation
        pins=pins,
        properties={
            "family": "ESP32",
            "flash": "4MB",
            "ram": "520KB",
            "clock_speed_mhz": 240,
            "wifi": True,
            "bluetooth": True,
            "adc_channels": 18,
            "pwm_channels": 16,
            "i2c_channels": 2,
            "spi_channels": 2,
            "uart_channels": 3,
        },
    )


# Aliases
ESP32_DEVKIT_V1 = get_esp32_spec