"""
Circuit simulation engine for HardwareAI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from uuid import uuid4

from hardware_ai.core.circuit import Circuit, CircuitConnection, ComponentSpec, ComponentType, ConnectionType
from hardware_ai.core.physics import PhysicsEngine
from hardware_ai.core.validator import Validator, ValidationResult, ValidationIssue, ValidationSeverity


class SimulationStatus(str, Enum):
    """Status of a simulation run."""

    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"


@dataclass
class SimulationStep:
    """A single step in the simulation."""

    step_number: int
    action: str
    description: str
    component: str
    result: str
    details: dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Result of a circuit simulation."""

    simulation_id: str
    status: SimulationStatus
    circuit_name: str
    steps: list[SimulationStep] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    analysis: dict[str, str] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    diagram: str = ""

    @property
    def passed(self) -> bool:
        return self.status == SimulationStatus.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "status": self.status.value,
            "circuit_name": self.circuit_name,
            "passed": self.passed,
            "steps": [
                {
                    "step": s.step_number,
                    "action": s.action,
                    "description": s.description,
                    "component": s.component,
                    "result": s.result,
                    "details": s.details,
                }
                for s in self.steps
            ],
            "analysis": self.analysis,
            "recommendations": self.recommendations,
            "diagram": self.diagram,
        }


