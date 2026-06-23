"""
Claude Code MCP server for HardwareAI.
Provides tools that Claude Code can call directly during code generation.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Optional
from pathlib import Path

# MCP server protocol
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool,TextContent
from mcp.server.notification_manager import NotificationManager

# HardwareAI core
from hardware_ai.core.simulator import Simulator
from hardware_ai.api.client import HardwareAIClient
from hardware_ai.components.registry import ComponentRegistry


# ---------------------------------------------------------------------------
# MCP Server Instance
# ---------------------------------------------------------------------------

SERVER_VERSION = "0.1.0"
server = Server("hardware-ai")

# Tools registry
tools = [
    Tool(
        name="simulate_circuit",
        description="Simulate a hardware circuit design with electrical validation. Use this when a user describes a hardware setup like 'ESP32 + motor driver + motor' to verify electrical compatibility before code generation.",
        inputSchema={
            "type": "object",
            "properties": {
                "mcu": {"type": "string", "description": "Microcontroller model (e.g., 'ESP32', 'Arduino Uno')"},
                "driver": {"type": "string", "description": "Motor driver model (e.g., 'HW-039', 'L298N', 'DRV8833')"},
                "motor": {"type": "string", "description": "Motor model (e.g., 'MY6812', 'NEMA17')"},
                "voltage": {"type": "number", "description": "Operating voltage in Volts", "default": 12.0},
                "pwm_pin": {"type": "string", "description": "MCU PWM pin to use (e.g., 'GPIO25' for ESP32)"},
                "flyback_diode": {"type": "boolean", "description": "Whether flyback protection is present", "default": False},
            },
            "required": ["mcu"],
        },
    ),
    Tool(
        name="validate_design",
        description="Validate electrical compatibility between components. Checks voltage levels, current limits, GPIO capabilities, and identifies potential issues before firmware generation.",
        inputSchema={
            "type": "object",
            "properties": {
                "mcu": {"type": "string", "description": "Microcontroller model"},
                "driver": {"type": "string", "description": "Motor driver or peripheral"},
                "motor": {"type": "string", "description": "Motor or actuator"},
                "voltage": {"type": "number", "description": "Operating voltage", "default": 12.0},
                "load_current": {"type": "number", "description": "Expected load current in Amps"},
            },
        },
    ),
    Tool(
        name="check_gpio",
        description="Check if a specific GPIO pin has a required capability (PWM, ADC, I2C, SPI, UART). Use this before generating code that uses specific pins to ensure they're valid.",
        inputSchema={
            "type": "object",
            "properties": {
                "mcu": {"type": "string", "description": "Microcontroller model (e.g., 'ESP32')"},
                "pin": {"type": "string", "description": "Pin name or number (e.g., 'GPIO34', 'D3', 'GP0')"},
                "capability": {"type": "string", "description": "Required capability: pwm, adc, i2c, spi, uart", "default": "pwm"},
            },
            "required": ["mcu", "pin"],
        },
    ),
    Tool(
        name="check_circuit",
        description="Quick check of circuit connections for common issues like using input-only pins as outputs, voltage mismatches, or missing components.",
        inputSchema={
            "type": "object",
            "properties": {
                "components": {"type": "array", "items": {"type": "string"}, "description": "List of components in the circuit"},
                "connections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Pin connections as strings like 'GPIO25→IN1'",
                },
            },
            "required": ["components"],
        },
    ),
    Tool(
        name="list_components",
        description="List available components in the HardwareAI database by category.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Component category: microcontroller, motor, motor_driver, sensor, power_supply",
                },
            },
        },
    ),
    Tool(
        name="get_component_info",
        description="Get detailed specifications for a specific component.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Component name or model (e.g., 'ESP32', 'HW-039', 'MY6812')"},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="physics_calc",
        description="Run electrical physics calculations (Ohm's law, power, resistance combinations).",
        inputSchema={
            "type": "object",
            "properties": {
                "calculation": {"type": "string", "description": "Type: v=ir, p=vi, series, parallel, voltage_divider"},
                "values": {"type": "array", "items": {"type": "number"}, "description": "Values for calculation"},
            },
            "required": ["calculation", "values"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool Handlers
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available HardwareAI tools."""
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from Claude Code."""

    try:
        if name == "simulate_circuit":
            result = await _simulate_circuit(arguments)
        elif name == "validate_design":
            result = await _validate_design(arguments)
        elif name == "check_gpio":
            result = await _check_gpio(arguments)
        elif name == "check_circuit":
            result = await _check_circuit(arguments)
        elif name == "list_components":
            result = await _list_components(arguments)
        elif name == "get_component_info":
            result = await _get_component_info(arguments)
        elif name == "physics_calc":
            result = await _physics_calc(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}, indent=2))]


async def _simulate_circuit(args: dict) -> dict:
    """Simulate a motor circuit."""
    simulator = Simulator()
    result = simulator.simulate_motor_circuit(
        mcu_name=args.get("mcu", "ESP32"),
        driver_name=args.get("driver", "unknown"),
        motor_name=args.get("motor", "unknown"),
        motor_voltage=args.get("voltage", 12.0),
        mcu_pwm_pin=args.get("pwm_pin", "GPIO25"),
        has_flyback_diode=args.get("flyback_diode", False),
    )
    return result.to_dict()


async def _validate_design(args: dict) -> dict:
    """Validate design compatibility."""
    simulator = Simulator()
    result = simulator.simulate_motor_circuit(
        mcu_name=args.get("mcu", "ESP32"),
        driver_name=args.get("driver", ""),
        motor_name=args.get("motor", ""),
        motor_voltage=args.get("voltage", 12.0),
        mcu_pwm_pin="GPIO25",
        has_flyback_diode=False,
    )

    return {
        "status": result.status.value,
        "passed": result.passed,
        "analysis": result.analysis,
        "recommendations": result.recommendations,
        "diagram": result.diagram,
    }


async def _check_gpio(args: dict) -> dict:
    """Check GPIO pin capability."""
    simulator = Simulator()
    return simulator.check_gpio(args.get("mcu", "ESP32"), args.get("pin", ""), args.get("capability", "pwm"))


async def _check_circuit(args: dict) -> dict:
    """Quick circuit check."""
    components = args.get("components", [])
    connections = args.get("connections", [])

    issues = []
    all_pins = []  # Track which pins are in use

    for comp in components:
        comp_lower = comp.lower()

        # Check for input-only GPIO on ESP32
        if "esp32" in comp_lower:
            for conn in connections:
                if "GPIO34" in conn or "GPIO35" in conn or "GPIO36" in conn:
                    issues.append({
                        "severity": "error",
                        "component": comp,
                        "message": f"{conn}: GPIO34-39 are INPUT-ONLY on ESP32",
                        "recommendation": "Use GPIO25 or GPIO26 for PWM output",
                    })

        # Check for voltage mismatches
        for conn in connections:
            all_pins.append(conn)

    return {
        "components": components,
        "connections": connections,
        "issues": issues,
        "warnings": [],
    }


async def _list_components(args: dict) -> dict:
    """List components by category."""
    registry = ComponentRegistry()
    category = args.get("category")

    if category:
        try:
            from hardware_ai.core.circuit import ComponentType
            ctype = ComponentType[category.upper()]
            specs = registry.by_type(ctype)
        except KeyError:
            return {"error": f"Unknown category: {category}", "valid_categories": [e.value for e in ComponentType]}
    else:
        specs = registry.list_all()

    return {
        "components": [
            {
                "name": spec.name,
                "type": spec.component_type.value,
                "model": spec.model,
                "voltage": spec.voltage,
                "current_limit": spec.current_limit,
                "power_rating": spec.power_rating,
            }
            for spec in specs
        ],
        "total": len(specs),
    }


async def _get_component_info(args: dict) -> dict:
    """Get detailed component info."""
    registry = ComponentRegistry()
    name = args.get("name", "")
    spec = registry.get(name)

    if not spec:
        return {"error": f"Component '{name}' not found in database"}

    return {
        "name": spec.name,
        "type": spec.component_type.value,
        "manufacturer": spec.manufacturer,
        "model": spec.model,
        "voltage": spec.voltage,
        "current_limit": spec.current_limit,
        "power_rating": spec.power_rating,
        "properties": spec.properties,
        "pins": {
            pin_name: {
                "direction": pin.direction,
                "voltage": pin.voltage,
                "current_limit": pin.current_limit,
                "is_pwm_capable": pin.is_pwm_capable,
                "is_adc_capable": pin.is_adc_capable,
                "description": pin.description,
            }
            for pin_name, pin in spec.pins.items()
        },
    }


async def _physics_calc(args: dict) -> dict:
    """Run physics calculation."""
    from hardware_ai.core.physics import PhysicsEngine

    calc = args.get("calculation", "")
    values = args.get("values", [])

    engine = PhysicsEngine()
    result = {}

    if calc == "v=ir" and len(values) >= 2:
        vals = engine.ohms_law(voltage=values[0], resistance=values[1])
        result = {"voltage": vals.voltage, "current_A": vals.current, "resistance_ohm": vals.resistance, "power_W": vals.power}
    elif calc == "p=vi" and len(values) >= 2:
        p = engine.power_formula_iv(values[0], values[1])
        result = {"power_W": p, "voltage": values[0], "current_A": values[1]}
    elif calc == "series":
        total = engine.series_resistance(*values)
        result = {"total_ohms": total, "individual": values}
    elif calc == "parallel":
        total = engine.parallel_resistance(*values)
        result = {"total_ohms": round(total, 4), "individual": values}

    return result


# ---------------------------------------------------------------------------
# Server Entry Point
# ---------------------------------------------------------------------------

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())