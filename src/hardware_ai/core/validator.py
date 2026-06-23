"""
Electrical validation rules for HardwareAI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from hardware_ai.core.circuit import Circuit, ComponentSpec, ComponentType, Pin, CircuitConnection, ConnectionType
from hardware_ai.core.physics import PhysicsEngine


class ValidationSeverity(str, Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PASS = "pass"


@dataclass
class ValidationIssue:
    """A single validation finding."""

    severity: ValidationSeverity
    component: str
    message: str
    detail: str = ""
    recommendation: str = ""
    pin_name: Optional[str] = None

    def __str__(self) -> str:
        prefix = {
            ValidationSeverity.ERROR: "❌ ERROR",
            ValidationSeverity.WARNING: "⚠️  WARNING",
            ValidationSeverity.INFO: "ℹ️  INFO",
            ValidationSeverity.PASS: "✅ PASS",
        }[self.severity]
        return f"{prefix}: {self.component} — {self.message}"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    issues: list[ValidationIssue] = field(default_factory=list)
    checks_performed: list[str] = field(default_factory=list)
    overall_status: ValidationSeverity = ValidationSeverity.PASS

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add an issue and recalculate overall status."""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.overall_status = ValidationSeverity.ERROR
        elif issue.severity == ValidationSeverity.WARNING and self.overall_status != ValidationSeverity.ERROR:
            self.overall_status = ValidationSeverity.WARNING

    def add_check(self, check_name: str) -> None:
        """Record that a check was performed."""
        self.checks_performed.append(check_name)

    @property
    def passed(self) -> bool:
        return self.overall_status == ValidationSeverity.PASS

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def summary(self) -> str:
        """Generate a human-readable summary."""
        status_icon = "✅" if self.passed else "❌"
        lines = [f"\n{status_icon} Validation Result: {self.overall_status.value.upper()}"]

        if self.errors:
            lines.append("\nErrors:")
            for issue in self.errors:
                lines.append(f"  {issue}")

        if self.warnings:
            lines.append("\nWarnings:")
            for issue in self.warnings:
                lines.append(f"  {issue}")

        if not self.errors and not self.warnings:
            lines.append("  No issues found.")

        return "\n".join(lines)


