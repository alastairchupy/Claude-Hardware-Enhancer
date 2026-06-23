"""
Resistor specifications and standard value series.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin

# Standard E12/E24 resistor values (Ohms)
RESISTOR_STANDARD_VALUES = [
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2,  # E12 × 1
    10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82,  # E12 × 10
    100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820,  # E12 × 100
    1000, 1200, 1500, 1800, 2200, 2700, 3300, 3900, 4700, 5600, 6800, 8200,
    10000, 12000, 15000, 18000, 22000, 27000, 33000, 39000, 47000, 56000, 68000, 82000,
    100000, 120000, 150000, 180000, 220000, 270000, 330000, 390000, 470000, 560000, 680000, 820000,
    1000000, 1200000, 1500000, 1800000, 2200000, 2700000, 3300000, 3900000, 4700000, 5600000, 6800000, 8200000,
    10000000,
]

COMMON_RESISTOR_VALUES = [100, 220, 330, 470, 680, 1000, 2200, 3300, 4700, 10000, 22000, 47000, 100000]


def make_resistor(value_ohms: float, tolerance: float = 5.0, power_rating: float = 0.25) -> ComponentSpec:
    """Create a resistor component specification."""
    pins = {
        "terminal1": Pin(name="terminal1", direction="bidirectional", voltage=0, description=""),
        "terminal2": Pin(name="terminal2", direction="bidirectional", voltage=0, description=""),
    }
    return ComponentSpec(
        name=f"{value_ohms}Ω Resistor",
        component_type=ComponentType.RESISTOR,
        voltage=None,
        current_limit=None,
        power_rating=power_rating,
        pins=pins,
        properties={
            "resistance_ohms": value_ohms,
            "tolerance_percent": tolerance,
            "power_rating_w": power_rating,
            "common_led_resistor": _is_common_led_resistor(value_ohms),
        },
    )


def _is_common_led_resistor(value: float) -> bool:
    """Check if resistor value is commonly used for LED current limiting."""
    return value in [150, 220, 330, 470] or value in [1000, 1500]  # 3.3V/5V LEDs


# Common LED current limiting resistor calculator
def led_resistor(led_voltage_drop: float, source_voltage: float, led_current_ma: float = 20.0) -> float:
    """Calculate LED current limiting resistor value."""
    voltage_drop = source_voltage - led_voltage_drop
    return (voltage_drop / (led_current_ma / 1000.0))