"""MedLingoOrchestrator -- the master AI. Receives every request, identifies user/org/role/
permissions, detects intent, decides which agents are required, executes them, merges and
validates responses, stores memory, triggers workflows. No agent or engine calls another
agent/engine directly; every cross-component call goes through here. See docs/AI_ARCHITECTURE.md.

Pipeline order (matches docs/AI_ARCHITECTURE.md / the PRD's request pipeline):
auth -> org/role/patient context -> language -> speaker -> intent -> emotion ->
conversation context -> medical context -> knowledge retrieval -> safety precheck ->
generate response (1+ agents, merged) -> translate -> generate speech -> safety postcheck ->
store memory -> publish events (analytics/workflow automation react via the event bus).
"""

from dataclasses import dataclass, field
from typing import Any

from app.ai.agents import AgentResponse, merge_responses
from app.ai.agents.analytics_agent import AnalyticsAgent
from app.ai.agents.clinical_intelligence_agent import ClinicalIntelligenceAgent
from app.ai.agents.conversation_intelligence_agent import ConversationIntelligenceAgent
from app.ai.agents.documentation_agent import MedicalDocumentationAgent
from app.ai.agents.emergency_agent import EmergencyAgent
from app.ai.agents.insurance_agent import InsuranceAgent
from app.ai.agents.interpreter_agent import MedicalInterpreterAgent
from app.ai.agents.knowledge_agent import KnowledgeAgent
from app.ai.agents.patient_concierge_agent import PatientConciergeAgent
from app.ai.agents.safety_agent import SafetyAgent
from app.ai.agents.travel_concierge_agent import TravelConciergeAgent
from app.ai.agents.voice_intelligence_agent import VoiceIntelligenceAgent
from app.ai.agents.workflow_agent import WorkflowAgent
from app.ai.engines.context import ContextEngine
from app.ai.engines.emotion import EmotionEngine
from app.ai.engines.intent import IntentEngine
from app.ai.engines.language_intelligence import LanguageIntelligenceEngine
from app.ai.engines.speaker_recognition import SpeakerRecognitionEngine

# intent -> ordered agent keys to fan out to. "safety" and "emergency" are not listed here --
# emergency is forced in by the precheck override below, safety always runs via pre/postcheck.
INTENT_AGENT_MAP: dict[str, list[str]] = {
    "medical_question": ["clinical_reasoning", "knowledge"],
    "appointment": ["concierge", "workflow"],
    "translation": ["interpret"],
    "travel": ["travel_concierge"],
    "insurance": ["insurance"],
    "hospital": ["knowledge", "concierge"],
    "doctor": ["knowledge", "concierge"],
    "medication": ["clinical_reasoning", "knowledge"],
    "billing": ["concierge"],
    "navigation": ["concierge"],
    "recovery": ["clinical_reasoning", "concierge"],
    "follow_up": ["workflow", "concierge"],
    "complaint": ["concierge", "analytics"],
    "feedback": ["analytics"],
    "administration": ["workflow"],
    "document_upload": ["documentation", "knowledge"],
    "medical_report": ["documentation", "clinical_reasoning"],
    "video_consultation": ["interpret", "conversation_intelligence"],
    "voice_call": ["voice", "interpret"],
    "unknown": ["knowledge"],
}


