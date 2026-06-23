"""
Pydantic models for HardwareAI API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SimulationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"


class ComponentModel(BaseModel):
    """Component in a simulation request."""

    name: str
    type: str  # microcontroller, motor, driver, sensor, etc.
    model: Optional[str] = None
    voltage: Optional[float] = None
    current_limit: Optional[float] = None
    pin: Optional[str] = None  # Specific pin being used
    properties: dict = Field(default_factory=dict)


class ConnectionModel(BaseModel):
    """A connection between two component pins."""

    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    type: str = "digital"  # digital, power, pwm, i2c, spi, uart


class SimulationRequest(BaseModel):
    """Request to run a circuit simulation."""

    circuit_name: str
    components: list[ComponentModel]
    connections: list[ConnectionModel] = Field(default_factory=list)
    power_voltage: float = 12.0  # Main power rail voltage
    flyback_protection: bool = False
    metadata: dict = Field(default_factory=dict)


class IssueModel(BaseModel):
    """A validation issue found during simulation."""

    severity: str  # error, warning, info
    component: str
    message: str
    detail: str = ""
    recommendation: str = ""
    pin: Optional[str] = None


class SimulationStepModel(BaseModel):
    """A simulation step."""

    step: int
    action: str
    description: str
    component: str
    result: str


class SimulationResponse(BaseModel):
    """Response from a circuit simulation."""

    simulation_id: str
    status: SimulationStatus
    circuit_name: str
    passed: bool
    analysis: dict[str, str]  # e.g. {"voltage_check": "PASS", ...}
    issues: list[IssueModel] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    steps: list[SimulationStepModel] = Field(default_factory=list)
    diagram: str = ""


class ComponentQueryResponse(BaseModel):
    """Response for component database queries."""

    components: list[ComponentModel]
    total: int
    categories: dict[str, int]


class ValidateRequest(BaseModel):
    """Request to validate electrical compatibility."""

    mcu: str
    driver: Optional[str] = None
    motor: Optional[str] = None
    sensor: Optional[str] = None
    voltage: float = 12.0
    load_current: Optional[float] = None
    pwm_pin: Optional[str] = None


class ValidateResponse(BaseModel):
    """Response from electrical validation."""

    status: SimulationStatus
    compatible: bool
    issues: list[IssueModel] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)