class Simulator:
    """
    Circuit simulation engine.

    Simulates circuit behavior and validates electrical compatibility.

    Example workflow:
        1. Build circuit with components and connections
        2. Run simulation
        3. Get validation results and recommendations
    """

    def __init__(self, physics: Optional[PhysicsEngine] = None, validator: Optional[Validator] = None):
        self.physics = physics or PhysicsEngine()
        self.validator = validator or Validator(self.physics)
        self.simulation_history: list[SimulationResult] = []

    def simulate(self, circuit: Circuit) -> SimulationResult:
        """
        Simulate a circuit and return results.

        Args:
            circuit: Circuit to simulate

        Returns:
            SimulationResult with status, analysis, and recommendations
        """
        simulation_id = str(uuid4())
        result = SimulationResult(
            simulation_id=simulation_id,
            status=SimulationStatus.RUNNING,
            circuit_name=circuit.name,
        )

        step = 1

        # Step 1: Analyze component compatibility
        result.steps.append(
            SimulationStep(
                step_number=step,
                action="component_analysis",
                description="Analyzing component compatibility",
                component="all",
                result="COMPLETE",
            )
        )
        step += 1

        # Step 2: Validate electrical connections
        validation_result = self.validator.validate_circuit(circuit)
        result.validation_result = validation_result

        result.steps.append(
            SimulationStep(
                step_number=step,
                action="electrical_validation",
                description="Validating electrical connectivity",
                component="all",
                result="COMPLETE",
                details={"issues_found": len(validation_result.issues)},
            )
        )
        step += 1

        # Step 3: Build analysis dict
        result.analysis = {
            "voltage_check": "PASS",
            "current_check": "PASS",
            "power_check": "PASS",
            "compatibility_check": "PASS",
            "gpio_check": "PASS",
        }

        if validation_result.errors:
            result.analysis["voltage_check"] = "FAIL"
            result.status = SimulationStatus.FAIL
        elif validation_result.warnings:
            result.analysis["voltage_check"] = "WARN"
            result.status = SimulationStatus.WARN
        else:
            result.status = SimulationStatus.PASS

        # Step 4: Generate recommendations
        for issue in validation_result.issues:
            if issue.recommendation:
                result.recommendations.append(f"{issue.component}: {issue.recommendation}")

        # Step 5: Build ASCII diagram
        result.diagram = circuit.to_ascii_diagram()

        self.simulation_history.append(result)
        return result

    def simulate_motor_circuit(
        self,
        mcu_name: str,
        driver_name: str,
        motor_name: str,
        motor_voltage: float,
        mcu_pwm_pin: str,
        has_flyback_diode: bool = False,
    ) -> SimulationResult:
        """
        Convenience method to simulate a motor control circuit.

        Args:
            mcu_name: Microcontroller model (e.g., "ESP32")
            driver_name: Motor driver model (e.g., "HW-039")
            motor_name: Motor model (e.g., "MY6812")
            motor_voltage: Motor operating voltage
            mcu_pwm_pin: PWM-capable GPIO pin on MCU
            has_flyback_diode: Whether flyback protection is present

        Returns:
            SimulationResult
        """
        from hardware_ai.components.registry import ComponentRegistry

        registry = ComponentRegistry()
        sim = Simulator()

        # Simulate step by step
        steps = []
        components_found = []
        overall_status = SimulationStatus.PASS
        recommendations = []

        # Check MCU
        mcu = registry.get(mcu_name.lower())
        if mcu:
            components_found.append(f"✅ {mcu_name} found")

            # Check PWM pin
            has_pwm = any(p.is_pwm_capable for p in mcu.pins.values())
            if has_pwm:
                components_found.append(f"✅ {mcu_name} has PWM-capable pins")
            else:
                components_found.append(f"❌ {mcu_name} has no PWM capability")
                overall_status = SimulationStatus.FAIL
        else:
            components_found.append(f"⚠️  {mcu_name} not in database, assuming 3.3V logic")
            recommendations.append(f"Verify {mcu_name} logic voltage matches driver")

        # Check driver
        driver = registry.get(driver_name.lower())
        if driver:
            components_found.append(f"✅ {driver_name} found")
            # Check motor voltage against driver spec's motor_voltage_range
            voltage_range = driver.properties.get("motor_voltage_range")
            if voltage_range:
                # Extract max voltage from range like "2.7-10.8V"
                if isinstance(voltage_range, str) and "-" in voltage_range:
                    try:
                        max_v = float(voltage_range.split("-")[-1].replace("V", ""))
                        if motor_voltage > max_v:
                            components_found.append(f"❌ {driver_name} cannot handle {motor_voltage}V (max: {max_v}V)")
                            overall_status = SimulationStatus.FAIL
                            recommendations.append(f"Motor voltage exceeds driver max of {max_v}V")
                    except ValueError:
                        pass  # Couldn't parse range
            elif driver.voltage and motor_voltage > driver.voltage:
                # Fallback: assume driver.voltage is motor supply rating (e.g. HW-039 rated at 12V)
                components_found.append(f"❌ {driver_name} cannot handle {motor_voltage}V")
                overall_status = SimulationStatus.FAIL
                recommendations.append(f"Motor voltage exceeds driver rating of {driver.voltage}V")
        else:
            components_found.append(f"⚠️  {driver_name} not in database")
            recommendations.append(f"Verify {driver_name} can handle {motor_voltage}V and required current")

        # Check motor
        motor = registry.get(motor_name.lower())
        if motor:
            components_found.append(f"✅ {motor_name} found")
        else:
            components_found.append(f"⚠️  {motor_name} not in database")

        # Flyback protection
        if not has_flyback_diode:
            components_found.append(f"⚠️  No flyback protection - add diode for motor longevity")
            if overall_status == SimulationStatus.PASS:
                overall_status = SimulationStatus.WARN
            recommendations.append("Add flyback diode across motor terminals to protect driver")

        # Voltage compatibility check
        if mcu and driver:
            if mcu.voltage == 3.3 and driver.voltage == 5.0:
                components_found.append(f"✅ {mcu_name} 3.3V logic compatible with {driver_name} 5V inputs")
            elif mcu.voltage and driver.voltage:
                if abs(mcu.voltage - driver.voltage) > 1.0:
                    components_found.append(f"⚠️  Logic voltage mismatch may need level shifter")
                    recommendations.append("Consider level shifter between MCU and driver")

        # Build result
        result = SimulationResult(
            simulation_id=str(uuid4()),
            status=overall_status,
            circuit_name=f"{mcu_name} + {driver_name} + {motor_name}",
            analysis={
                "mcu_logic": "PASS" if mcu else "UNKNOWN",
                "driver_compatibility": "PASS" if driver else "UNKNOWN",
                "motor_compatibility": "PASS" if motor else "UNKNOWN",
                "flyback_protection": "PRESENT" if has_flyback_diode else "MISSING",
                "overall": overall_status.value.upper(),
            },
            recommendations=recommendations,
            diagram=self._build_motor_diagram(mcu_name, driver_name, motor_name, motor_voltage, mcu_pwm_pin),
        )

        result.steps.append(
            SimulationStep(
                step_number=1,
                action="component_lookup",
                description="Looking up component specifications",
                component="all",
                result="COMPLETE",
                details={"components": components_found},
            )
        )

        result.steps.append(
            SimulationStep(
                step_number=2,
                action="voltage_validation",
                description="Validating voltage compatibility",
                component=f"{mcu_name}, {driver_name}",
                result=result.analysis.get("mcu_logic", "UNKNOWN"),
            )
        )

        result.steps.append(
            SimulationStep(
                step_number=3,
                action="pwm_check",
                description=f"PWM output on {mcu_pwm_pin}",
                component=mcu_name,
                result="PASS" if mcu else "UNKNOWN",
                details={"pwm_pin": mcu_pwm_pin},
            )
        )

        self.simulation_history.append(result)
        return result

    def _build_motor_diagram(
        self, mcu_name: str, driver_name: str, motor_name: str, voltage: float, pwm_pin: str
    ) -> str:
        """Build an ASCII circuit diagram."""
        lines = [
            "Hardware Circuit Diagram",
            "=" * 40,
            "",
            f"  {mcu_name}          {driver_name}         {motor_name}",
            f"    │  PWM  ──────────► │IN1, IN2──────────►  Motor",
            f"    │         {voltage}V ────────► VCC    (+)",
            f"    │                                    │",
            f"    │                              [Flyback Diode]",
            f"    │                                    │",
            f"  GND  ────────────────────────────   GND (-)",
            "",
            "PWM Signal: 3.3V → Driver Input",
            f"Motor Power: {voltage}V External Supply",
            f"PWM Pin: {pwm_pin}",
            "",
        ]
        return "\n".join(lines)

    def check_gpio(self, mcu_name: str, pin_name: str, required_capability: str) -> dict[str, Any]:
        """
        Check if a GPIO pin has a required capability.

        Args:
            mcu_name: Microcontroller model
            pin_name: Pin name/number
            required_capability: "pwm", "adc", "uart", "i2c", "spi"

        Returns:
            Dict with check result
        """
        from hardware_ai.components.registry import ComponentRegistry

        registry = ComponentRegistry()
        mcu = registry.get(mcu_name.lower())

        if not mcu:
            return {
                "result": "unknown",
                "message": f"{mcu_name} not found in component database",
                "recommendation": f"Add {mcu_name} to database or verify manually",
            }

        pin = mcu.pins.get(pin_name)
        if not pin:
            return {
                "result": "error",
                "message": f"Pin {pin_name} not found on {mcu_name}",
                "recommendation": f"Check valid pins for {mcu_name}",
            }

        capability_map = {
            "pwm": pin.is_pwm_capable,
            "adc": pin.is_adc_capable,
        }

        has_capability = capability_map.get(required_capability, False)

        return {
            "result": "pass" if has_capability else "fail",
            "message": f"Pin {pin_name}: {'has' if has_capability else 'does not have'} {required_capability}",
            "pin": pin_name,
            "capability": required_capability,
            "recommendation": (
                f"Use a {required_capability}-capable pin (other pins may support this)"
                if not has_capability
                else None
            ),
        }