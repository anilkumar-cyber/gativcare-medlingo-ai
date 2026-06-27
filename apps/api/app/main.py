"""App entrypoint. Mounts each module's router under /api/v1/<module>, wires the AI tool
registry and default automations on startup. No business logic here -- see docs/MODULES.md."""

from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.ai.agents.automation_agent import register_default_automations
    from app.ai.providers.claude_provider import ClaudeProvider
    from app.ai.tools.builtin import register_builtin_tools
    from app.ai.tools.registry import tool_registry

    llm_provider = ClaudeProvider()
    register_builtin_tools(tool_registry, llm_provider=llm_provider)
    register_default_automations(llm_provider)
    yield


app = FastAPI(title="GativCare MedLingo AI API", lifespan=lifespan)

# Module routers are registered here as they're implemented, e.g.:
# from app.modules.auth.router import router as auth_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
