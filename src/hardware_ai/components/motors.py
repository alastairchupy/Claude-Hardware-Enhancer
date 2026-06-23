"""
Motor component specifications and database.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


# ---------------------------------------------------------------------------
# MY6812 Brushed DC Motor
# ---------------------------------------------------------------------------
def get_my6812_spec() -> ComponentSpec:
    """Return the MY6812 brushed DC motor specification."""
    pins = {
        "positive": Pin(name="positive", direction="bidirectional", voltage=12.0, description="Motor positive terminal"),
        "negative": Pin(name="negative", direction="bidirectional", voltage=12.0, description="Motor negative terminal"),
    }
    return ComponentSpec(
        name="MY6812 Brushed DC Motor",
        component_type=ComponentType.MOTOR,
        manufacturer="Generic",
        model="MY6812",
        voltage=12.0,
        current_limit=2.5,  # No-load current ~0.15A, stall current ~2.5A
        power_rating=30.0,  # 30W rated
        pins=pins,
        properties={
            "type": "brushed_dc",
            "rated_voltage": 12.0,
            "no_load_current": 0.15,
            "stall_current": 2.5,
            "rated_power": 30.0,
            "rated_torque_mn_m": 45.0,
            "speed_rpm": 12000,
            "shaft_diameter_mm": 3.17,
            "requires_driver": True,
            "requires_flyback_protection": True,
            "notes": "Add flyback diode for inductive spike protection",
        },
    )


# ---------------------------------------------------------------------------
# Common motor database
# ---------------------------------------------------------------------------
MOTOR_DATABASE: dict[str, callable] = {
    "my6812": get_my6812_spec,
    "nema17": lambda: _make_generic_stepper("NEMA 17", 12.0, 1.5, 5.0),
    "28byj48": lambda: _make_generic_stepper("28BYJ-48", 5.0, 0.25, 5.0),
    "jga25": lambda: _make_generic_dc("JGA25 DC Motor", 12.0, 1.5, 15.0),
    "rrs395": lambda: _make_generic_dc("RS-395 Brushed DC", 6.0, 2.0, 10.0),
}


def _make_generic_dc(name: str, voltage: float, current: float, power: float) -> ComponentSpec:
    """Create a generic DC motor spec."""
    pins = {
        "positive": Pin(name="positive", direction="bidirectional", voltage=voltage, description="Motor positive"),
        "negative": Pin(name="negative", direction="bidirectional", voltage=voltage, description="Motor negative"),
    }
    return ComponentSpec(
        name=name,
        component_type=ComponentType.MOTOR,
        manufacturer="Generic",
        model=name,
        voltage=voltage,
        current_limit=current,
        power_rating=power,
        pins=pins,
        properties={
            "type": "brushed_dc",
            "rated_voltage": voltage,
            "requires_driver": True,
            "requires_flyback_protection": True,
        },
    )


def _make_generic_stepper(name: str, voltage: float, current: float, power: float) -> ComponentSpec:
    """Create a generic stepper motor spec."""
    pins = {
        "coil_a": Pin(name="coil_a", direction="bidirectional", voltage=voltage, description="Coil A"),
        "coil_b": Pin(name="coil_b", direction="bidirectional", voltage=voltage, description="Coil B"),
    }
    return ComponentSpec(
        name=name,
        component_type=ComponentType.MOTOR,
        manufacturer="Generic",
        model=name,
        voltage=voltage,
        current_limit=current,
        power_rating=power,
        pins=pins,
        properties={
            "type": "stepper",
            "rated_voltage": voltage,
            "requires_driver": True,
            "requires_stepper_driver": True,
            "notes": "Use stepper driver (A4988, DRV8825) for microstepping control",
        },
    )