"""
Motor driver component specifications and database.
"""

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin


# ---------------------------------------------------------------------------
# HW-039 Motor Driver Module
# ---------------------------------------------------------------------------
def get_hw039_spec() -> ComponentSpec:
    """Return the HW-039 (L298N-based) motor driver specification."""
    pins = {
        "IN1": Pin(name="IN1", direction="input", voltage=3.3, current_limit=10, description="Motor input 1"),
        "IN2": Pin(name="IN2", direction="input", voltage=3.3, current_limit=10, description="Motor input 2"),
        "IN3": Pin(name="IN3", direction="input", voltage=3.3, current_limit=10, description="Motor input 3"),
        "IN4": Pin(name="IN4", direction="input", voltage=3.3, current_limit=10, description="Motor input 4"),
        "ENA": Pin(name="ENA", direction="input", voltage=3.3, current_limit=10, is_pwm_capable=True, description="Enable A / PWM speed control"),
        "ENB": Pin(name="ENB", direction="input", voltage=3.3, current_limit=10, is_pwm_capable=True, description="Enable B / PWM speed control"),
        "OUT1": Pin(name="OUT1", direction="output", voltage=12.0, current_limit=2000, description="Motor A output 1"),
        "OUT2": Pin(name="OUT2", direction="output", voltage=12.0, current_limit=2000, description="Motor A output 2"),
        "OUT3": Pin(name="OUT3", direction="output", voltage=12.0, current_limit=2000, description="Motor B output 1"),
        "OUT4": Pin(name="OUT4", direction="output", voltage=12.0, current_limit=2000, description="Motor B output 2"),
        "VCC": Pin(name="VCC", direction="power", voltage=12.0, current_limit=3000, description="Motor supply voltage (5-35V)"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
        "5V": Pin(name="5V", direction="power", voltage=5.0, current_limit=500, description="5V output (from internal regulator)"),
    }

    return ComponentSpec(
        name="HW-039 Motor Driver",
        component_type=ComponentType.MOTOR_DRIVER,
        manufacturer="Generic",
        model="HW-039",
        voltage=12.0,
        current_limit=2.0,  # Per channel
        power_rating=25.0,
        pins=pins,
        properties={
            "chipset": "L298N",
            "channels": 2,
            "logic_voltage": 3.3,
            "motor_voltage_range": "5-35V",
            "output_current_per_channel": 2000,  # mA
            "total_max_current": 3000,  # mA
            "pwm_support": True,
            "notes": "Use ENA and ENB pins for PWM speed control. IN1/IN2 control direction.",
        },
    )


# ---------------------------------------------------------------------------
# L298N Dual H-Bridge
# ---------------------------------------------------------------------------
def get_l298n_spec() -> ComponentSpec:
    """Return the L298N dual H-bridge motor driver specification."""
    return get_hw039_spec()  # HW-039 is essentially a L298N module


# ---------------------------------------------------------------------------
# L293D Motor Driver Shield
# ---------------------------------------------------------------------------
def get_l293d_spec() -> ComponentSpec:
    """Return the L293D motor driver specification."""
    pins = {
        "IN1": Pin(name="IN1", direction="input", voltage=5.0, current_limit=10, description="Motor 1 input 1"),
        "IN2": Pin(name="IN2", direction="input", voltage=5.0, current_limit=10, description="Motor 1 input 2"),
        "IN3": Pin(name="IN3", direction="input", voltage=5.0, current_limit=10, description="Motor 2 input 1"),
        "IN4": Pin(name="IN4", direction="input", voltage=5.0, current_limit=10, description="Motor 2 input 2"),
        "ENA": Pin(name="ENA", direction="input", voltage=5.0, current_limit=10, is_pwm_capable=True, description="Enable 1 / PWM"),
        "ENB": Pin(name="ENB", direction="input", voltage=5.0, current_limit=10, is_pwm_capable=True, description="Enable 2 / PWM"),
        "OUT1": Pin(name="OUT1", direction="output", voltage=12.0, current_limit=600, description="Motor 1 output 1"),
        "OUT2": Pin(name="OUT2", direction="output", voltage=12.0, current_limit=600, description="Motor 1 output 2"),
        "OUT3": Pin(name="OUT3", direction="output", voltage=12.0, current_limit=600, description="Motor 2 output 1"),
        "OUT4": Pin(name="OUT4", direction="output", voltage=12.0, current_limit=600, description="Motor 2 output 2"),
        "VCC": Pin(name="VCC", direction="power", voltage=12.0, current_limit=1000, description="Motor supply (4.5-36V)"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
    }

    return ComponentSpec(
        name="L293D Motor Driver",
        component_type=ComponentType.MOTOR_DRIVER,
        manufacturer="Texas Instruments",
        model="L293D",
        voltage=12.0,
        current_limit=0.600,  # 600mA per channel
        power_rating=4.0,
        pins=pins,
        properties={
            "chipset": "L293D",
            "channels": 2,
            "logic_voltage": 5.0,
            "motor_voltage_range": "4.5-36V",
            "output_current_per_channel": 600,  # mA
            "pwm_support": True,
            "notes": "Lower current than L298N. Good for small motors.",
        },
    )


# ---------------------------------------------------------------------------
# DRV8833 Dual H-Bridge
# ---------------------------------------------------------------------------
def get_drv8833_spec() -> ComponentSpec:
    """Return the DRV8833 dual H-bridge motor driver specification."""
    pins = {
        "AIN1": Pin(name="AIN1", direction="input", voltage=3.3, current_limit=10, description="Motor A input 1"),
        "AIN2": Pin(name="AIN2", direction="input", voltage=3.3, current_limit=10, description="Motor A input 2"),
        "BIN1": Pin(name="BIN1", direction="input", voltage=3.3, current_limit=10, description="Motor B input 1"),
        "BIN2": Pin(name="BIN2", direction="input", voltage=3.3, current_limit=10, description="Motor B input 2"),
        "STBY": Pin(name="STBY", direction="input", voltage=3.3, current_limit=1, description="Standby pin (active LOW)"),
        "AOUT1": Pin(name="AOUT1", direction="output", voltage=12.0, current_limit=1500, description="Motor A output 1"),
        "AOUT2": Pin(name="AOUT2", direction="output", voltage=12.0, current_limit=1500, description="Motor A output 2"),
        "BOUT1": Pin(name="BOUT1", direction="output", voltage=12.0, current_limit=1500, description="Motor B output 1"),
        "BOUT2": Pin(name="BOUT2", direction="output", voltage=12.0, current_limit=1500, description="Motor B output 2"),
        "VM": Pin(name="VM", direction="power", voltage=12.0, current_limit=2000, description="Motor supply (2.7-10.8V)"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
    }

    return ComponentSpec(
        name="DRV8833 Motor Driver",
        component_type=ComponentType.MOTOR_DRIVER,
        manufacturer="Texas Instruments",
        model="DRV8833",
        voltage=3.3,  # Logic voltage
        current_limit=1.5,  # Per channel
        power_rating=3.0,
        pins=pins,
        properties={
            "chipset": "DRV8833",
            "channels": 2,
            "logic_voltage": 3.3,
            "motor_voltage_range": "2.7-10.8V",
            "output_current_per_channel": 1500,  # mA
            "pwm_support": True,
            "notes": "3.3V logic compatible with ESP32. Smaller and more efficient than L298N.",
        },
    )


# ---------------------------------------------------------------------------
# TB6612FNG Dual H-Bridge
# ---------------------------------------------------------------------------
def get_tb6612_spec() -> ComponentSpec:
    """Return the TB6612FNG dual H-bridge motor driver specification."""
    pins = {
        "AIN1": Pin(name="AIN1", direction="input", voltage=3.3, current_limit=10, description="Motor A input 1"),
        "AIN2": Pin(name="AIN2", direction="input", voltage=3.3, current_limit=10, description="Motor A input 2"),
        "PWMA": Pin(name="PWMA", direction="input", voltage=3.3, current_limit=10, is_pwm_capable=True, description="Motor A PWM / speed control"),
        "BIN1": Pin(name="BIN1", direction="input", voltage=3.3, current_limit=10, description="Motor B input 1"),
        "BIN2": Pin(name="BIN2", direction="input", voltage=3.3, current_limit=10, description="Motor B input 2"),
        "PWMB": Pin(name="PWMB", direction="input", voltage=3.3, current_limit=10, is_pwm_capable=True, description="Motor B PWM / speed control"),
        "STBY": Pin(name="STBY", direction="input", voltage=3.3, current_limit=1, description="Standby (active LOW)"),
        "A01": Pin(name="A01", direction="output", voltage=12.0, current_limit=1300, description="Motor A output 1"),
        "A02": Pin(name="A02", direction="output", voltage=12.0, current_limit=1300, description="Motor A output 2"),
        "B01": Pin(name="B01", direction="output", voltage=12.0, current_limit=1300, description="Motor B output 1"),
        "B02": Pin(name="B02", direction="output", voltage=12.0, current_limit=1300, description="Motor B output 2"),
        "VM": Pin(name="VM", direction="power", voltage=12.0, current_limit=3000, description="Motor supply (2.7-13.5V)"),
        "VCC": Pin(name="VCC", direction="power", voltage=3.3, current_limit=100, description="Logic supply (2.7-5.5V)"),
        "GND": Pin(name="GND", direction="ground", voltage=0, description="Ground"),
    }

    return ComponentSpec(
        name="TB6612FNG Motor Driver",
        component_type=ComponentType.MOTOR_DRIVER,
        manufacturer="Toshiba",
        model="TB6612FNG",
        voltage=3.3,  # Logic voltage
        current_limit=1.3,  # Per channel
        power_rating=3.0,
        pins=pins,
        properties={
            "chipset": "TB6612FNG",
            "channels": 2,
            "logic_voltage": 3.3,
            "motor_voltage_range": "2.7-13.5V",
            "output_current_per_channel": 1300,  # mA
            "pwm_support": True,
            "notes": "More efficient than L298N, 3.3V logic compatible. Requires separate PWM pin.",
        },
    )


# ---------------------------------------------------------------------------
# Motor driver database
# ---------------------------------------------------------------------------
DRIVER_DATABASE: dict[str, callable] = {
    "hw-039": get_hw039_spec,
    "l298n": get_l298n_spec,
    "l293d": get_l293d_spec,
    "drv8833": get_drv8833_spec,
    "tb6612": get_tb6612_spec,
}