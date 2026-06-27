"""Concrete tools, each a thin wrapper around an existing agent/module service -- no new
business logic lives here. register_builtin_tools() wires them into a ToolRegistry; called once
at app startup (app/main.py)."""

from app.ai.agents.interpreter_agent import MedicalInterpreterAgent
from app.ai.tools import Tool, ToolResult
from app.ai.tools.registry import ToolRegistry


class TranslationTool(Tool):
    name = "translate"
    description = "Interpret/translate text from one language to another, medically aware."

    def __init__(self, llm_provider):
        self.agent = MedicalInterpreterAgent(llm_provider)

    async def run(self, *, text: str, source_lang: str, target_lang: str, speaker_role: str = "patient") -> ToolResult:
        response = await self.agent.handle({
            "text": text, "source_lang": source_lang, "target_lang": target_lang, "speaker_role": speaker_role,
        })
        return ToolResult(tool_name=self.name, output=response.content)


class KnowledgeSearchTool(Tool):
    name = "knowledge_search"
    description = "Search hospital policies, treatment packages, drug data, FAQs, insurance/travel/visa rules."

    async def run(self, *, query: str) -> ToolResult:
        from app.modules.knowledge_base import service as kb_service
        results = await kb_service.search_articles(query)
        return ToolResult(tool_name=self.name, output=results)


class HospitalSearchTool(Tool):
    name = "hospital_search"
    description = "Find hospitals matching a specialty/location/org."

    async def run(self, *, db, org_id, query: str) -> ToolResult:
        from app.modules.hospitals import service as hospitals_service
        results = await hospitals_service.search(db, org_id=org_id, query=query)
        return ToolResult(tool_name=self.name, output=results)


class DoctorSearchTool(Tool):
    name = "doctor_search"
    description = "Find doctors matching a specialty/hospital/availability."

    async def run(self, *, db, org_id, query: str) -> ToolResult:
        from app.modules.doctors import service as doctors_service
        results = await doctors_service.search(db, org_id=org_id, query=query)
        return ToolResult(tool_name=self.name, output=results)


class AppointmentSchedulingTool(Tool):
    name = "schedule_appointment"
    description = "Book or reschedule an appointment for a medical case."

    async def run(self, *, db, medical_case_id=None, doctor_id=None, appointment_id=None, slot) -> ToolResult:
        from app.modules.appointments import service as appointments_service
        if appointment_id:
            result = await appointments_service.reschedule(db, appointment_id, slot)
        else:
            result = await appointments_service.book(db, medical_case_id, doctor_id, slot)
        return ToolResult(tool_name=self.name, output=result)


class DocumentProcessingTool(Tool):
    name = "process_document"
    description = "Extract, summarize, translate, and explain an uploaded medical/insurance/visa document."

    async def run(self, *, file_bytes: bytes, mime_type: str, native_text: str | None, patient_language: str, medical_context: dict) -> ToolResult:
        from app.modules.medical_documents.service import DocumentIntelligenceService
        # Provider instances are constructed by the caller (route handler / DI) and passed via
        # kwargs in a real wiring; omitted here since this tool is invoked through the registry
        # by agents that already hold those instances.
        raise NotImplementedError


class InsuranceVerificationTool(Tool):
    name = "verify_insurance"
    description = "Check coverage/pre-authorization status for a medical case."

    async def run(self, *, medical_case_id) -> ToolResult:
        from app.modules.insurance import service as insurance_service
        result = await insurance_service.check_coverage(medical_case_id)
        return ToolResult(tool_name=self.name, output=result)


class NotificationTool(Tool):
    name = "notify"
    description = "Send a notification (email/SMS/push/in-app) to a user."

    async def run(self, *, user_id, template: str, metadata: dict | None = None) -> ToolResult:
        from app.modules.notifications import service as notification_service
        await notification_service.notify(user_id, template=template, metadata=metadata)
        return ToolResult(tool_name=self.name, output="dispatched")


def register_builtin_tools(registry: ToolRegistry, *, llm_provider) -> None:
    for tool in (
        TranslationTool(llm_provider),
        KnowledgeSearchTool(),
        HospitalSearchTool(),
        DoctorSearchTool(),
        AppointmentSchedulingTool(),
        DocumentProcessingTool(),
        InsuranceVerificationTool(),
        NotificationTool(),
    ):
        registry.register(tool)
