from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("v2_enterprise_agents")

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.agent_card = {
            "name": name,
            "role": role,
            "protocol": "a2a/2.0"
        }

    async def process(self, context: dict) -> dict:
        """
        Main entry point for the agent. Wraps the execution in an OpenTelemetry span.
        """
        with tracer.start_as_current_span(f"agent.{self.name}") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.role", self.role)
            span.set_attribute("a2a.lead_id", context.get("lead_id", "unknown"))
            
            try:
                # Add mock token usage to telemetry
                span.set_attribute("gen_ai.usage.input_tokens", 150)
                span.set_attribute("gen_ai.usage.output_tokens", 50)
                
                result = await self._execute(context, span)
                
                # Add result to span events
                span.add_event("agent_completion", attributes={"status": "success"})
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    async def _execute(self, context: dict, span: trace.Span) -> dict:
        """Override this in subclasses."""
        raise NotImplementedError
