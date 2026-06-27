"""Phase 3: implement against the patients table (docs/DATA_MODEL.md). Signature is fixed now
because app.ai.agents.orchestrator and medical_twin.service already call it."""


async def get_patient(patient_id):
    raise NotImplementedError


async def update_case_stage(medical_case_id, new_stage: str):
    raise NotImplementedError  # called by app.core.workflow_engine.WorkflowEngine.advance()
