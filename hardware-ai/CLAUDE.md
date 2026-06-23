# HardwareAI Design

HardwareAI prevents AI-generated hardware mistakes by simulating and validating embedded hardware designs before firmware generation.

## Architecture

```
User Request
    ↓
Claude Code
    ↓
HardwareAI Plugin (MCP server / CLI)
    ↓
Simulation Engine + Component Database
    ↓
Validation Results
    ↓
Claude generates corrected firmware
```

## Key Components

### Core (`src/hardware_ai/core/`)
- **physics.py** — Ohm's law, power calculations, resistance combinations
- **circuit.py** — Circuit representation (components, pins, connections)
- **simulator.py** — Main simulation engine; `simulate_motor_circuit()` is the primary entry point
- **validator.py** — Electrical validation (voltage compatibility, current limits, GPIO capabilities)

### Components (`src/hardware_ai/components/`)
- **registry.py** — Component database (microcontrollers, motors, drivers, sensors, power supplies)
- **esp32.py** — ESP32 DevKit V1 pin definitions (GPIO0-GPIO39, special pins, PWM/ADC capabilities)
- **arduino.py** — Arduino Uno R3 pin definitions
- **raspberry_pi_pico.py** — Raspberry Pi Pico / RP2040 pin definitions
- **motors.py** — Motor specs (MY6812, NEMA17, 28BYJ-48, etc.)
- **motor_drivers.py** — Motor driver specs (HW-039/L298N, L293D, DRV8833, TB6612FNG)
- **sensors.py** — Sensor specs (OLED SSD1306, BMP280, MPU6050, HC-SR04, DHT22)
- **power_supplies.py** — Power supply specs (12V 2A, 5V 3A, LDO regulators)
- **resistors.py** — Standard E-series values and LED resistor calculator

### API (`src/hardware_ai/api/`)
- **client.py** — Async HTTP client; falls back to local simulation when cloud unavailable
- **models.py** — Pydantic request/response schemas

### Plugins (`src/hardware_ai/plugins/claude_code/`)
- **mcp_server.py** — MCP server exposing 7 tools to Claude Code (simulate_circuit, validate_design, check_gpio, check_circuit, list_components, get_component_info, physics_calc)
- **skill.py** — Legacy slash command skill

## Critical Design Rules

1. **Local-first**: Simulation runs locally without cloud. Cloud API is optional upgrade.
2. **Error over silently wrong**: If a component isn't in the database, return `unknown` status and suggest verification.
3. **ESP32 GPIO34-39**: These are INPUT-ONLY. No PWM. This is the most common AI hardware mistake — always validate.
4. **Pydantic for all models**: Request/response schemas, component specs, validation results all use Pydantic.
5. **Rich console output**: CLI uses Rich for formatted tables, panels, and color-coded results.

## Common Validation Patterns

- `simulate_motor_circuit()` → Full motor circuit with diagram
- `check_gpio("ESP32", "GPIO34", "pwm")` → Pin capability check
- `validator.validate_motor_circuit()` → Electrical compatibility check

## Testing

```bash
pytest tests/ -v
```

Key test fixtures: `ESP32 + HW-039 + MY6812 + 12V` is the canonical test circuit.

## Adding New Components

Add to the appropriate `components/*.py` file following the existing pattern:
- Define pins using `Pin(name=, direction=, voltage=, current_limit=, is_pwm_capable=, is_adc_capable=)`
- Register in `MOTOR_DATABASE`, `DRIVER_DATABASE`, or `SENSOR_DATABASE`
- Import and register in `registry.py`'s `_initialize_database()`

## Claude Code Integration

Copy `.claude.example/settings.json` to `.claude/settings.json` to enable the MCP server.
The MCP server runs the HardwareAI tools directly inside Claude Code conversations.