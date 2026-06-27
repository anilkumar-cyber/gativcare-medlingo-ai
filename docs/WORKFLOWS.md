# Workflows & Journeys

## Patient journey (maps to `medical_cases.stage`)

```
inquiry -> qualification -> records_upload -> clinical_review -> second_opinion ->
treatment_planning -> quotation -> insurance -> visa -> travel_planning -> airport_pickup ->
hotel -> admission -> consultation -> diagnosis -> treatment -> surgery -> recovery ->
discharge -> follow_up -> long_term_care
```

Each stage transition is an event (`medical_case.stage_changed`, published by
`app/core/workflow_engine.py::WorkflowEngine.advance()`) other modules subscribe to — e.g.
`notifications` sends a status update, `analytics` logs a funnel metric, `travel`/`visa`/
`insurance` modules only activate once the case reaches their relevant stage. This keeps
`medical_cases` from becoming a god-object that every module reaches into. The stage *sequence*
itself is the default list in `WorkflowEngine.DEFAULT_STAGE_SEQUENCE`, overridable per org via
`organizations.ai_config.workflow_overrides` — "organizations should be able to customize
workflows" without a code change.

## Conversation/AI orchestration workflow (per turn)

1. Input arrives (audio chunk or text) on a `conversation_session` via WebSocket or REST.
2. `MedLingoOrchestrator.handle_request()` runs the full pipeline — see
   [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md#master-orchestrator-workflow): intent detection picks
   which of the 14 agents run, results are merged, a translation pass and optional speech
   synthesis follow.
3. Context Engine loads: org AI config, patient's `ai_memory_facts` (consent-checked), case stage,
   prior turns in this session.
4. Output turn is persisted (`conversation_turns`); lifecycle events are published (not called
   directly) for anything reactive — see the event catalog below.
5. Response streamed back (text + optionally synthesized voice).

Safety Agent runs at step 2 both before and after agent dispatch: precheck flags emergency-keyword
content and forces the Emergency agent regardless of detected intent; postcheck flags anything
resembling a diagnosis/prescription claim for a "confirm with your physician" disclaimer and
triggers Human-in-the-Loop escalation on low confidence — see
[AI_ARCHITECTURE.md](AI_ARCHITECTURE.md#human-in-the-loop-hitl).

## Event catalog

`app/core/events.py` (representative, not exhaustive — new events are added as new modules need
them):

| Event | Published by | Typically reacted to by |
|---|---|---|
| `patient.registered` | patients module (Phase 3) | notifications, analytics |
| `appointment.booked` | appointments module (Phase 3) | notifications |
| `report.uploaded` | medical_reports module (Phase 3) | Automation Agent → coordinator notification |
| `translation.started` / `translation.completed` | orchestrator's translation pass | analytics (latency/volume) |
| `video_consultation.started` | video_consultation module (Phase 3) | notifications, analytics |
| `prescription.created` | clinical_documentation (Phase 3) | notifications, pharmacy workflows |
| `hospital.assigned` | medical_tourism/patients (Phase 3) | notifications |
| `treatment.completed` | patients module (Phase 3) | Workflow Agent (next stage), follow-up scheduling |
| `follow_up.scheduled` | appointments module (Phase 3) | notifications |
| `medical_case.stage_changed` | `WorkflowEngine.advance()` | Automation Agent, analytics, stage-gated modules (travel/visa/insurance) |
| `ai.needs_human_review` | orchestrator's HITL check | Automation Agent → clinician notification |
| `ai.emergency_detected` | orchestrator's safety precheck | Automation Agent → emergency staff notification |

The Automation Agent (`app/ai/agents/automation_agent.py`) is the default subscriber for the
AI-originated events; module-to-module reactions (e.g. `report.uploaded` → coordinator alert) land
in Phase 3 as each module is implemented, subscribing to events that already exist rather than
the orchestrator/workflow engine being changed to know about them.

## Role-based business workflows (representative)

**New international patient inquiry**
`medical_tourism.qualify_lead()` → creates `patient` + `medical_case(stage=inquiry)` →
Patient Coordinator assigned → `notifications` alerts coordinator → patient uploads records via
portal → `medical_reports.attach_report()` → stage → `clinical_review`.

**Doctor consultation with interpretation**
Receptionist checks in patient → `appointments` marks arrived → `conversations.start_session()`
linked to `medical_case_id` → doctor & patient speak, AI interprets in real time (role-aware:
doctor gets clinical phrasing, patient gets plain-language phrasing of the *same* clinical content)
→ session ends → `clinical_documentation` offers AI-drafted note → doctor reviews/edits/signs
(AI never auto-finalizes a clinical note).

**Insurance + travel coordination (parallel, not sequential)**
Once `quotation` stage is reached, `insurance.check_coverage()` and `travel`/`visa` workflows can
run concurrently — the case-stage model allows fan-out, it isn't a strict single-file pipeline.

## Why workflows are event-driven, not hardcoded call chains

A hardcoded chain (`appointments` calling `notifications` calling `analytics` directly) means every
new module insertion requires editing existing modules. An event bus (Redis pub/sub at this stage;
swappable for a message queue later) means new modules subscribe to existing events without
existing modules knowing they exist — required for "every module must be independent" to survive
contact with 30+ modules.
