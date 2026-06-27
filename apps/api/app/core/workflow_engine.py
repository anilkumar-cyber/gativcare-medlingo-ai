"""Configurable workflow engine over medical_cases.stage. Default sequence matches the patient
journey in docs/WORKFLOWS.md; an org can override the sequence (skip/reorder stages) via
organizations.ai_config['workflow_overrides'] without a code change. Advancing a stage publishes
MEDICAL_CASE_STAGE_CHANGED so other modules (notifications, analytics, travel/visa/insurance
activation) react without this engine knowing they exist.
"""

from app.core.events import MEDICAL_CASE_STAGE_CHANGED, Event, event_bus

DEFAULT_STAGE_SEQUENCE = [
    "inquiry",
    "qualification",
    "records_upload",
    "clinical_review",
    "second_opinion",
    "treatment_planning",
    "quotation",
    "insurance",
    "visa",
    "travel_planning",
    "airport_pickup",
    "hotel",
    "admission",
    "consultation",
    "diagnosis",
    "treatment",
    "surgery",
    "recovery",
    "discharge",
    "follow_up",
    "long_term_care",
]


class InvalidStageTransitionError(Exception):
    pass


class WorkflowEngine:
    def __init__(self, *, stage_sequence: list[str] | None = None):
        self.stage_sequence = stage_sequence or DEFAULT_STAGE_SEQUENCE

    def next_stage(self, current_stage: str) -> str | None:
        try:
            index = self.stage_sequence.index(current_stage)
        except ValueError as exc:
            raise InvalidStageTransitionError(f"unknown stage: {current_stage!r}") from exc
        if index + 1 >= len(self.stage_sequence):
            return None
        return self.stage_sequence[index + 1]

    async def advance(self, *, org_id: str, medical_case_id: str, current_stage: str) -> str | None:
        new_stage = self.next_stage(current_stage)
        if new_stage is None:
            return None

        from app.modules.patients import service as patients_service  # owns medical_cases per
        # docs/MODULES.md ("case records" under patients) -- this call is the Phase 3 seam.
        await patients_service.update_case_stage(medical_case_id, new_stage)

        await event_bus.publish(Event(
            type=MEDICAL_CASE_STAGE_CHANGED,
            org_id=org_id,
            payload={"medical_case_id": medical_case_id, "from": current_stage, "to": new_stage},
        ))
        return new_stage


def for_org(org_ai_config: dict) -> WorkflowEngine:
    override = org_ai_config.get("workflow_overrides")
    return WorkflowEngine(stage_sequence=override) if override else WorkflowEngine()
