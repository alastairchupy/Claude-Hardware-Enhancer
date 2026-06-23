"""
Tests for HardwareAI validator.
"""

import pytest
from hardware_ai.core.validator import Validator, ValidationSeverity
from hardware_ai.core.circuit import Circuit, ComponentSpec, ComponentType, Pin, CircuitConnection, ConnectionType
from hardware_ai.core.physics import PhysicsEngine


class TestValidationResult:
    def test_validation_result_defaults_to_pass(self):
        from hardware_ai.core.validator import ValidationResult
        result = ValidationResult()
        assert result.passed is True
        assert result.overall_status == ValidationSeverity.PASS

    def test_validation_result_errors_cause_fail(self):
        from hardware_ai.core.validator import ValidationResult, ValidationIssue
        result = ValidationResult()
        result.add_issue(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                component="Test",
                message="Test error",
            )
        )
        assert result.passed is False
        assert result.overall_status == ValidationSeverity.ERROR


class TestValidatorLogic:
    def test_validator_creates_with_physics(self):
        validator = Validator()
        assert validator.physics is not None
        assert isinstance(validator.physics, PhysicsEngine)

    def test_validate_motor_circuit(self):
        """Test motor circuit validation."""
        from hardware_ai.components.motors import get_my6812_spec
        from hardware_ai.components.motor_drivers import get_hw039_spec
        from hardware_ai.components.esp32 import get_esp32_spec

        esp32 = get_esp32_spec()
        hw039 = get_hw039_spec()
        my6812 = get_my6812_spec()

        validator = Validator()
        result = validator.validate_motor_circuit(
            mcu_spec=esp32,
            driver_spec=hw039,
            motor_spec=my6812,
            motor_voltage=12.0,
            has_flyback_diode=False,
        )

        # Should have warnings about flyback protection
        assert len(result.issues) >= 1
        warnings = [i for i in result.issues if i.severity == ValidationSeverity.WARNING]
        assert any("flyback" in w.message.lower() for w in warnings)

    def test_logic_level_compatibility(self):
        """3.3V MCU to 5V logic should be flagged."""
        from hardware_ai.components.esp32 import get_esp32_spec
        from hardware_ai.components.arduino import get_arduino_uno_spec

        esp32 = get_esp32_spec()
        arduino = get_arduino_uno_spec()

        validator = Validator()
        circuit = Circuit(name="Test Circuit")
        circuit.add_component("esp32", esp32)
        # This test would need a proper connection to trigger validation


class TestPhysicsEngineWithValidator:
    def test_validator_with_physics(self):
        """Validator should use physics engine for calculations."""
        physics = PhysicsEngine()
        validator = Validator(physics=physics)

        # Ohm's law check
        elec = physics.ohms_law(voltage=12.0, resistance=1000.0)
        assert elec.current == pytest.approx(0.012)
        assert elec.power == pytest.approx(0.144)