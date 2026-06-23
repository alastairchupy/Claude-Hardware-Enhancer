"""
Arduino Uno component specification.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


def get_arduino_uno_spec() -> ComponentSpec:
    """Return the Arduino Uno R3 component specification."""
    pins = {
        # digital PWM-capable pins
        "D3": Pin(name="D3", pin_number=3, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable"),
        "D5": Pin(name="D5", pin_number=5, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable"),
        "D6": Pin(name="D6", pin_number=6, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable"),
        "D9": Pin(name="D9", pin_number=9, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable"),
        "D10": Pin(name="D10", pin_number=10, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable"),
        "D11": Pin(name="D11", pin_number=11, direction="bidirectional", voltage=5.0, current_limit=40, is_pwm_capable=True, description="PWM-capable (also SPI MOSI)"),
        # other digital pins
        "D0": Pin(name="D0", pin_number=0, direction="bidirectional", voltage=5.0, current_limit=40, description="UART RX"),
        "D1": Pin(name="D1", pin_number=1, direction="bidirectional", voltage=5.0, current_limit=40, description="UART TX"),
        "D2": Pin(name="D2", pin_number=2, direction="bidirectional", voltage=5.0, current_limit=40, description=""),
        "D4": Pin(name="D4", pin_number=4, direction="bidirectional", voltage=5.0, current_limit=40, description=""),
        "D7": Pin(name="D7", pin_number=7, direction="bidirectional", voltage=5.0, current_limit=40, description=""),
        "D8": Pin(name="D8", pin_number=8, direction="bidirectional", voltage=5.0, current_limit=40, description=""),
        "D12": Pin(name="D12", pin_number=12, direction="bidirectional", voltage=5.0, current_limit=40, description="SPI MISO"),
        "D13": Pin(name="D13", pin_number=13, direction="bidirectional", voltage=5.0, current_limit=40, description="SPI SCK (also built-in LED)"),
        # analog pins (also usable as digital)
        "A0": Pin(name="A0", pin_number=14, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description=""),
        "A1": Pin(name="A1", pin_number=15, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description=""),
        "A2": Pin(name="A2", pin_number=16, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description=""),
        "A3": Pin(name="A3", pin_number=17, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description=""),
        "A4": Pin(name="A4", pin_number=18, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description="I2C SDA"),
        "A5": Pin(name="A5", pin_number=19, direction="bidirectional", voltage=5.0, current_limit=40, is_adc_capable=True, description="I2C SCL"),
        # power pins
        "5V": Pin(name="5V", pin_number=None, direction="power", voltage=5.0, current_limit=450, description="5V regulated output (USB) or input"),
        "3.3V": Pin(name="3.3V", pin_number=None, direction="power", voltage=3.3, current_limit=150, description="3.3V regulated output"),
        "GND": Pin(name="GND", pin_number=None, direction="ground", voltage=0, description="Ground"),
        "Vin": Pin(name="Vin", pin_number=None, direction="power", voltage=7, description="External power input (7-12V)"),
        "AREF": Pin(name="AREF", pin_number=None, direction="input", voltage=5.0, description="Analog reference voltage"),
    }

    return ComponentSpec(
        name="Arduino Uno R3",
        component_type=ComponentType.MICROCONTROLLER,
        manufacturer="Arduino",
        model="ATmega328P",
        voltage=5.0,  # Logic voltage
        current_limit=0.040,  # 40mA per GPIO
        power_rating=1.0,
        pins=pins,
        properties={
            "family": "Arduino",
            "flash": "32KB",
            "ram": "2KB",
            "clock_speed_mhz": 16,
            "adc_resolution": 10,
            "pwm_resolution": 8,
            "i2c_channels": 1,
            "spi_channels": 1,
            "uart_channels": 1,
        },
    )