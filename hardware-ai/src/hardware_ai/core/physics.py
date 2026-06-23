"""
Electrical physics engine for HardwareAI.
Implements Ohm's Law, power calculations, and resistance combinations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class ElectricalValues:
    """Container for electrical values with units."""

    voltage: float  # Volts (V)
    current: float  # Amperes (A)
    resistance: float  # Ohms (Ω)
    power: float  # Watts (W)


class PhysicsEngine:
    """
    Physics engine implementing core electrical equations.

    Supports:
    - Ohm's Law: V = IR
    - Power: P = VI, P = I²R, P = V²/R
    - Series resistance: R_total = R1 + R2 + ... + Rn
    - Parallel resistance: 1/R_total = 1/R1 + 1/R2 + ... + 1/Rn
    - Voltage division
    - Current division
    - Power dissipation
    """

    # Common voltage standards (V)
    LOGIC_VOLTAGES = {
        "3.3V": 3.3,
        "5V": 5.0,
        "12V": 12.0,
        "1.8V": 1.8,
        "2.5V": 2.5,
        "48V": 48.0,
    }

    @staticmethod
    def ohms_law(voltage: float = None, current: float = None, resistance: float = None) -> ElectricalValues:
        """
        Calculate missing electrical value using Ohm's Law (V = IR).

        Args:
            voltage: Voltage in Volts
            current: Current in Amperes
            resistance: Resistance in Ohms

        Returns:
            ElectricalValues with all three calculated

        Raises:
            ValueError: If fewer than two values provided, or invalid values

        Example:
            >>> PhysicsEngine.ohms_law(voltage=5.0, resistance=1000.0)
            ElectricalValues(voltage=5.0, current=0.005, resistance=1000.0, power=0.025)
        """
        provided = sum(1 for v in [voltage, current, resistance] if v is not None)
        if provided < 2:
            raise ValueError("At least two of voltage, current, or resistance must be provided")

        if voltage is not None and resistance is not None:
            current = voltage / resistance
        elif voltage is not None and current is not None:
            resistance = voltage / current
        elif current is not None and resistance is not None:
            voltage = current * resistance
        else:
            raise ValueError("Could not calculate - check inputs")

        power = PhysicsEngine.power_formula_iv(voltage, current)

        return ElectricalValues(
            voltage=float(voltage),
            current=float(current),
            resistance=float(resistance),
            power=float(power),
        )

    @staticmethod
    def power_formula_iv(voltage: float, current: float) -> float:
        """Calculate power using P = VI."""
        return voltage * current

    @staticmethod
    def power_formula_i2r(current: float, resistance: float) -> float:
        """Calculate power using P = I²R."""
        return current**2 * resistance

    @staticmethod
    def power_formula_v2r(voltage: float, resistance: float) -> float:
        """Calculate power using P = V²/R."""
        return voltage**2 / resistance

    @classmethod
    def series_resistance(cls, *resistances: float) -> float:
        """
        Calculate total resistance of resistors in series.

        R_total = R1 + R2 + ... + Rn

        Args:
            *resistances: Individual resistance values in Ohms

        Returns:
            Total resistance in Ohms

        Example:
            >>> PhysicsEngine.series_resistance(100, 200, 300)
            600.0
        """
        if not resistances:
            raise ValueError("At least one resistance value required")
        return sum(resistances)

    @classmethod
    def parallel_resistance(cls, *resistances: float) -> float:
        """
        Calculate total resistance of resistors in parallel.

        1/R_total = 1/R1 + 1/R2 + ... + 1/Rn

        Args:
            *resistances: Individual resistance values in Ohms

        Returns:
            Total resistance in Ohms

        Example:
            >>> PhysicsEngine.parallel_resistance(100, 200, 300)
            54.54...
        """
        if not resistances:
            raise ValueError("At least one resistance value required")

        # Check for zero resistance (short circuit)
        if 0.0 in resistances:
            return 0.0

        reciprocal_sum = sum(1.0 / r for r in resistances if r > 0)
        if reciprocal_sum == 0:
            return float("inf")
        return 1.0 / reciprocal_sum

    @staticmethod
    def voltage_divider(v_in: float, r1: float, r2: float) -> tuple[float, float]:
        """
        Calculate voltage divider output.

        Args:
            v_in: Input voltage
            r1: Upper resistor (Ω)
            r2: Lower resistor (Ω)

        Returns:
            (V_out, voltage across R2), (V_r1, voltage across R1)

        Example:
            >>> PhysicsEngine.voltage_divider(12.0, 1000.0, 2000.0)
            (8.0, 4.0)
        """
        r_total = r1 + r2
        i = v_in / r_total
        v_r1 = i * r1
        v_r2 = i * r2
        return v_r2, v_r1

    @staticmethod
    def current_divider(i_total: float, r_branch: float, r_total: float) -> float:
        """
        Calculate current through one branch of a parallel divider.

        I_branch = I_total * (R_total / R_branch)

        Args:
            i_total: Total current entering parallel network
            r_branch: Resistance of target branch
            r_total: Equivalent parallel resistance

        Returns:
            Current through the branch
        """
        return i_total * (r_total / r_branch)

    @classmethod
    def check_voltage_compatible(cls, v1: float, v2: float, tolerance: float = 0.1) -> bool:
        """
        Check if two voltages are compatible (within tolerance).

        Args:
            v1: First voltage
            v2: Second voltage
            tolerance: Acceptable difference ratio (default 10%)

        Returns:
            True if compatible
        """
        if v1 == v2:
            return True
        diff = abs(v1 - v2)
        avg = (v1 + v2) / 2
        return (diff / avg) <= tolerance if avg > 0 else False

    @classmethod
    def check_logic_level_compatible(cls, source_v: float, target_v: float) -> bool:
        """
        Check if source logic voltage can drive target (3.3V → 5V, etc).

        Args:
            source_v: Source logic voltage
            target_v: Target logic voltage

        Returns:
            True if source can drive target
        """
        # 3.3V can drive 3.3V systems
        if abs(source_v - target_v) < 0.1:
            return True
        # Higher voltage source can often drive lower voltage target (with caution)
        if source_v > target_v:
            # Allow if not more than one logic level apart
            return (source_v - target_v) <= 1.8
        return False

    @staticmethod
    def power_dissipation_check(power: float, component_rating: float) -> dict:
        """
        Check if power dissipation is within component ratings.

        Args:
            power: Actual power dissipation (W)
            component_rating: Component's power rating (W)

        Returns:
            Dict with status and derating percentage
        """
        if power <= component_rating * 0.5:
            status = "safe"
        elif power <= component_rating * 0.75:
            status = "caution"
        elif power <= component_rating:
            status = "acceptable"
        elif power <= component_rating * 1.25:
            status = "warning"
        else:
            status = "danger"

        derating = (power / component_rating) * 100 if component_rating > 0 else float("inf")
        return {
            "status": status,
            "derating_percent": round(derating, 1),
            "power_w": round(power, 4),
            "rating_w": component_rating,
        }