@dataclass
class OrchestratorRequest:
    org_id: str
    user_id: str
    text: str = ""
    task: str | None = None  # explicit override; if None, intent detection picks the agent(s)
    audio: bytes | None = None
    patient_id: str | None = None
    medical_case_id: str | None = None
    conversation_session_id: str | None = None
    source_lang: str | None = None
    target_lang: str | None = None
    voice_output: bool = False
    voice_id: str | None = None
    voice_clone_consent: bool = False
    db: Any = None  # AsyncSession, injected by the route handler
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorResponse:
    content: str
    confidence: float
    flags: list[str]
    emergency: bool
    intent: str
    audio: bytes | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MedLingoOrchestrator:
    def __init__(self, *, llm_provider, stt_provider=None, tts_provider=None):
        self.llm = llm_provider
        self.speaker_engine = SpeakerRecognitionEngine()
        self.language_engine = LanguageIntelligenceEngine()
        self.intent_engine = IntentEngine()
        self.context_engine = ContextEngine()
        self.emotion_engine = EmotionEngine()
        self.safety = SafetyAgent(llm_provider)
        self.interpreter = MedicalInterpreterAgent(llm_provider)
        self.agents: dict[str, object] = {
            "interpret": self.interpreter,
            "clinical_reasoning": ClinicalIntelligenceAgent(llm_provider),
            "voice": VoiceIntelligenceAgent(llm_provider, stt_provider, tts_provider),
            "concierge": PatientConciergeAgent(llm_provider),
            "documentation": MedicalDocumentationAgent(llm_provider),
            "knowledge": KnowledgeAgent(llm_provider),
            "travel_concierge": TravelConciergeAgent(llm_provider),
            "insurance": InsuranceAgent(llm_provider),
            "emergency": EmergencyAgent(llm_provider),
            "analytics": AnalyticsAgent(llm_provider),
            "workflow": WorkflowAgent(llm_provider),
            "conversation_intelligence": ConversationIntelligenceAgent(llm_provider),
        }

    async def handle_request(self, request: OrchestratorRequest) -> OrchestratorResponse:
        user = await self._identify_user(request)
        org = await self._identify_organization(request)
        await self._authenticate(request, user, org)

        language = await self._detect_language(request)
        speaker_role = await self._detect_speaker(request, user)
        intent = request.task or (await self.intent_engine.run({"text": request.text})).get("intent", "unknown")
        emotion = await self._detect_emotion(request)

        medical_context = await self._build_medical_context(request, org)
        patient_memory = await self._retrieve_patient_memory(request)
        knowledge = await self._retrieve_knowledge(request, medical_context)

        precheck = self.safety.precheck(request.text, language=language)

        agent_keys = ["emergency"] if precheck.is_emergency else INTENT_AGENT_MAP.get(intent, ["knowledge"])

        agent_payload = {
            **request.extra,
            "text": request.text,
            "audio": request.audio,
            "speaker_role": speaker_role,
            "language": language,
            "source_lang": request.source_lang or language,
            "target_lang": request.target_lang or language,
            "emotion": emotion,
            "medical_context": medical_context,
            "patient_memory": patient_memory,
            "knowledge": knowledge,
            "journey_data": request.extra.get("journey_data", {}),
        }

        response = await self._dispatch_agents(agent_keys, agent_payload, org_id=request.org_id)
        response = await self._translate_if_needed(response, request, language, agent_keys)

        audio_out = None
        if request.voice_output:
            audio_out = await self._generate_speech(response, request)

        response = self.safety.postcheck(response)
        await self._maybe_escalate_to_human(request, org, response)

        await self._store_conversation_turn(request, response)
        await self._publish_lifecycle_events(request, precheck, response)

        return OrchestratorResponse(
            content=response.content,
            confidence=response.confidence,
            flags=response.flags,
            emergency=precheck.is_emergency,
            intent=intent,
            audio=audio_out,
            metadata=response.metadata,
        )

    async def _dispatch_agents(self, agent_keys: list[str], agent_payload: dict, *, org_id: str) -> AgentResponse:
        from app.core.observability import measure_agent_call
        from app.core.security import require_permission

        responses: list[AgentResponse] = []
        for key in agent_keys:
            if key != "emergency":  # emergency response must never be blockable by a missing
                require_permission(f"ai.{key}.run")  # permission grant -- see docs/RBAC.md
                # per-agent, not just "can use AI at all"
            agent = self.agents[key]
            async with measure_agent_call(agent_name=key, org_id=org_id, provider_used=type(self.llm).__name__) as measurement:
                result = await agent.handle(agent_payload)
                measurement.response = result
            responses.append(result)
        return merge_responses(responses)

    async def _translate_if_needed(
        self, response: AgentResponse, request: OrchestratorRequest, detected_language: str, agent_keys: list[str]
    ) -> AgentResponse:
        target = request.target_lang
        # interpret/emergency already translate to target_lang internally; other agents answer
        # in the working language and need an explicit translation pass before returning.
        already_translated = {"interpret", "emergency", "voice"}.intersection(agent_keys)
        if not target or target == detected_language or already_translated:
            return response

        from app.core.events import TRANSLATION_COMPLETED, TRANSLATION_STARTED, Event, event_bus

        await event_bus.publish(Event(type=TRANSLATION_STARTED, org_id=request.org_id, payload={"target": target}))
        translated = await self.interpreter.handle({
            "text": response.content,
            "speaker_role": "patient",
            "source_lang": detected_language,
            "target_lang": target,
            "medical_context": {},
        })
        await event_bus.publish(Event(type=TRANSLATION_COMPLETED, org_id=request.org_id, payload={"target": target}))

        translated.flags = sorted(set(translated.flags) | set(response.flags))
        translated.metadata = {**response.metadata, **translated.metadata}
        return translated

    async def _generate_speech(self, response: AgentResponse, request: OrchestratorRequest) -> bytes:
        voice_agent = self.agents["voice"]
        tts_response = await voice_agent.handle({
            "direction": "tts",
            "text": response.content,
            "language": request.target_lang or request.source_lang or "en",
            "voice_id": request.voice_id,
            "voice_clone_consent": request.voice_clone_consent,
        })
        return tts_response.metadata.get("audio")

    async def _maybe_escalate_to_human(self, request: OrchestratorRequest, org, response: AgentResponse) -> None:
        from app.modules.interpreter import service as interpreter_service

        threshold = (org or {}).get("ai_config", {}).get("hitl_confidence_threshold") if isinstance(org, dict) else None
        decision = interpreter_service.should_escalate(
            confidence=response.confidence, flags=response.flags, org_confidence_threshold=threshold
        )
        if not decision.should_escalate:
            return

        response.flags.append("human_handoff_requested")
        from app.core.events import AI_NEEDS_HUMAN_REVIEW, Event, event_bus
        await event_bus.publish(Event(
            type=AI_NEEDS_HUMAN_REVIEW,
            org_id=request.org_id,
            payload={"conversation_session_id": request.conversation_session_id, "reason": decision.reason},
        ))

    # -- pipeline steps: each delegates to a module service or engine. Module services are
    # Phase-1 interface stubs; this orchestration logic is the real Phase-2/3 deliverable. --

    async def _identify_user(self, request: OrchestratorRequest):
        from app.modules.auth import service as auth_service
        return await auth_service.get_user(request.user_id)

    async def _identify_organization(self, request: OrchestratorRequest):
        from app.modules.organizations import service as org_service
        return await org_service.get_org_settings(request.org_id)

    async def _authenticate(self, request: OrchestratorRequest, user, org) -> None:
        from app.core.security import require_permission
        require_permission("conversations.translate")  # coarse "may use the AI orchestrator at
        # all" gate; per-agent permissions are checked in _dispatch_agents once intent is known.

    async def _detect_language(self, request: OrchestratorRequest) -> str:
        result = await self.language_engine.run({"text": request.text})
        return result.get("language", request.source_lang or "en")

    async def _detect_speaker(self, request: OrchestratorRequest, user) -> str:
        result = await self.speaker_engine.run({"user": user})
        return result.get("role", "patient")

    async def _detect_emotion(self, request: OrchestratorRequest) -> str | None:
        result = await self.emotion_engine.run({"text": request.text})
        return result.get("emotion")

    async def _build_medical_context(self, request: OrchestratorRequest, org) -> dict:
        return await self.context_engine.run({
            "medical_case_id": request.medical_case_id,
            "conversation_session_id": request.conversation_session_id,
        })

    async def _retrieve_patient_memory(self, request: OrchestratorRequest) -> dict:
        if not request.patient_id:
            return {}
        from app.modules.ai_memory import service as memory_service
        return await memory_service.recall_all(request.db, request.patient_id)

    async def _retrieve_knowledge(self, request: OrchestratorRequest, medical_context: dict) -> list:
        from app.modules.knowledge_base import service as kb_service
        return await kb_service.search_articles(request.text)

    async def _store_conversation_turn(self, request: OrchestratorRequest, response: AgentResponse) -> None:
        from app.modules.conversations import service as conversation_service
        await conversation_service.add_turn(
            session_id=request.conversation_session_id,
            speaker_user_id=request.user_id,
            content=response.content,
            confidence=response.confidence,
            flags=response.flags,
        )

    async def _publish_lifecycle_events(self, request: OrchestratorRequest, precheck, response: AgentResponse) -> None:
        from app.core.events import AI_EMERGENCY_DETECTED, Event, event_bus

        if precheck.is_emergency:
            await event_bus.publish(Event(
                type=AI_EMERGENCY_DETECTED,
                org_id=request.org_id,
                payload={"pattern": precheck.matched_pattern, "conversation_session_id": request.conversation_session_id},
            ))