class Validator:
    """
    Validates circuits for electrical compatibility and correctness.

    Checks:
    - Voltage compatibility between connected components
    - Current limits and power consumption
    - GPIOpin capabilities (PWM, ADC, etc.)
    - Communication bus conflicts (I2C, SPI, etc.)
    - Short circuit risks
    """

    def __init__(self, physics: Optional[PhysicsEngine] = None):
        self.physics = physics or PhysicsEngine()
        self.validation_history: list[ValidationResult] = []

    def validate_circuit(self, circuit: Circuit) -> ValidationResult:
        """Run all validation checks on a circuit."""
        result = ValidationResult()

        # Run all checks
        self._check_voltage_compatibility(circuit, result)
        self._check_current_limits(circuit, result)
        self._check_power_consumption(circuit, result)
        self._check_gpio_capabilities(circuit, result)
        self._check_communication_conflicts(circuit, result)
        self._check_short_circuits(circuit, result)
        self._check_ground_loops(circuit, result)

        self.validation_history.append(result)
        return result

    def _check_voltage_compatibility(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check that connected components have compatible voltage levels."""
        result.add_check("voltage_compatibility")

        power_pins: dict[str, list[tuple[str, Pin]]] = {}  # voltage -> [(component, pin)]

        for conn in circuit.connections:
            if conn.connection_type != ConnectionType.POWER:
                continue

            from_pin = circuit.get_pin(conn.from_component, conn.from_pin)
            to_pin = circuit.get_pin(conn.to_component, conn.to_pin)

            if from_pin and to_pin and from_pin.voltage and to_pin.voltage:
                if not self.physics.check_logic_level_compatible(from_pin.voltage, to_pin.voltage):
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            component=conn.to_component,
                            message=f"Voltage mismatch on {conn.to_pin}",
                            detail=f"Connected {from_pin.voltage}V to {to_pin.voltage}V",
                            recommendation=f"Use a level shifter or ensure compatible logic voltages",
                            pin_name=conn.to_pin,
                        )
                    )

    def _check_current_limits(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check that current draw doesn't exceed component limits."""
        result.add_check("current_limits")

        for conn in circuit.connections:
            if conn.connection_type == ConnectionType.POWER:
                target_comp = circuit.get_component(conn.to_component)
                if target_comp and target_comp.current_limit:
                    # In a real implementation, we'd calculate actual current draw
                    # For now, this is a placeholder that checks if limits are defined
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.INFO,
                            component=target_comp.name,
                            message=f"Current limit defined: {target_comp.current_limit}A",
                            detail="Ensure load current stays below this limit",
                            pin_name=conn.to_pin,
                        )
                    )

    def _check_power_consumption(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check total power consumption against power supply capacity."""
        result.add_check("power_consumption")

        total_power = 0.0
        power_supplies = [c for c in circuit.components.values() if c.component_type == ComponentType.POWER_SUPPLY]

        for comp in circuit.components.values():
            if comp.power_rating:
                total_power += comp.power_rating * 0.1  # Assume 10% average utilization

        for supply in power_supplies:
            if supply.current_limit and supply.voltage:
                supply_power = supply.voltage * supply.current_limit
                if total_power > supply_power:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            component=supply.name,
                            message="Power consumption may exceed supply capacity",
                            detail=f"Estimated draw: {total_power:.2f}W, Supply capacity: {supply_power:.2f}W",
                            recommendation="Use a higher capacity power supply or reduce load",
                        )
                    )

    def _check_gpio_capabilities(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check that GPIO pins are used correctly (PWM, ADC, etc.)."""
        result.add_check("gpio_capabilities")

        for conn in circuit.connections:
            if conn.connection_type == ConnectionType.PWM:
                dest_pin = circuit.get_pin(conn.to_component, conn.to_pin)
                if dest_pin and not dest_pin.is_pwm_capable:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            component=conn.to_component,
                            message=f"Pin {conn.to_pin} cannot output PWM",
                            detail="This pin does not support PWM functionality",
                            recommendation=f"Use a PWM-capable pin (check spec for {conn.to_component})",
                            pin_name=conn.to_pin,
                        )
                    )

            elif conn.connection_type == ConnectionType.ANALOG:
                dest_pin = circuit.get_pin(conn.to_component, conn.to_pin)
                if dest_pin and not dest_pin.is_adc_capable:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            component=conn.to_component,
                            message=f"Pin {conn.to_pin} cannot read analog",
                            detail="This pin does not have ADC capability",
                            recommendation=f"Use an ADC-capable pin",
                            pin_name=conn.to_pin,
                        )
                    )

    def _check_communication_conflicts(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check for I2C/SPI/UART bus conflicts."""
        result.add_check("communication_conflicts")

        i2c_connections: list[CircuitConnection] = []
        spi_connections: list[CircuitConnection] = []
        uart_connections: list[CircuitConnection] = []

        for conn in circuit.connections:
            if conn.connection_type == ConnectionType.I2C:
                i2c_connections.append(conn)
            elif conn.connection_type == ConnectionType.SPI:
                spi_connections.append(conn)
            elif conn.connection_type == ConnectionType.UART:
                uart_connections.append(conn)

        # Check for multiple masters on same I2C bus
        i2c_pairs = [(c.from_component, c.to_component) for c in i2c_connections]
        for i, (a, b) in enumerate(i2c_pairs):
            for j, (c, d) in enumerate(i2c_pairs):
                if i < j and {a, b} == {c, d}:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            component=f"I2C bus {a}-{b}",
                            message="Duplicate I2C connection detected",
                            recommendation="Verify this is intentional",
                        )
                    )

    def _check_short_circuits(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check for potential short circuit conditions."""
        result.add_check("short_circuits")

        for comp_id, comp in circuit.components.items():
            # Check for directly connected power and ground
            for conn in circuit.connections:
                if conn.connection_type == ConnectionType.POWER:
                    to_comp = circuit.get_component(conn.to_component)
                    if to_comp and to_comp.component_type == ComponentType.POWER_SUPPLY:
                        # Power to power supply - check direction
                        from_pin = circuit.get_pin(conn.from_component, conn.from_pin)
                        if from_pin and from_pin.direction == "output":
                            result.add_issue(
                                ValidationIssue(
                                    severity=ValidationSeverity.ERROR,
                                    component=comp_id,
                                    message="Potential short circuit - power output to power supply input",
                                    recommendation="Reverse connection direction",
                                )
                            )

    def _check_ground_loops(self, circuit: Circuit, result: ValidationResult) -> None:
        """Check for problematic ground loops."""
        result.add_check("ground_loops")

        # In a real implementation, this would check for multiple ground paths
        # causing potential ground loops. For now, minimal check.
        pass

    def validate_motor_circuit(
        self,
        mcu_spec: ComponentSpec,
        driver_spec: ComponentSpec,
        motor_spec: ComponentSpec,
        motor_voltage: float,
        has_flyback_diode: bool = False,
    ) -> ValidationResult:
        """
        Convenience method to validate a motor control circuit.

        Args:
            mcu_spec: Microcontroller specification
            driver_spec: Motor driver specification
            motor_spec: Motor specification
            motor_voltage: Motor operating voltage
            has_flyback_diode: Whether flyback protection is present

        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult()

        # Check MCU logic voltage vs driver
        if mcu_spec.voltage and driver_spec.voltage:
            if not self.physics.check_voltage_compatible(mcu_spec.voltage, driver_spec.voltage):
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=driver_spec.name,
                        message="Logic voltage mismatch",
                        detail=f"MCU: {mcu_spec.voltage}V, Driver: {driver_spec.voltage}V",
                        recommendation="Ensure voltage compatibility or use level shifter",
                    )
                )

        # Check motor voltage vs driver capability
        if driver_spec.voltage and motor_voltage > driver_spec.voltage:
            result.add_issue(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    component=motor_spec.name,
                    message=f"Motor voltage ({motor_voltage}V) exceeds driver capability ({driver_spec.voltage}V)",
                    recommendation="Use appropriate motor driver for voltage level",
                )
            )

        # Check driver current rating vs motor
        if driver_spec.current_limit and motor_spec.current_limit:
            if motor_spec.current_limit > driver_spec.current_limit:
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        component=driver_spec.name,
                        message=f"Motor current ({motor_spec.current_limit}A) exceeds driver rating ({driver_spec.current_limit}A)",
                        recommendation="Use higher current-rated motor driver",
                    )
                )

        # Flyback protection warning
        if not has_flyback_diode:
            result.add_issue(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    component=motor_spec.name,
                    message="No flyback protection detected",
                    detail="Inductive motor transients can damage driver",
                    recommendation="Add flyback diode across motor terminals",
                )
            )

        self.validation_history.append(result)
        return result