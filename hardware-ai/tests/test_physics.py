"""
Tests for HardwareAI physics engine.
"""

import pytest
from hardware_ai.core.physics import PhysicsEngine, ElectricalValues


class TestOhmsLaw:
    def test_voltage_from_current_and_resistance(self):
        result = PhysicsEngine.ohms_law(current=0.005, resistance=1000.0)
        assert result.voltage == pytest.approx(5.0)
        assert result.current == pytest.approx(0.005)
        assert result.resistance == pytest.approx(1000.0)
        assert result.power == pytest.approx(0.025)

    def test_current_from_voltage_and_resistance(self):
        result = PhysicsEngine.ohms_law(voltage=5.0, resistance=1000.0)
        assert result.current == pytest.approx(0.005)
        assert result.power == pytest.approx(0.025)

    def test_resistance_from_voltage_and_current(self):
        result = PhysicsEngine.ohms_law(voltage=5.0, current=0.005)
        assert result.resistance == pytest.approx(1000.0)

    def test_insufficient_parameters_raises(self):
        with pytest.raises(ValueError):
            PhysicsEngine.ohms_law(voltage=5.0)

    def test_power_i2r(self):
        p = PhysicsEngine.power_formula_i2r(0.01, 1000.0)
        assert p == pytest.approx(0.1)

    def test_power_v2r(self):
        p = PhysicsEngine.power_formula_v2r(5.0, 1000.0)
        assert p == pytest.approx(0.025)


class TestResistanceCombinations:
    def test_series_resistance(self):
        total = PhysicsEngine.series_resistance(100.0, 200.0, 300.0)
        assert total == pytest.approx(600.0)

    def test_parallel_resistance_two(self):
        total = PhysicsEngine.parallel_resistance(100.0, 200.0)
        # 1/R = 1/100 + 1/200 = 0.015 → R ≈ 66.67
        assert total == pytest.approx(66.66666667, abs=0.01)

    def test_parallel_resistance_three(self):
        total = PhysicsEngine.parallel_resistance(100.0, 200.0, 300.0)
        assert total == pytest.approx(54.54, abs=0.01)

    def test_parallel_with_zero_short_circuit(self):
        total = PhysicsEngine.parallel_resistance(100.0, 0.0)
        assert total == pytest.approx(0.0)

    def test_series_empty_raises(self):
        with pytest.raises(ValueError):
            PhysicsEngine.series_resistance()

    def test_parallel_empty_raises(self):
        with pytest.raises(ValueError):
            PhysicsEngine.parallel_resistance()


class TestVoltageDivision:
    def test_voltage_divider(self):
        v_out, v_r1 = PhysicsEngine.voltage_divider(12.0, 1000.0, 2000.0)
        assert v_out == pytest.approx(8.0)
        assert v_r1 == pytest.approx(4.0)

    def test_voltage_divider_equal_resistors(self):
        v_out, v_r1 = PhysicsEngine.voltage_divider(10.0, 1000.0, 1000.0)
        assert v_out == pytest.approx(5.0)


class TestLogicLevelCompatibility:
    def test_same_voltage_compatible(self):
        assert PhysicsEngine.check_logic_level_compatible(3.3, 3.3) is True

    def test_3v3_to_5v_not_directly_compatible(self):
        # 3.3V typically can't reliably drive 5V logic
        # But allow slightly higher (within 1.8V difference)
        assert PhysicsEngine.check_logic_level_compatible(3.3, 5.0) is False

    def test_5v_to_3v3_drive(self):
        # 5V can drive 3.3V input (with care)
        assert PhysicsEngine.check_logic_level_compatible(5.0, 3.3) is True


class TestPowerDissipation:
    def test_power_safe(self):
        result = PhysicsEngine.power_dissipation_check(0.1, 0.5)
        assert result["status"] == "safe"

    def test_power_caution(self):
        result = PhysicsEngine.power_dissipation_check(0.3, 0.5)
        assert result["status"] == "caution"

    def test_power_danger(self):
        result = PhysicsEngine.power_dissipation_check(0.8, 0.5)
        assert result["status"] == "danger"