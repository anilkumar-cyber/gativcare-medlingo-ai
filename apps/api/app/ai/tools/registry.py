"""One registry, looked up by name. Agents call registry.get(name).run(**kwargs) instead of
importing a tool module directly -- this is what lets the orchestrator expose a stable tool list
to the LLM's function-calling interface regardless of which agent ends up using a given tool."""

from app.ai.tools import Tool, ToolResult


class ToolNotFoundError(Exception):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def list_specs(self) -> list[dict]:
        """Function-calling schema shape, for handing to an LLMProvider that supports tool use."""
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    async def invoke(self, name: str, **kwargs) -> ToolResult:
        try:
            return await self.get(name).run(**kwargs)
        except ToolNotFoundError as exc:
            return ToolResult(tool_name=name, output=None, error=str(exc))


tool_registry = ToolRegistry()
