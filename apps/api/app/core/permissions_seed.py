"""Baseline permission set granted to the Owner role created at org signup. Mirrors the "Org
Owner" column of docs/RBAC.md's permission matrix plus the per-agent `ai.<key>.run` permissions
from docs/AI_ARCHITECTURE.md#the-fourteen-agents (emergency excluded -- it's never gated, see
app/ai/agents/orchestrator.py::_dispatch_agents). This is a seed list, not the full matrix --
finer-grained roles (Doctor, Nurse, Coordinator, ...) are an org-admin role-management feature,
not something this seed needs to anticipate.
"""

AI_AGENT_KEYS = [
    "interpret",
    "clinical_reasoning",
    "voice",
    "concierge",
    "documentation",
    "knowledge",
    "travel_concierge",
    "insurance",
    "analytics",
    "workflow",
    "automation",
    "conversation_intelligence",
]

ORG_OWNER_PERMISSIONS = [
    "patients.view",
    "patients.edit",
    "patients.delete",
    "appointments.book",
    "reports.view",
    "reports.upload",
    "conversations.translate",
    "conversations.generate_summary",
    "doctors.manage",
    "hospitals.manage",
    "billing.manage",
    "ai.manage_config",
    "api.manage_keys",
    "analytics.view",
    "analytics.export",
    "integrations.manage",
    "audit.view",
    "medical_twin.view",
    "medical_twin.edit_preferences",
    "ai.view_confidence_flags",
    "consent.manage",
    *[f"ai.{key}.run" for key in AI_AGENT_KEYS],
]
