"""AutomationEngine — see docs/ARCHITECTURE.md #1 for this engine's place in the pipeline."""

from app.ai.engines import Engine


class AutomationEngine(Engine):
    name = "automation"

    async def run(self, payload: dict) -> dict:
        raise NotImplementedError
