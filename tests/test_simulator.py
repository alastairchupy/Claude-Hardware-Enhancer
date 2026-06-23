"""
Tests for HardwareAI simulator.
"""

import pytest
from hardware_ai.core.simulator import Simulator, SimulationStatus
from hardware_ai.components.registry import ComponentRegistry


class TestMotorCircuitSimulator:
    def test_simulate_esp32_hw039_my6812(self):
        """Test the classic ESP32 + HW-039 + MY6812 circuit."""
        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name="ESP32",
            driver_name="HW-039",
            motor_name="MY6812",
            motor_voltage=12.0,
            mcu_pwm_pin="GPIO25",
            has_flyback_diode=False,
        )

        assert result.simulation_id is not None
        assert result.status in [SimulationStatus.PASS, SimulationStatus.WARN]
        assert len(result.steps) > 0
        assert len(result.recommendations) >= 0
        assert result.diagram != ""

    def test_simulate_esp32_gpio34_pwm_fails(self):
        """GPIO34 is input-only on ESP32 — should error if used for PWM."""
        simulator = Simulator()
        result = simulator.check_gpio("ESP32", "GPIO34", "pwm")
        assert result["result"] == "fail"
        assert "cannot output PWM" in result["message"] or "does not have pwm" in result["message"]

    def test_simulate_esp32_gpio25_pwm_passes(self):
        """GPIO25 is PWM-capable on ESP32."""
        simulator = Simulator()
        result = simulator.check_gpio("ESP32", "GPIO25", "pwm")
        assert result["result"] == "pass"

    def test_simulate_arduino_uno(self):
        """Arduino Uno should work with motor drivers."""
        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name="Arduino Uno",
            driver_name="DRV8833",
            motor_name="MY6812",
            motor_voltage=6.0,  # DRV8833 supports up to 10.8V motor supply
            mcu_pwm_pin="D3",
            has_flyback_diode=False,
        )
        # Should pass with warnings from missing flyback protection
        assert result.status in [SimulationStatus.PASS, SimulationStatus.WARN]

    def test_unknown_mcu_returns_unknown(self):
        """Unknown MCU should return unknown status."""
        simulator = Simulator()
        result = simulator.check_gpio("FakeMCU", "GPIO1", "pwm")
        assert result["result"] == "unknown"


class TestCircuitRepresentation:
    def test_build_circuit_diagram(self):
        """Circuit diagram should be generated."""
        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name="ESP32",
            driver_name="HW-039",
            motor_name="MY6812",
            motor_voltage=12.0,
            mcu_pwm_pin="GPIO25",
        )
        assert "ESP32" in result.diagram
        assert "HW-039" in result.diagram
        assert "MY6812" in result.diagram
        assert "12" in result.diagram