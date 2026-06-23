"""
Claude Code skill for HardwareAI.
Provides a /hardware-ai slash command for Claude Code.
"""

from hardware_ai.core.simulator import Simulator
from hardware_ai.components.registry import ComponentRegistry


def hardware_ai_skill(circuit_description: str) -> str:
    """
    HardwareAI skill for validating hardware designs.

    Usage in Claude Code:
        /hardware-ai simulate "ESP32 + HW-039 + MY6812 + 12V"

    Args:
        circuit_description: Circuit description string

    Returns:
        Formatted simulation result string
    """
    parts = [p.strip() for p in circuit_description.replace("+", ",").split(",")]

    mcu = parts[0] if len(parts) > 0 else None
    driver = parts[1] if len(parts) > 1 else None
    motor = parts[2] if len(parts) > 2 else None
    voltage = float(parts[3].replace("V", "").strip()) if len(parts) > 3 else 12.0

    if not driver or not motor:
        return (
            "❌ **HardwareAI**: Please specify a complete circuit\n\n"
            "Example: `/hardware-ai simulate ESP32 + HW-039 + MY6812 + 12V`\n\n"
            "Format: `<MCU> + <Driver> + <Motor> + <Voltage>`"
        )

    simulator = Simulator()
    result = simulator.simulate_motor_circuit(
        mcu_name=mcu,
        driver_name=driver,
        motor_name=motor,
        motor_voltage=voltage,
        mcu_pwm_pin="GPIO25",
        has_flyback_diode=False,
    )

    lines = [f"### 🖥️ HardwareAI Simulation Result\n"]
    lines.append(f"**Circuit:** {mcu} + {driver} + {motor} @ {voltage}V\n")

    # Status
    if result.passed:
        lines.append(f"**Status:** ✅ {result.status.value.upper()}")
    else:
        lines.append(f"**Status:** ❌ {result.status.value.upper()}")

    # Analysis table
    lines.append("\n| Check | Result |")
    lines.append("|-------|--------|")
    for check, res in result.analysis.items():
        icon = "✅" if res == "PASS" else ("⚠️" if res == "WARN" else "❌")
        lines.append(f"| {check.replace('_', ' ').title()} | {icon} {res} |")

    # Recommendations
    if result.recommendations:
        lines.append("\n**Recommendations:**")
        for rec in result.recommendations:
            lines.append(f"- ⚠️ {rec}")

    # Circuit diagram
    if result.diagram:
        lines.append(f"\n```\n{result.diagram}\n```")

    return "\n".join(lines)


def hardware_ai_validate(mcu: str, driver: str, motor: str, voltage: float = 12.0) -> str:
    """
    HardwareAI validation skill.

    Usage:
        /hardware-ai validate --mcu ESP32 --driver HW-039 --motor MY6812 --voltage 12

    Returns:
        Formatted validation result
    """
    simulator = Simulator()
    result = simulator.simulate_motor_circuit(
        mcu_name=mcu,
        driver_name=driver,
        motor_name=motor,
        motor_voltage=voltage,
        mcu_pwm_pin="GPIO25",
        has_flyback_diode=False,
    )

    lines = [f"### 🔍 HardwareAI Validation\n"]
    lines.append(f"**Design:** {mcu} → {driver} → {motor} @ {voltage}V\n")

    for check, res in result.analysis.items():
        color = "green" if res == "PASS" else ("yellow" if res != "FAIL" else "red")
        lines.append(f"- **{check.replace('_', ' ').title()}**: {res}")

    for issue in result.validation_result.issues if result.validation_result else []:
        lines.append(f"  - {issue}")

    return "\n".join(lines)


def hardware_ai_check_gpio(mcu: str, pin: str, capability: str = "pwm") -> str:
    """
    HardwareAI GPIO check skill.

    Usage:
        /hardware-ai check-gpio ESP32 GPIO34 pwm

    Returns:
        GPIO check result
    """
    simulator = Simulator()
    result = simulator.check_gpio(mcu, pin, capability)

    icon = "✅" if result["result"] == "pass" else ("⚠️" if result["result"] == "unknown" else "❌")
    lines = [f"### 🎯 HardwareAI GPIO Check\n"]
    lines.append(f"**{mcu} {pin}**: {icon} {result['result'].upper()}\n")
    lines.append(f"{result['message']}")

    if result.get("recommendation"):
        lines.append(f"\n💡 **Recommendation:** {result['recommendation']}")

    return "\n".join(lines)


def register_skill() -> dict:
    """
    Return the skill definition for HardwareAI.

    This is used by Claude Code to register the /hardware-ai command.
    """
    return {
        "name": "hardware-ai",
        "description": "Simulate and validate hardware circuits before generating firmware",
        "commands": {
            "simulate": {
                "description": "Simulate a motor control circuit",
                "usage": "/hardware-ai simulate ESP32 + HW-039 + MY6812 + 12V",
                "example": "/hardware-ai simulate ESP32 + HW-039 + MY6812 + 12V",
            },
            "validate": {
                "description": "Validate electrical compatibility",
                "usage": "/hardware-ai validate --mcu ESP32 --driver HW-039 --motor MY6812 --voltage 12",
            },
            "check-gpio": {
                "description": "Check GPIO pin capability",
                "usage": "/hardware-ai check-gpio ESP32 GPIO34 pwm",
            },
        },
    }