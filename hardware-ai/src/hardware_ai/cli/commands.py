"""
HardwareAI CLI commands.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hardware_ai.core.simulator import Simulator, SimulationStatus
from hardware_ai.core.physics import PhysicsEngine
from hardware_ai.core.validator import Validator
from hardware_ai.components.registry import ComponentRegistry
from hardware_ai.components.motors import MOTOR_DATABASE
from hardware_ai.components.motor_drivers import DRIVER_DATABASE

app = typer.Typer(help="HardwareAI — Hardware simulation and validation for AI coding assistants", add_completion=False)
console = Console()


@app.command()
def simulate(
    circuit: str = typer.Argument(..., help="Circuit description (e.g. 'ESP32 + HW-039 + MY6812 + 12V')"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed step-by-step output"),
) -> None:
    """
    Simulate a hardware circuit design.

    Example:
        hardware-ai simulate "ESP32 + HW-039 + MY6812 + 12V"
    """
    console.print(Panel.fit(f"[bold cyan]HardwareAI Simulator[/bold cyan]\n{circuit}", title="Simulation"))

    # Parse the circuit description
    parts = [p.strip() for p in circuit.replace("+", ",").split(",")]

    mcu = parts[0] if len(parts) > 0 else None
    driver = parts[1] if len(parts) > 1 else None
    motor = parts[2] if len(parts) > 2 else None
    voltage_str = parts[3] if len(parts) > 3 else "12"
    voltage = float(voltage_str.replace("V", "").strip())

    if driver and motor:
        # Motor circuit simulation
        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name=mcu or "ESP32",
            driver_name=driver,
            motor_name=motor,
            motor_voltage=voltage,
            mcu_pwm_pin="GPIO25",
            has_flyback_diode=False,
        )

        # Print diagram
        console.print(Panel.fit(result.diagram, title="Circuit Diagram"))

        # Print analysis
        table = Table(title="Simulation Analysis")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="white")
        table.add_column("Detail", style="dim")

        for check, res in result.analysis.items():
            color = "green" if res == "PASS" or res == "PRESENT" else ("red" if res in ("FAIL", "MISSING") else "yellow")
            table.add_row(check, f"[{color}]{res}[/{color}]", "")

        console.print(table)

        # Print warnings
        if result.recommendations:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in result.recommendations:
                console.print(f"  • {rec}")

        # Final status
        status = result.status
        if status == SimulationStatus.PASS:
            console.print("\n[green bold]✅ RESULT: PASS[/green bold]")
        elif status == SimulationStatus.WARN:
            console.print("\n[yellow bold]⚠️  RESULT: PASS WITH WARNINGS[/yellow bold]")
        else:
            console.print(f"\n[red bold]❌ RESULT: {status.value.upper()}[/red bold]")

        if verbose:
            console.print("\n[dim]Simulation Steps:[/dim]")
            for step in result.steps:
                console.print(f"  [{step.step_number}] {step.action}: {step.result}")

    else:
        console.print("[yellow]Please specify a full circuit: MCU + driver + motor + voltage[/yellow]")
        console.print("Example: hardware-ai simulate \"ESP32 + HW-039 + MY6812 + 12V\"")


@app.command()
def validate(
    mcu: str = typer.Option("ESP32", help="Microcontroller model"),
    driver: str = typer.Option(None, help="Motor driver model"),
    motor: str = typer.Option(None, help="Motor model"),
    voltage: float = typer.Option(12.0, help="Operating voltage"),
    load_current: float = typer.Option(None, help="Expected load current in Amps"),
) -> None:
    """
    Validate electrical compatibility of a hardware design.

    Example:
        hardware-ai validate --mcu ESP32 --driver HW-039 --motor MY6812 --voltage 12
    """
    console.print(f"[bold cyan]HardwareAI Validator[/bold cyan] — {mcu} + {driver or 'no driver'} + {motor or 'no motor'} @ {voltage}V")

    if driver and motor:
        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name=mcu,
            driver_name=driver,
            motor_name=motor,
            motor_voltage=voltage,
            mcu_pwm_pin="GPIO25",
            has_flyback_diode=False,
        )

        if result.validation_result:
            console.print(result.validation_result.summary())
        else:
            for issue in result.steps:
                console.print(f"  {issue.description}: {issue.result}")

        if result.recommendations:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in result.recommendations:
                console.print(f"  • {rec}")
    else:
        console.print("[yellow]At minimum, provide --driver and --motor for validation[/yellow]")


@app.command()
def check_gpio(
    mcu: str = typer.Option("ESP32", help="Microcontroller model"),
    pin: str = typer.Argument(..., help="Pin name or number to check (e.g. GPIO34, D3)"),
    capability: str = typer.Option("pwm", help="Required capability: pwm, adc, i2c, spi, uart"),
) -> None:
    """
    Check if a GPIO pin has a specific capability.

    Example:
        hardware-ai check-gpio ESP32 GPIO34 --capability pwm
    """
    simulator = Simulator()
    result = simulator.check_gpio(mcu, pin, capability)

    color = "green" if result["result"] == "pass" else ("red" if result["result"] == "fail" else "yellow")
    console.print(f"[bold cyan]GPIO Check:[/bold cyan] {mcu} {pin}")
    console.print(f"  Capability: [cyan]{capability}[/cyan] → [{color}]{result['result'].upper()}[/{color}]")
    console.print(f"  Message: {result['message']}")
    if result.get("recommendation"):
        console.print(f"  [yellow]→ {result['recommendation']}[/yellow]")


@app.command()
def check_circuit(
    components: str = typer.Argument(..., help="Comma-separated components to check"),
) -> None:
    """
    Check circuit connections and compatibility.

    Example:
        hardware-ai check-circuit "ESP32,GPIO25,HW-039,MY6812,12V"
    """
    parts = [c.strip() for c in components.split(",")]
    console.print(f"[bold cyan]Circuit Check[/bold cyan] — {', '.join(parts)}")

    # Simple validation - check for known conflicts
    issues = []

    # Check for ESP32 GPIO34-39 used as outputs
    for part in parts:
        if part.upper() in ["GPIO34", "GPIO35", "GPIO36", "GPIO37", "GPIO38", "GPIO39"]:
            issues.append(f"  ❌ ERROR: {part} is INPUT-ONLY on ESP32 — cannot output PWM or drive HIGH")

    if issues:
        console.print("\n".join(issues))
    else:
        console.print("  ✅ No obvious circuit issues detected")
        console.print("\n[dim]Note: Run 'hardware-ai simulate' for full electrical validation[/dim]")


@app.command()
def verify_code(
    board: str = typer.Option("ESP32", help="Target board"),
    code: str = typer.Option(None, help="Code snippet to verify (not yet implemented)"),
) -> None:
    """
    Verify generated code matches hardware capabilities.

    This is a placeholder for future firmware verification.
    """
    console.print(f"[bold cyan]Code Verify[/bold cyan] — {board}")
    console.print("[yellow]⚠️  Code verification not yet implemented[/yellow]")
    console.print("  Coming soon: Parse Arduino/PlatformIO code and verify pin usage against hardware")


@app.command()
def components(
    category: Optional[str] = typer.Option(None, help="Filter by category (microcontroller, motor, driver, sensor, power_supply)"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all components"),
) -> None:
    """
    List components in the HardwareAI database.

    Example:
        hardware-ai components --list
        hardware-ai components --category motor
    """
    registry = ComponentRegistry()

    if list_all or category:
        by_category = registry.list_by_category()

        table = Table(title="HardwareAI Component Database")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="dim")
        table.add_column("Voltage", style="green")
        table.add_column("Current", style="yellow")

        filter_cat = category.lower() if category else None
        shown = 0
        for ctype, specs in by_category.items():
            if filter_cat and ctype.value != filter_cat and ctype.name.lower() != filter_cat:
                continue
            for spec in specs:
                table.add_row(
                    spec.name,
                    ctype.value,
                    f"{spec.voltage}V" if spec.voltage else "-",
                    f"{spec.current_limit}A" if spec.current_limit else "-",
                )
                shown += 1

        console.print(table)
        console.print(f"\n[dim]{shown} components shown[/dim]")
    else:
        summary = registry.summary()
        console.print(summary)


@app.command()
def physics(
    calc: str = typer.Argument(..., help="Calculation: v=ir, p=vi, series, parallel"),
    values: str = typer.Argument(..., help="Comma-separated values (e.g. '5,1000' for V=5V, R=1000Ω)"),
) -> None:
    """
    Run electrical physics calculations.

    Examples:
        hardware-ai physics v=ir 5,1000       # V=5V, R=1000Ω → calculate I
        hardware-ai physics p=vi 5,0.02        # V=5V, I=0.02A → calculate P
        hardware-ai physics series 100,220,330 # R1,R2,R3 → total series R
        hardware-ai physics parallel 1000,2000 # R1,R2 → total parallel R
    """
    parts = [float(v.strip()) for v in values.split(",")]
    engine = PhysicsEngine()
    result_str = ""

    calc = calc.lower()
    if calc == "v=ir":
        if len(parts) == 2:
            if parts[0] > 0 and parts[1] > 0:
                vals = engine.ohms_law(voltage=parts[0], resistance=parts[1])
                result_str = f"V={vals.voltage}V, I={vals.current*1000:.2f}mA, P={vals.power*1000:.2f}mW"
            else:
                result_str = "[red]Voltage and resistance must be positive[/red]"
        else:
            result_str = "[yellow]Usage: physics v=ir <voltage>,<resistance>[/yellow]"
    elif calc == "p=vi":
        if len(parts) == 2:
            p = engine.power_formula_iv(parts[0], parts[1])
            result_str = f"P={p*1000:.2f}mW (V={parts[0]}V × I={parts[1]*1000:.2f}mA)"
        else:
            result_str = "[yellow]Usage: physics p=vi <voltage>,<current>[/yellow]"
    elif calc == "series":
        total = engine.series_resistance(*parts)
        result_str = f"R_total = {total}Ω ({' + '.join(str(p) for p in parts)})"
    elif calc == "parallel":
        total = engine.parallel_resistance(*parts)
        result_str = f"R_total = {total:.2f}Ω ({' || '.join(str(p) for p in parts)})"
    else:
        result_str = f"[yellow]Unknown calculation: {calc}[/yellow]"
        console.print(result_str)
        console.print("Supported: v=ir, p=vi, series, parallel")
        return

    console.print(f"[bold cyan]Physics[/bold cyan] {calc} {values}")
    console.print(f"  → {result_str}")


@app.command()
def version() -> None:
    """Show HardwareAI version."""
    from hardware_ai import __version__
    console.print(f"[cyan]HardwareAI[/cyan] v{__version__}")


if __name__ == "__main__":
    app()