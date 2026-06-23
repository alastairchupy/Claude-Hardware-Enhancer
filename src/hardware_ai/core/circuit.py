"""
Circuit representation for HardwareAI simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ConnectionType(str, Enum):
    """Type of electrical connection."""

    POWER = "power"
    GROUND = "ground"
    DIGITAL = "digital"
    ANALOG = "analog"
    PWM = "pwm"
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"


class ComponentType(str, Enum):
    """Category of component."""

    MICROCONTROLLER = "microcontroller"
    MOTOR = "motor"
    MOTOR_DRIVER = "motor_driver"
    SENSOR = "sensor"
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    LED = "led"
    POWER_SUPPLY = "power_supply"
    DISPLAY = "display"
    RELAY = "relay"
    CONNECTOR = "connector"


@dataclass
class Pin:
    """Represents a component pin/connection point."""

    name: str
    pin_number: Optional[int] = None
    direction: str = "bidirectional"  # input, output, bidirectional, power, ground
    voltage: Optional[float] = None  # Nominal voltage level
    current_limit: Optional[float] = None  # Max current in mA
    is_pwm_capable: bool = False
    is_adc_capable: bool = False
    description: str = ""


@dataclass
class ComponentSpec:
    """Specification for a hardware component."""

    name: str
    component_type: ComponentType
    manufacturer: str = ""
    model: str = ""
    voltage: Optional[float] = None  # V
    current_limit: Optional[float] = None  # A
    power_rating: Optional[float] = None  # W
    pins: dict[str, Pin] = field(default_factory=dict)
    properties: dict = field(default_factory=dict)  # Flexible extra properties

    def __repr__(self) -> str:
        return f"ComponentSpec({self.name}, {self.component_type.value}, {self.model})"


class CircuitConnection(BaseModel):
    """A connection between two component pins."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    connection_type: ConnectionType = ConnectionType.DIGITAL
    wire_gauge: Optional[float] = None  # AWG
    description: str = ""

    def __repr__(self) -> str:
        return f"{self.from_component}.{self.from_pin} → {self.to_component}.{self.to_pin}"


class Circuit(BaseModel):
    """Represents a circuit with components and connections."""

    name: str = "Untitled Circuit"
    components: dict[str, ComponentSpec] = Field(default_factory=dict)
    connections: list[CircuitConnection] = Field(default_factory=list)
    power_supplies: list[str] = Field(default_factory=list)  # Component IDs that are power sources
    grounds: list[str] = Field(default_factory=list)  # Component IDs that are ground references

    def add_component(self, component_id: str, spec: ComponentSpec) -> None:
        """Add a component to the circuit."""
        self.components[component_id] = spec

    def add_connection(self, connection: CircuitConnection) -> None:
        """Add a connection between two pins."""
        self.connections.append(connection)

    def get_component(self, component_id: str) -> Optional[ComponentSpec]:
        """Get a component by ID."""
        return self.components.get(component_id)

    def get_pin(self, component_id: str, pin_name: str) -> Optional[Pin]:
        """Get a specific pin from a component."""
        component = self.get_component(component_id)
        return component.pins.get(pin_name) if component else None

    def find_pwm_capable_pins(self, component_id: str) -> list[Pin]:
        """Find all PWM-capable pins on a component."""
        component = self.get_component(component_id)
        if not component:
            return []
        return [pin for pin in component.pins.values() if pin.is_pwm_capable]

    def find_adc_capable_pins(self, component_id: str) -> list[Pin]:
        """Find all ADC-capable pins on a component."""
        component = self.get_component(component_id)
        if not component:
            return []
        return [pin for pin in component.pins.values() if pin.is_adc_capable]

    def get_connections_for_pin(self, component_id: str, pin_name: str) -> list[CircuitConnection]:
        """Get all connections involving a specific pin."""
        return [
            conn
            for conn in self.connections
            if (conn.from_component == component_id and conn.from_pin == pin_name)
            or (conn.to_component == component_id and conn.to_pin == pin_name)
        ]

    def to_ascii_diagram(self) -> str:
        """Generate an ASCII representation of the circuit."""
        lines = [f"Circuit: {self.name}", "=" * 50]

        for comp_id, spec in self.components.items():
            lines.append(f"\n[{comp_id}] {spec.name} ({spec.component_type.value})")
            if spec.voltage:
                lines.append(f"  Voltage: {spec.voltage}V")
            if spec.current_limit:
                lines.append(f"  Current Limit: {spec.current_limit}A")
            if spec.power_rating:
                lines.append(f"  Power Rating: {spec.power_rating}W")

        lines.append("\nConnections:")
        for conn in self.connections:
            lines.append(f"  {conn}")

        return "\n".join(lines)