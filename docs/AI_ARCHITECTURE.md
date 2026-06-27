# AI Architecture — The MedLingo Brain

This extends [ARCHITECTURE.md §1/§4](ARCHITECTURE.md). The Phase-1 "engines" are fine-grained,
single-responsibility pipeline stages. This doc adds an **agent layer** above them: agents are
task-level specialists a human/portal actually talks to; engines are the reusable building blocks
agents compose. Engines never call each other; agents never call each other — both only happen
through the orchestrator. Two layers because a single flat list of 14+ engines has no place to put
"behave like a medical interpreter" persona/tone without duplicating it into every engine; the
agent layer is exactly that home.

```
Master Orchestrator (MedLingoOrchestrator)
  ├─ Medical Interpreter Agent        → speaker_recognition, language_intelligence, medical_knowledge, emotion engines
  ├─ Clinical Intelligence Agent      → medical_knowledge, clinical_reasoning, knowledge_retrieval engines
  ├─ Medical Documentation Agent      → clinical_reasoning, medical_knowledge engines
  ├─ Voice Intelligence Agent         → voice_intelligence engine + STT/TTS providers
  ├─ Conversation Intelligence Agent  → context engine (multi-turn continuity, not single-utterance interpretation)
  ├─ Knowledge Agent                  → knowledge_retrieval engine + knowledge_base module (RAG)
  ├─ Patient Concierge Agent          → context, knowledge_retrieval engines + journey modules
  ├─ Travel Concierge Agent           → travel/hotels/airport_pickup/visa modules
  ├─ Insurance Agent                  → insurance module + retrieved insurer rules
  ├─ Emergency Agent                  → reuses Medical Interpreter + forces notification/priority side-effects
  ├─ Analytics Agent                  → analytics module's pre-computed aggregates (phrasing layer only)
  ├─ Workflow Agent                   → app/core/workflow_engine.py (case-stage state machine)
  ├─ Automation Agent                 → app/core/events.py subscriptions, rule-table reactions
  └─ Safety Agent                     → cross-cutting, reviews every other agent's output before it ships
```

This is 14 specialized agents + the orchestrator, matching the PRD's roster 1:1. No agent calls
another agent — the only exception by design is Emergency, which *wraps* Medical Interpreter
(same interpretation, different side-effects), not a peer-to-peer call.

Every agent is an `Agent` (see `app/ai/agents/__init__.py`): takes a typed request, returns a
typed response, declares which engines/modules it depends on. The orchestrator is the only thing
that knows the full agent roster.

## Master orchestrator workflow

`app/ai/agents/orchestrator.py::MedLingoOrchestrator.handle_request()` implements, in order:

```
receive_request -> identify_user -> identify_organization -> authenticate (coarse gate) ->
detect_language -> detect_speaker -> detect_intent -> detect_emotion ->
build_medical_context -> retrieve_patient_memory -> retrieve_knowledge ->
run_safety_precheck (emergency override) -> dispatch_agents (per-agent permission + intent routing) ->
merge_responses -> translate_if_needed -> generate_speech_if_requested ->
run_safety_postcheck -> maybe_escalate_to_human (HITL) -> store_conversation_turn ->
publish_lifecycle_events -> return_response
```

`run_safety_precheck`/`run_safety_postcheck` are the Safety Agent running before *and* after
agent dispatch — before, to catch emergency content early and override routing entirely (an
emergency doesn't wait for intent classification to pick the "right" agent, it forces the
Emergency agent); after, to catch hallucination/confidence/diagnosis-shaped issues in the
generated output before it reaches anyone.

Implementation status: control flow, intent routing, multi-agent merge, translation pass, and HITL
escalation are real (`app/ai/agents/orchestrator.py`). The identify/authenticate/persist steps
call into `auth`/`organizations`/`conversations` module services, which are still interface stubs
per Phase 1 — wiring those is Phase 3 (module implementation), not an AI-layer concern.

## Intent Engine and routing

