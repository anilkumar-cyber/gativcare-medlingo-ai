"""App entrypoint. Mounts each module's router under /api/v1/<module>, wires the AI tool
registry and default automations on startup. No business logic here -- see docs/MODULES.md."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.ai.agents.automation_agent import register_default_automations
    from app.ai.agents.orchestrator import MedLingoOrchestrator
    from app.ai.providers.claude_provider import ClaudeProvider
    from app.ai.tools.builtin import register_builtin_tools
    from app.ai.tools.registry import tool_registry

    llm_provider = ClaudeProvider()
    register_builtin_tools(tool_registry, llm_provider=llm_provider)
    register_default_automations(llm_provider)
    # One orchestrator instance for the app's lifetime -- agents hold no per-request state, so
    # this is safe to share across concurrent requests. Routes reach it via app.state, not a
    # global, so tests can swap in a different instance.
    app.state.orchestrator = MedLingoOrchestrator(llm_provider=llm_provider)
    yield


app = FastAPI(title="GativCare MedLingo AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.modules.auth.router import router as auth_router
from app.modules.organizations.router import router as organizations_router
from app.modules.hospitals.router import router as hospitals_router
from app.modules.doctors.router import router as doctors_router
from app.modules.patients.router import router as patients_router
from app.modules.appointments.router import router as appointments_router
from app.modules.conversations.router import router as conversations_router
from app.modules.ai_memory.router import router as ai_memory_router
from app.modules.medical_twin.router import router as medical_twin_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(organizations_router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(hospitals_router, prefix="/api/v1/hospitals", tags=["hospitals"])
app.include_router(doctors_router, prefix="/api/v1/doctors", tags=["doctors"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(conversations_router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(ai_memory_router, prefix="/api/v1/ai-memory", tags=["ai-memory"])
app.include_router(medical_twin_router, prefix="/api/v1/medical-twin", tags=["medical-twin"])

# Remaining module routers are registered here as their service logic is implemented (Phase 3
# continued) -- see docs/MODULES.md for the full list.
