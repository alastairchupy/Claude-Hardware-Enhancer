"""
Power supply component specifications.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin

POWER_SUPPLY_DATABASE: dict[str, ComponentSpec] = {
    "12v_2a": ComponentSpec(
        name="12V 2A Switching Power Supply",
        component_type=ComponentType.POWER_SUPPLY,
        voltage=12.0,
        current_limit=2.0,
        power_rating=24.0,
        pins={
            "positive": Pin(name="positive", direction="power", voltage=12.0, description="12V output"),
            "negative": Pin(name="negative", direction="ground", voltage=0, description="Ground"),
        },
        properties={"type": "smps", "input_voltage_range": "100-240V AC", "efficiency": 0.85},
    ),
    "5v_3a": ComponentSpec(
        name="5V 3A USB Power Supply",
        component_type=ComponentType.POWER_SUPPLY,
        voltage=5.0,
        current_limit=3.0,
        power_rating=15.0,
        pins={
            "positive": Pin(name="positive", direction="power", voltage=5.0, description="5V output"),
            "negative": Pin(name="negative", direction="ground", voltage=0, description="Ground"),
        },
        properties={"type": "usb_charger", "connector": "USB-A"},
    ),
    "3v3_1a": ComponentSpec(
        name="3.3V 1A LDO Regulator",
        component_type=ComponentType.POWER_SUPPLY,
        voltage=3.3,
        current_limit=1.0,
        power_rating=3.3,
        pins={
            "VIN": Pin(name="VIN", direction="power", voltage=5.0, description="Input voltage (5V)"),
            "VOUT": Pin(name="VOUT", direction="power", voltage=3.3, current_limit=1000, description="3.3V output"),
            "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
        },
        properties={"type": "ldo_regulator", "dropout_voltage": 0.3, "noise_uVrms": 50},
    ),
    "5v_regulator_7805": ComponentSpec(
        name="7805 5V Linear Regulator",
        component_type=ComponentType.POWER_SUPPLY,
        voltage=5.0,
        current_limit=1.5,
        power_rating=7.5,
        pins={
            "VIN": Pin(name="VIN", direction="power", voltage=7.0, description="Input (7-12V DC)"),
            "VOUT": Pin(name="VOUT", direction="power", voltage=5.0, current_limit=1500, description="5V output"),
        },
        properties={
            "type": "linear_regulator",
            "dropout_voltage": 2.0,
            "requires_heat_sink": True,
            "notes": "Inefficient for battery applications. Drops 2V minimum.",
        },
    ),
}