`app/ai/engines/intent.py::IntentEngine` classifies every request into one of the PRD's 20 intent
categories (medical_question, appointment, emergency, translation, travel, insurance, hospital,
doctor, medication, billing, navigation, recovery, follow_up, complaint, feedback,
administration, document_upload, medical_report, video_consultation, voice_call, unknown) via
keyword/regex matching — cheap, deterministic, testable, with emergency checked first and
winning over every other match. `INTENT_AGENT_MAP` in `orchestrator.py` maps each intent to the
ordered list of agent keys required, e.g. `medical_report -> [documentation, clinical_reasoning]`,
`travel -> [travel_concierge]`. The orchestrator routes to **only** those agents — this is what
keeps a 14-agent roster from meaning 14 LLM calls per request.

An LLM-based classifier can replace/augment the keyword pass later without changing the `Engine`
interface or `INTENT_AGENT_MAP` — the routing table is the stable contract, not the classifier
implementation.

## Multi-agent collaboration and merge model

No agent calls another agent. When an intent maps to more than one agent key (e.g.
`document_upload -> [documentation, knowledge]`), the orchestrator runs each agent against the
*same* payload independently and combines results with `merge_responses()`
(`app/ai/agents/__init__.py`): content sections are concatenated and labeled by agent, flags are
unioned, and **confidence is the minimum across agents, not the average** — a merged answer is
only as trustworthy as its weakest contributing agent, and averaging would hide that.

This fan-out-then-merge model, not a single monolithic call and not agents invoking each other,
is what "every AI agent must collaborate, no AI agent should operate independently" means in
code: collaboration happens at the orchestrator's merge step, never via direct agent-to-agent
calls (which would make the dependency graph between 14 agents unmanageable).

## The fourteen agents

| Agent | Persona / job | Primary engines/modules used | Notes |
|---|---|---|---|
| Medical Interpreter | certified medical interpreter, never literal | speaker_recognition, language_intelligence, medical_knowledge, emotion | role-aware output: same clinical fact, doctor-register vs patient-register phrasing |
| Clinical Intelligence | senior-physician-level medical reasoning, explanatory only | medical_knowledge, clinical_reasoning, knowledge_retrieval | never outputs a diagnosis/prescription as a final answer |
| Medical Documentation | drafts, never finalizes, clinical paperwork | clinical_reasoning, medical_knowledge | every output requires clinician sign-off |
| Voice Intelligence | speech in/out pipeline owner | voice_intelligence engine + STT/TTS providers | delegates DSP/ASR/TTS to providers, see Voice Pipeline below |
| Conversation Intelligence | multi-turn continuity, not single-utterance translation | context engine | resolves references to earlier turns; produces conversation summaries |
| Knowledge | RAG specialist over guidelines/hospital/drug/FAQ data | knowledge_retrieval, knowledge_base module | answers strictly from retrieved passages, cites them, says "not found" rather than guessing |
| Patient Concierge | healthcare concierge for non-travel/insurance logistics | context, knowledge_retrieval | redirects clinical questions instead of answering them |
| Travel Concierge | flights/visas/hotels/airport pickup | travel, hotels, airport_pickup, visa modules | split from Patient Concierge so travel logic has one owner |
| Insurance | coverage/claims/pre-auth | insurance module + retrieved insurer rules | refuses to answer (flags `insufficient_data`) if policy/rule data is missing, never guesses coverage |
| Emergency | low-latency interpretation during a flagged emergency | wraps Medical Interpreter | appends an emergency-assistance disclaimer; doesn't replace emergency protocols |
| Analytics | answers questions about an org's own metrics | analytics module's pre-computed aggregates | phrasing layer only — never estimates a number it wasn't given |
| Workflow | "what stage is this case at / what's next" | `app/core/workflow_engine.py` | reports state machine status; doesn't own the state machine |
| Automation | event -> action rule table | `app/core/events.py` subscriptions | no LLM call for the common cases — a rule lookup is faster and more predictable |
| Safety | the only agent every response passes through | safety engine + standalone heuristics | described fully below |

Each agent file defines a constant `SYSTEM_PROMPT` (the persona/responsibility text) and a
`handle()` coroutine. Persona text lives in code, not as a magic string scattered across callers,
so org-level tone customization (`organizations.ai_config`) is one place to merge overrides.

