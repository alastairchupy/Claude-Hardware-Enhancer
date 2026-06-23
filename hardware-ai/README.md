# HardwareAI

**Cloud-based hardware simulation and validation for AI coding assistants.**

HardwareAI acts as a hardware verification engine between Claude and physical electronics. Its purpose is to simulate, test, and validate embedded hardware designs before Claude generates final firmware — preventing AI-generated hardware mistakes before they reach real-world devices.

## Features

- 🔌 **Circuit Simulation** — Simulate microcontrollers, motors, drivers, sensors, and power supplies
- ⚡ **Electrical Validation** — Voltage compatibility, current limits, GPIO capabilities
- 🎯 **GPIO Checking** — Verify pins support required capabilities (PWM, ADC, I2C, SPI)
- 📊 **Component Database** — Pre-loaded specs for ESP32, Arduino, Raspberry Pi Pico, motors, drivers, sensors
- 🖥️ **CLI** — `hardware-ai` command-line tool for manual testing
- 🔌 **Claude Code MCP** — HardwareAI tools available directly in Claude Code conversations
- ☁️ **Cloud-Ready** — Local-first architecture with optional cloud service upgrade

## Quick Start

```bash
# Install
pip install -e .

# Simulate a motor circuit
hardware-ai simulate "ESP32 + HW-039 + MY6812 + 12V"

# Check GPIO pin capability
hardware-ai check-gpio ESP32 GPIO34 pwm

# Run physics calculations
hardware-ai physics v=ir 5,1000

# List components
hardware-ai components --list
```

## Example

```
$ hardware-ai simulate "ESP32 + HW-039 + MY6812 + 12V"

✅ RESULT: PASS with warnings

⚠️  No flyback protection detected
   → Add flyback diode across motor terminals
```

## Architecture

```
User Request → Claude Code → HardwareAI Plugin → Simulation Engine
                                                   ↓
                                             Component Database
                                                   ↓
                                           Validation Results
                                                   ↓
                                        Claude Code Correction
                                                   ↓
                                            Final Firmware
```

## Supported Hardware

**Microcontrollers:** ESP32 DevKit V1, Arduino Uno R3, Raspberry Pi Pico

**Motor Drivers:** HW-039, L298N, L293D, DRV8833, TB6612FNG

**Motors:** MY6812, NEMA17, 28BYJ-48, JGA25

**Sensors:** OLED SSD1306, BMP280, MPU6050, HC-SR04, DHT22

## Claude Code Integration

Copy `.claude.example/settings.json` to `.claude/settings.json`, then restart Claude Code to enable the MCP server.

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed design documentation.

## License

MIT