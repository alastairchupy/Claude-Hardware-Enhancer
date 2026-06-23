"""
Component registry and database for HardwareAI.
Provides access to all known hardware components with their electrical specifications.
"""

from __future__ import annotations

from typing import Optional

from hardware_ai.core.circuit import ComponentSpec, ComponentType, Pin
from hardware_ai.components.esp32 import get_esp32_spec
from hardware_ai.components.arduino import get_arduino_uno_spec
from hardware_ai.components.raspberry_pi_pico import get_pico_spec
from hardware_ai.components.motors import get_my6812_spec, MOTOR_DATABASE
from hardware_ai.components.motor_drivers import get_hw039_spec, DRIVER_DATABASE
from hardware_ai.components.sensors import SENSOR_DATABASE
from hardware_ai.components.power_supplies import POWER_SUPPLY_DATABASE
from hardware_ai.components.resistors import RESISTOR_STANDARD_VALUES


class ComponentRegistry:
    """
    Registry of all known hardware components.

    Provides lookup by name/model and category filtering.
    """

    def __init__(self):
        self._components: dict[str, ComponentSpec] = {}
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the component database with known components."""
        # Microcontrollers
        self.register(get_esp32_spec(), "esp32", "esp32_devkit")
        self.register(get_arduino_uno_spec(), "arduino", "arduino_uno", "uno")
        self.register(get_pico_spec(), "pico", "rpi_pico", "raspberry_pi_pico", "rp2040")

        # Motors
        for name, spec_fn in MOTOR_DATABASE.items():
            self.register(spec_fn())

        # Motor drivers
        for name, spec_fn in DRIVER_DATABASE.items():
            self.register(spec_fn())

        # Power supplies
        for name, spec in POWER_SUPPLY_DATABASE.items():
            self.register(spec)

        # Standard resistor values
        # (not individual components, just the standard series)

    def register(self, spec: ComponentSpec, *extra_keys: str) -> None:
        """Register a component in the database with standard keys + optional aliases."""
        for key in extra_keys:
            self._components[key.lower().replace("-", "_").replace(" ", "_")] = spec
        key = f"{spec.manufacturer}_{spec.model}".lower().replace("-", "_").replace(" ", "_")
        self._components[key] = spec
        self._components[spec.model.lower().replace("-", "_").replace(" ", "_")] = spec
        self._components[spec.name.lower().replace("-", "_").replace(" ", "_")] = spec

    def get(self, name: str) -> Optional[ComponentSpec]:
        """Get a component by name (case-insensitive)."""
        key = name.lower().replace("-", "_").replace(" ", "_")
        return self._components.get(key)

    def search(self, query: str) -> list[ComponentSpec]:
        """Search components by name or model substring."""
        query_lower = query.lower()
        return [
            spec
            for spec in self._components.values()
            if query_lower in spec.name.lower() or query_lower in spec.model.lower()
        ]

    def by_type(self, component_type: ComponentType) -> list[ComponentSpec]:
        """Get all components of a specific type."""
        return [spec for spec in self._components.values() if spec.component_type == component_type]

    def list_all(self) -> list[ComponentSpec]:
        """List all registered components."""
        return list(self._components.values())

    def list_by_category(self) -> dict[ComponentType, list[ComponentSpec]]:
        """List components grouped by type."""
        by_type: dict[ComponentType, list[ComponentSpec]] = {}
        for spec in self._components.values():
            if spec.component_type not in by_type:
                by_type[spec.component_type] = []
            by_type[spec.component_type].append(spec)
        return by_type

    def summary(self) -> str:
        """Get a summary of all registered components."""
        by_category = self.list_by_category()
        lines = ["HardwareAI Component Database", "=" * 40]
        for ctype, components in by_category.items():
            lines.append(f"\n{ctype.value.upper()} ({len(components)}):")
            for comp in components:
                lines.append(f"  - {comp.name} ({comp.model})")
        return "\n".join(lines)