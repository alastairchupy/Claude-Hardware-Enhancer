"""Raspberry Pi Pico component specification."""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


def get_pico_spec() -> ComponentSpec:
    """Return the Raspberry Pi Pico component specification."""
    pins = {
        # GP0-GP28 (PWM-capable on all except GP23-28 for certain uses)
        "GP0": Pin(name="GP0", pin_number=0, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="UART0 TX"),
        "GP1": Pin(name="GP1", pin_number=1, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="UART0 RX"),
        "GP2": Pin(name="GP2", pin_number=2, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="I2C0 SDA"),
        "GP3": Pin(name="GP3", pin_number=3, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="I2C0 SCL"),
        "GP4": Pin(name="GP4", pin_number=4, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description=""),
        "GP5": Pin(name="GP5", pin_number=5, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description=""),
        "GP6": Pin(name="GP6", pin_number=6, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="SPI0 RX"),
        "GP7": Pin(name="GP7", pin_number=7, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="SPI0 CSn"),
        "GP8": Pin(name="GP8", pin_number=8, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="SPI0 SCK"),
        "GP9": Pin(name="GP9", pin_number=9, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="SPI0 MOSI"),
        "GP10": Pin(name="GP10", pin_number=10, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="SPI0 MISO"),
        "GP11": Pin(name="GP11", pin_number=11, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP12": Pin(name="GP12", pin_number=12, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP13": Pin(name="GP13", pin_number=13, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP14": Pin(name="GP14", pin_number=14, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="UART1 TX"),
        "GP15": Pin(name="GP15", pin_number=15, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description="UART1 RX"),
        "GP16": Pin(name="GP16", pin_number=16, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP17": Pin(name="GP17", pin_number=17, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP18": Pin(name="GP18", pin_number=18, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP19": Pin(name="GP19", pin_number=19, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP20": Pin(name="GP20", pin_number=20, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP21": Pin(name="GP21", pin_number=21, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        "GP22": Pin(name="GP22", pin_number=22, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, description=""),
        # ADCs (GP26-GP28) - 12-bit ADC, 3.3V max input
        "GP26": Pin(name="GP26", pin_number=26, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="ADC0"),
        "GP27": Pin(name="GP27", pin_number=27, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="ADC1"),
        "GP28": Pin(name="GP28", pin_number=28, direction="bidirectional", voltage=3.3, current_limit=12, is_pwm_capable=True, is_adc_capable=True, description="ADC2"),
        # Power pins
        "3V3": Pin(name="3V3", pin_number=None, direction="power", voltage=3.3, current_limit=300, description="3.3V output"),
        "VBUS": Pin(name="VBUS", pin_number=None, direction="power", voltage=5.0, description="USB bus voltage"),
        "VSYS": Pin(name="VSYS", pin_number=None, direction="power", voltage=5.0, description="System input (min 1.8V, max 5.5V)"),
        "GND": Pin(name="GND", pin_number=None, direction="ground", voltage=0.0, description="Ground"),
        "AGND": Pin(name="AGND", pin_number=None, direction="ground", voltage=0.0, description="Analog ground"),
    }

    return ComponentSpec(
        name="Raspberry Pi Pico",
        component_type=ComponentType.MICROCONTROLLER,
        manufacturer="Raspberry Pi",
        model="RP2040",
        voltage=3.3,
        current_limit=0.012,  # 12mA per GPIO (lower than ESP32/Arduino)
        power_rating=0.8,
        pins=pins,
        properties={
            "family": "RP2040",
            "flash": "2MB",
            "ram": "264KB",
            "clock_speed_mhz": 133,
            "adc_channels": 4,
            "pwm_channels": 16,
            "i2c_channels": 2,
            "spi_channels": 2,
            "uart_channels": 2,
            "usb": True,
        },
    )