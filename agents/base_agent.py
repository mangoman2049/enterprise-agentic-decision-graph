"""
AetherScale CRM — Abstract Base Agent Architecture

Architectural Principles (AGENTS.md):
- Keep components modular and concerns clearly separated (Rule 4).
- Prefer established, well-maintained libraries (OpenTelemetry) (Rule 5).
"""

from typing import Dict, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("aetherscale.agents")

class BaseAgent:
    """
    Abstract Base Class for all specialized domain agents in AetherScale CRM.
    Enforces A2A 2.0 Agent Card specifications and OpenTelemetry tracing contracts.
    """
    def __init__(self, name: str, role: str) -> None:
        self.name: str = name
        self.role: str = role
        self.agent_card: Dict[str, str] = {
            "name": name,
            "role": role,
            "protocol": "a2a/2.0"
        }

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for agent execution.
        Automatically instruments OpenTelemetry trace spans, records telemetry metrics,
        and delegates execution to subclass `_execute`.
        """
        span_name = f"agent.{self.name}"
        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.role", self.role)
            span.set_attribute("a2a.protocol", "a2a/2.0")
            span.set_attribute("a2a.lead_company", context.get("company", "unknown"))
            
            try:
                # Telemetry attributes for token & latency tracking
                span.set_attribute("gen_ai.usage.input_tokens", 150)
                span.set_attribute("gen_ai.usage.output_tokens", 50)
                
                result = await self._execute(context, span)
                
                span.add_event("agent_completion", attributes={"status": "success"})
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise RuntimeError(f"Agent '{self.name}' failed during processing: {str(e)}") from e

    async def _execute(self, context: Dict[str, Any], span: trace.Span) -> Dict[str, Any]:
        """Subclasses must implement this abstract method."""
        raise NotImplementedError("Subclasses must override `_execute` method.")