## Safety Agent (detail)

Three things it does, none requiring a trained classifier to start:

1. **Emergency detection** — keyword/pattern match against an emergency lexicon (chest pain,
   can't breathe, severe bleeding, suicide, etc., localized per language) run on every turn
   pre-dispatch. A hit short-circuits the orchestrator straight to a notification to on-call/
   emergency staff, in parallel with (not instead of) a normal response.
2. **Disclaimer injection** — if the Clinical Intelligence or Documentation agent's output matches
   diagnosis/prescription-shaped language, append the "confirm with your physician" disclaimer.
   Pattern-based now; an LLM self-check can replace the pattern list later without changing the
   interface.
3. **Confidence scoring + hallucination flag** — every agent response carries a `confidence: float`
   and `flags: list[str]`. Source of confidence: provider-reported logprobs/finish-reason where
   available, otherwise a cheap self-consistency check (ask the model to rate its own certainty).
   Below a threshold, the orchestrator marks the turn `needs_human_review` instead of suppressing
   it — suppressing low-confidence medical output silently is worse than flagging it.

`run_safety_postcheck` is what actually invokes these three; the engine file
(`app/ai/engines/safety.py`) holds the reusable detection logic, the agent
(`app/ai/agents/safety_agent.py`) holds the orchestration-facing decision (escalate / disclaim /
flag / pass).

## Memory architecture

Eleven named memory types, all consent-gated where they touch patient data, all org-scoped:

| Memory | Lifetime | Consent required | Storage |
|---|---|---|---|
| Session | single session | no | Redis |
| Conversation | one conversation_session | no (operational) | Postgres `conversation_turns` |
| Patient | persistent | **yes** | Postgres `ai_memory_facts` |
| Hospital | persistent | no | Postgres `hospitals`-linked config |
| Doctor | persistent | no | Postgres `doctors`-linked config |
| Organization | persistent | no | Postgres `organizations.ai_config` |
| Knowledge | persistent, shared | no | vector store + `knowledge_base` module |
| Workflow | persistent | no | Postgres `medical_cases.stage` history |
| Preference | persistent | yes (patient-level) | Postgres `ai_memory_facts` (scope=preference) |
| Language | persistent | yes (patient-level) | Postgres `ai_memory_facts` (scope=language) |
| Medical History | persistent | **yes**, strictest | Postgres `ai_memory_facts` (scope=medical_history) + Medical Twin |

All patient-scoped memory reads go through `ai_memory.service.recall(patient_id, scope)`, which
checks `consents` before returning anything — see [DATA_MODEL.md](DATA_MODEL.md). This is the
single chokepoint; no agent queries `ai_memory_facts` directly.

## Medical Twin

A patient's Medical Twin is not a new memory type — it's a **read-optimized aggregate view** over
existing data (medical history memory, consultations, reports, allergies, medications, imaging,
surgeries, recovery progress, language/cultural preference memory, travel history, preferred
doctors/hospitals, insurance) assembled on read, not duplicated on write. Storing it as a separate
denormalized blob would create a second source of truth that drifts from the underlying records —
exactly the bug class multi-tenant healthcare data can't afford.

`medical_twin.service.get_twin(patient_id)` therefore: checks consent, then fan-out reads from
`patients`, `medical_cases`, `medical_reports`, `ai_memory_facts`, `travel_itineraries`,
`insurance_policies`, composes one `MedicalTwin` response object. It explicitly does not store a
diagnosis or risk score — continuity and context only, per the PRD's own framing.

Every Clinical Intelligence / Medical Interpreter / Patient Concierge agent call that needs patient
background calls `get_twin()` once at the top of `handle()` rather than separately querying memory,
reports, and travel data itself — one call, one consent check, one place to extend later.

## Voice pipeline

`app/ai/voice_pipeline.py`, a real chained async function, not a stub:

```
raw_audio -> AudioProcessor.denoise() -> AudioProcessor.enhance() ->
VoiceIntelligenceAgent.detect_speaker() -> LanguageIntelligenceEngine.detect() ->
STTProvider.transcribe() -> MedLingoOrchestrator.handle_request() (text path) ->
TTSProvider.synthesize() -> output_audio
```

`AudioProcessor` (denoise/enhance) is its own interface (`app/ai/providers/audio.py`) for the same
reason `STTProvider`/`TTSProvider` are interfaces — noise removal and voice enhancement are
specialized DSP/ML problems best solved by a dedicated vendor model, not reimplemented in-house.
Target: <1s end-to-end where the provider chain allows streaming (STT/TTS providers chosen later
must support streaming, not just batch, to hit this).

Voice cloning is **opt-in only**: a `voice_clone_consent` flag on the patient/doctor record, checked
by `VoiceIntelligenceAgent` before any `TTSProvider.synthesize(..., voice_id=cloned_id)` call —
without explicit consent, only stock/neutral voices are available.

## Knowledge retrieval (RAG)

The Knowledge Agent never answers from model memory alone. `knowledge_base.service.search_articles()`
retrieves passages from hospital policies, treatment packages, medical tourism information, drug
databases, clinical guidelines, FAQs, insurance rules, travel/visa requirements, and
organization-specific documents (vector-store-backed, org-scoped — an org's private documents
never leak into another org's retrieval results, same tenant-isolation rule as everywhere else).
The orchestrator runs retrieval *before* generation (`_retrieve_knowledge()` step, ahead of agent
dispatch) and passes results into every agent's payload as `knowledge: list[str]` — the Knowledge
Agent cites them by index; Clinical Intelligence and Insurance agents ground their answers in them
when present and explicitly flag `insufficient_data`/`no_retrieval_hits` when absent, rather than
falling back to unguided model knowledge for anything insurance/policy/medication-specific.

## AI Tools

`app/ai/tools/` is a modular tool-invocation layer separate from agents: a `Tool` (translate,
knowledge_search, hospital_search, doctor_search, schedule_appointment, process_document,
verify_insurance, notify) wraps exactly one existing module service or provider call — a tool
contains no business logic of its own, it's a function-calling-shaped adapter. `ToolRegistry`
(`app/ai/tools/registry.py`) is the single place tools are registered and looked up by name, and
`registry.list_specs()` is what would be handed to an `LLMProvider` that supports tool-calling, so
an agent (or future capability) can invoke `schedule_appointment` or `verify_insurance` as a
function call instead of the orchestrator hardcoding when each module gets touched.
`register_builtin_tools()` wires the built-in set at app startup (`app/main.py`).

## Human-in-the-Loop (HITL)

`app/modules/interpreter/service.py::should_escalate()` is the pure decision function the
orchestrator calls after every safety postcheck: if confidence drops below a
configurable threshold (org-overridable via `organizations.ai_config.hitl_confidence_threshold`,
default 0.55) or the response carries a complexity flag (`needs_human_review`,
`diagnosis_shaped_disclaimer_added`, `emergency_flagged`, `insufficient_data`), the orchestrator
publishes `AI_NEEDS_HUMAN_REVIEW` and flags the turn `human_handoff_requested`. This **augments**
rather than pauses communication — the AI's response still goes out; a qualified human
interpreter/coordinator is invited into the session in parallel, not instead. This is the
trust-building mechanism for hospitals/clinicians: the AI is maximally useful on its own, and
visibly defers the moment a conversation gets clinically complex or the AI itself is unsure.

## AI governance model

A small, fixed set of rules every agent is built to respect, enforced at the orchestrator/Safety
layer rather than left to prompt wording alone:

1. No agent's output is ever treated as a final diagnosis, prescription, or dosage change —
   Clinical Intelligence and Documentation are prompted never to state one, and Safety's
   diagnosis-shaped pattern match adds a disclaimer as a backstop if one slips through.
2. Every patient-identifying memory read/write is consent-gated at the `ai_memory.service`
   chokepoint — no agent or tool has a path to `ai_memory_facts` that skips the consent check.
3. Low confidence is surfaced, never silently suppressed (`needs_human_review`, HITL escalation).
4. Voice cloning requires explicit, current consent, checked before every cloned-voice synthesis.
5. Every agent call is observable (`app/core/observability.py`) — there is no agent invocation
   that doesn't emit a measurable event, which is what makes audit and quality monitoring
   possible after the fact rather than only at design time.

These map directly onto RBAC's `ai.safety_override` (only Super Admin/assigned clinician may
dismiss a safety flag) and `consent.manage` permissions — governance is enforced by code paths and
permission checks, not by documentation alone.

## Document intelligence

Lives in `medical_documents.service` (not a new module — it's an operation on an existing entity).
Pipeline: `OCRProvider.extract() -> ClinicalIntelligenceAgent.summarize() ->
MedicalInterpreterAgent.translate() -> patient-friendly explanation render`. Scanned images route
through `OCRProvider` first; native PDF/Word text extraction skips straight to summarize. Original
file is always retained unmodified — every output is a derived artifact linked to, never replacing,
the source document.

## Event-driven side effects

`app/core/events.py::EventBus` is the single publish/subscribe seam (`patient.registered`,
`appointment.booked`, `report.uploaded`, `translation.started/completed`,
`medical_case.stage_changed`, `ai.needs_human_review`, `ai.emergency_detected`, ...). The
orchestrator **publishes**, it never calls `notifications.service.notify()` directly for
reactive side effects — the Automation Agent **subscribes** and maps event → notification via a
fixed rule table (`AUTOMATION_RULES`). This is what lets a brand-new module react to
`report.uploaded` later without editing the orchestrator or the `medical_reports` module: it just
subscribes. Phase 2 implementation is in-process pub/sub; Phase 3 swaps the transport for Redis
pub/sub without changing any subscriber.

The Workflow Agent's underlying `app/core/workflow_engine.py::WorkflowEngine` advances
`medical_cases.stage` through the sequence in [WORKFLOWS.md](WORKFLOWS.md), publishing
`medical_case.stage_changed` on every advance, and accepts a per-org stage-sequence override via
`organizations.ai_config.workflow_overrides` — configurable workflows without a code change.

## Observability & AI quality monitoring

`app/core/observability.py`: every agent call emits a structured event — `agent_name`, `org_id`,
`latency_ms`, `confidence`, `flags`, `provider_used`. Feeds the Analytics module's "AI Accuracy
Metrics" / "Translation Confidence" dashboards directly (PRD's Analytics section) — there's no
separate AI-metrics pipeline, it's the same event stream analytics already consumes. The same
mechanism backs agent usage, API usage, error-rate, and escalation-rate monitoring called for in
this round's spec — they're all `AgentCallEvent`/`Event` consumers, not separate pipelines.

## Testing strategy for AI quality

See [AI_TESTING.md](AI_TESTING.md).

## API versioning

All module routers mount under `/api/v1/<module>` from day one (`app/main.py`) — versioned from
the first route, not retrofitted later, because a multi-tenant enterprise API can't break existing
hospital/EMR integrations on a minor release.

## Extensibility

New agent = new file in `app/ai/agents/` + one entry in `INTENT_AGENT_MAP` (or direct dispatch via
`request.task`). New intent = new pattern list in `INTENT_PATTERNS` + a routing-table entry. New
tool = new `Tool` subclass + one `registry.register()` call. New event = a new constant in
`app/core/events.py` + whichever agent/module wants to subscribe — none of these require editing
the orchestrator's core `handle_request()` method. New memory type = new `scope` value in
`ai_memory_facts` + a consent category; no schema migration required for the common case.

Future modules named in this round's spec — clinical decision support, remote patient
monitoring, wearable/medical-device integration, robot-assisted interpretation, smart glasses, OR
and ambulance communication, health information exchange — all fit the same shape: a new agent (or
a new `STTProvider`/`AudioProcessor` implementation for a new device's audio format) routed by a
new intent or a new `task` override, never a change to the orchestrator's pipeline steps
themselves. Clinical decision support in particular reuses Clinical Intelligence's existing
"explanatory only, clinician confirms" constraint rather than introducing a new governance rule.
