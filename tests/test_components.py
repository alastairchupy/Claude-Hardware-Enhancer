"""
Tests for HardwareAI component registry and component specs.
"""

import pytest
from hardware_ai.components.registry import ComponentRegistry
from hardware_ai.components.esp32 import get_esp32_spec
from hardware_ai.components.motors import MOTOR_DATABASE
from hardware_ai.components.motor_drivers import DRIVER_DATABASE


class TestComponentRegistry:
    def test_registry_initialized(self):
        registry = ComponentRegistry()
        # Should have at least microcontrollers + motors + drivers
        assert len(registry.list_all()) > 0

    def test_get_esp32(self):
        registry = ComponentRegistry()
        esp32 = registry.get("esp32")
        assert esp32 is not None
        assert esp32.name == "ESP32 DevKit V1"
        assert esp32.voltage == 3.3

    def test_get_case_insensitive(self):
        registry = ComponentRegistry()
        assert registry.get("ESP32") is not None
        assert registry.get("esp32") is not None
        assert registry.get("Esp32") is not None

    def test_get_motor_driver(self):
        registry = ComponentRegistry()
        driver = registry.get("hw-039")
        assert driver is not None
        assert driver.component_type.value == "motor_driver"

    def test_search(self):
        registry = ComponentRegistry()
        results = registry.search("motor")
        assert len(results) > 0

    def test_by_type(self):
        registry = ComponentRegistry()
        microcontrollers = registry.by_type("microcontroller")
        assert len(microcontrollers) > 0
        from hardware_ai.core.circuit import ComponentType
        assert all(c.component_type == ComponentType.MICROCONTROLLER for c in microcontrollers)


class TestESPPins:
    def test_esp32_pwm_pins(self):
        """ESP32 should have PWM-capable pins."""
        esp32 = get_esp32_spec()
        pwm_pins = [p for p in esp32.pins.values() if p.is_pwm_capable]
        assert len(pwm_pins) > 0

    def test_esp32_input_only_pins(self):
        """ESP32 GPIO34-39 should be input-only."""
        esp32 = get_esp32_spec()
        for pin_name in ["GPIO34", "GPIO35", "GPIO36", "GPIO37", "GPIO38", "GPIO39"]:
            pin = esp32.pins.get(pin_name)
            assert pin is not None
            assert pin.direction == "input" or pin.current_limit == 0
            assert not pin.is_pwm_capable, f"{pin_name} should not be PWM-capable"

    def test_esp32_gpio25_pwm_capable(self):
        """ESP32 GPIO25 should be PWM-capable."""
        esp32 = get_esp32_spec()
        pin = esp32.pins.get("GPIO25")
        assert pin is not None
        assert pin.is_pwm_capable


class TestMotorDatabase:
    def test_my6812_spec(self):
        from hardware_ai.components.motors import get_my6812_spec
        motor = get_my6812_spec()
        assert motor.name == "MY6812 Brushed DC Motor"
        assert motor.voltage == 12.0
        assert motor.current_limit == 2.5

    def test_motor_database_not_empty(self):
        assert len(MOTOR_DATABASE) > 0


class TestDriverDatabase:
    def test_hw039_spec(self):
        from hardware_ai.components.motor_drivers import get_hw039_spec
        driver = get_hw039_spec()
        assert driver.name == "HW-039 Motor Driver"
        assert driver.voltage == 12.0
        # Should have PWM-capable pins
        pwm_pins = [p for p in driver.pins.values() if p.is_pwm_capable]
        assert len(pwm_pins) > 0

    def test_driver_database_not_empty(self):
        assert len(DRIVER_DATABASE) > 0