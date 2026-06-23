"""
HardwareAI API client for cloud communication.
"""

from __future__ import annotations

from typing import Optional
from urllib.parse import urljoin

import httpx

from hardware_ai.api.models import (
    SimulationRequest,
    SimulationResponse,
    ValidateRequest,
    ValidateResponse,
    ComponentQueryResponse,
    ComponentModel,
)


class HardwareAIClient:
    """
    Client for the HardwareAI cloud API.

    Handles:
    - Circuit simulation
    - Electrical validation
    - Component database queries
    - Code verification

    Args:
        base_url: Base URL of the HardwareAI cloud service.
                   Defaults to http://localhost:8000 for local development.
        api_key: API key for authentication.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _get_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # -------------------------------------------------------------------------
    # Simulation
    # -------------------------------------------------------------------------

    async def simulate(self, request: SimulationRequest) -> SimulationResponse:
        """
        Run a circuit simulation.

        Args:
            request: Simulation request with circuit details

        Returns:
            SimulationResponse with results and analysis

        Note:
            This is a local-first implementation that runs the simulation
            directly. When connected to a cloud service, this will dispatch
            to the cloud simulation engine.
        """
        # Local-first: import and use the local simulator
        from hardware_ai.core.simulator import Simulator
        from hardware_ai.core.circuit import Circuit, CircuitConnection, ComponentType, Pin, ComponentSpec
        from hardware_ai.components.registry import ComponentRegistry

        # Check if cloud service is available
        cloud_available = await self._check_cloud_available()

        if cloud_available:
            return await self._simulate_cloud(request)
        else:
            return await self._simulate_local(request)

    async def _check_cloud_available(self) -> bool:
        """Check if the cloud service is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def _simulate_cloud(self, request: SimulationRequest) -> SimulationResponse:
        """Run simulation on cloud service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/simulate",
                json=request.model_dump(),
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()
            return SimulationResponse(**data)

    async def _simulate_local(self, request: SimulationRequest) -> SimulationResponse:
        """Run simulation locally without cloud."""
        from hardware_ai.core.simulator import Simulator

        # Convert request to circuit representation
        circuit = Circuit(name=request.circuit_name)
        registry = ComponentRegistry()
        step_results = []

        # Build components
        for comp in request.components:
            spec = registry.get(comp.name)
            if not spec:
                # Create generic component
                spec = ComponentSpec(
                    name=comp.name,
                    component_type=ComponentType[comp.type.upper()] if comp.type.upper() in ComponentType.__members__ else ComponentType.SENSOR,
                    voltage=comp.voltage,
                    current_limit=comp.current_limit,
                )
            # Override voltage from request
            if comp.voltage:
                spec.voltage = comp.voltage
            circuit.add_component(comp.name, spec)

        # Build connections
        for conn in request.connections:
            circuit.add_connection(
                CircuitConnection(
                    from_component=conn.from_component,
                    from_pin=conn.from_pin,
                    to_component=conn.to_component,
                    to_pin=conn.to_pin,
                )
            )

        # Run simulation
        simulator = Simulator()
        sim_result = simulator.simulate(circuit)

        return SimulationResponse(
            simulation_id=sim_result.simulation_id,
            status=sim_result.status,
            circuit_name=sim_result.circuit_name,
            passed=sim_result.passed,
            analysis=sim_result.analysis,
            recommendations=sim_result.recommendations,
            diagram=sim_result.diagram,
        )

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    async def validate(self, request: ValidateRequest) -> ValidateResponse:
        """
        Validate electrical compatibility.

        Args:
            request: Validation request with design details

        Returns:
            ValidateResponse with compatibility status and issues
        """
        cloud_available = await self._check_cloud_available()
        if cloud_available:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/validate",
                    json=request.model_dump(),
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return ValidateResponse(**response.json())

        # Local validation
        from hardware_ai.core.simulator import Simulator

        simulator = Simulator()
        result = simulator.simulate_motor_circuit(
            mcu_name=request.mcu,
            driver_name=request.driver or "unknown",
            motor_name=request.motor or "unknown",
            motor_voltage=request.voltage,
            mcu_pwm_pin=request.pwm_pin or "GPIO25",
            has_flyback_diode=False,
        )

        return ValidateResponse(
            status=result.status,
            compatible=result.passed,
            issues=[],
            recommendations=result.recommendations,
            warnings=[s.description for s in result.steps],
        )

    # -------------------------------------------------------------------------
    # Component Database
    # -------------------------------------------------------------------------

    async def list_components(self, category: Optional[str] = None) -> ComponentQueryResponse:
        """
        List components from the database.

        Args:
            category: Optional filter by component type

        Returns:
            ComponentQueryResponse with matching components
        """
        registry = HardwareAIClient._get_local_registry()
        by_cat = registry.list_by_category()

        components = []
        count_by_cat: dict[str, int] = {}

        for ctype, specs in by_cat.items():
            count_by_cat[ctype.value] = len(specs)
            if category is None or ctype.value == category or ctype.name.lower() == category.lower():
                for spec in specs:
                    components.append(
                        ComponentModel(
                            name=spec.name,
                            type=ctype.value,
                            model=spec.model,
                            voltage=spec.voltage,
                            current_limit=spec.current_limit,
                            properties=spec.properties,
                        )
                    )

        return ComponentQueryResponse(components=components, total=len(components), categories=count_by_cat)

    @staticmethod
    def _get_local_registry():
        """Get the local component registry."""
        from hardware_ai.components.registry import ComponentRegistry
        return ComponentRegistry()

    # -------------------------------------------------------------------------
    # GPIO Check
    # -------------------------------------------------------------------------

    async def check_gpio(self, mcu: str, pin: str, capability: str) -> dict:
        """
        Check if a GPIO pin has a required capability.

        Args:
            mcu: Microcontroller model
            pin: Pin name/number
            capability: Required capability (pwm, adc, i2c, spi, uart)

        Returns:
            Dict with check result and recommendation
        """
        from hardware_ai.core.simulator import Simulator

        simulator = Simulator()
        return simulator.check_gpio(mcu, pin, capability)


# Synchronous client for simpler use cases
class SyncHardwareAIClient(HardwareAIClient):
    """Synchronous version of the HardwareAI client."""

    def simulate(self, request: SimulationRequest) -> SimulationResponse:
        """Run simulation synchronously."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(super().simulate(request))

    def validate(self, request: ValidateRequest) -> ValidateResponse:
        """Run validation synchronously."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(super().validate(request))

    def list_components(self, category: Optional[str] = None) -> ComponentQueryResponse:
        """List components synchronously."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(super().list_components(category))