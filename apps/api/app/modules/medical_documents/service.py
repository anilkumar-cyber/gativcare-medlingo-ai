"""Document intelligence: extract -> summarize -> translate -> patient-friendly explanation.
Pipeline per docs/AI_ARCHITECTURE.md #document-intelligence. The source file is never modified --
every call here returns a derived artifact linked to, not replacing, the original document.
PDF/Word text extraction skips OCR; scanned images go through OCRProvider first.
"""

from dataclasses import dataclass

from app.ai.agents.clinical_intelligence_agent import ClinicalIntelligenceAgent
from app.ai.agents.interpreter_agent import MedicalInterpreterAgent
from app.ai.providers.ocr import OCRProvider

NATIVE_TEXT_MIME_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


@dataclass
class DocumentAnalysis:
    extracted_text: str
    clinical_summary: str
    patient_friendly_explanation: str
    translated_explanation: str | None


class DocumentIntelligenceService:
    def __init__(self, *, ocr_provider: OCRProvider, clinical_agent: ClinicalIntelligenceAgent, interpreter_agent: MedicalInterpreterAgent):
        self.ocr = ocr_provider
        self.clinical_agent = clinical_agent
        self.interpreter_agent = interpreter_agent

    async def extract_text(self, file_bytes: bytes, *, mime_type: str, native_text: str | None = None) -> str:
        if mime_type in NATIVE_TEXT_MIME_TYPES and native_text is not None:
            return native_text
        return await self.ocr.extract(file_bytes, mime_type=mime_type)

    async def analyze(
        self,
        file_bytes: bytes,
        *,
        mime_type: str,
        native_text: str | None,
        patient_language: str,
        medical_context: dict,
    ) -> DocumentAnalysis:
        extracted_text = await self.extract_text(file_bytes, mime_type=mime_type, native_text=native_text)

        summary_response = await self.clinical_agent.handle({
            "text": extracted_text,
            "task_type": "explain_findings",
            "medical_context": medical_context,
            "patient_memory": {},
            "knowledge": [],
        })

        explanation_response = await self.interpreter_agent.handle({
            "text": summary_response.content,
            "speaker_role": "patient",
            "source_lang": "en",
            "target_lang": "en",
            "medical_context": medical_context,
        })

        translated = None
        if patient_language != "en":
            translated_response = await self.interpreter_agent.handle({
                "text": explanation_response.content,
                "speaker_role": "patient",
                "source_lang": "en",
                "target_lang": patient_language,
                "medical_context": medical_context,
            })
            translated = translated_response.content

        return DocumentAnalysis(
            extracted_text=extracted_text,
            clinical_summary=summary_response.content,
            patient_friendly_explanation=explanation_response.content,
            translated_explanation=translated,
        )


async def get_documents(patient_id):
    raise NotImplementedError  # Phase 3: query medical_documents table
