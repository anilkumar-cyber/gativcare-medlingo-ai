# AI Quality Testing Strategy

AI behavior isn't unit-testable the way CRUD endpoints are — correctness is "is this a good
medical interpretation," not "does this return 200." Four layers, each catching a different
failure mode:

## 1. Unit tests (deterministic, run on every PR)

Everything that isn't an LLM call: `SafetyAgent.precheck()`/`postcheck()` regex matching,
`ai_memory.service` consent enforcement (revoke → recall returns empty, no active consent →
`remember()` raises `ConsentRequiredError`), `MedLingoOrchestrator` control flow with a mocked
`LLMProvider`/`STTProvider`/`TTSProvider` (assert the pipeline steps run in order, assert an
emergency-pattern match triggers `_dispatch_emergency_notification` before the task agent runs).
These are real `pytest` + `pytest-asyncio` tests against the code already in `apps/api`.

## 2. Golden conversation sets (per language pair, run nightly)

Curated input/expected-interpretation pairs covering: common symptom descriptions, drug names
(must preserve pronunciation/spelling), emergency phrases (must trigger Safety Agent precheck),
culturally sensitive phrasing (family involvement, religious topics). Scored by a combination of:
exact-match on must-preserve terms (drug names, dosages), semantic similarity for the rest, and a
clinician-reviewed pass/fail sample. Regressions block release for that language pair.

## 3. Safety red-team set (run on every change to safety_agent.py or any agent prompt)

Adversarial inputs designed to make the system: state a definitive diagnosis, recommend a specific
dosage, miss an emergency phrase, leak one patient's memory into another patient's session
(cross-tenant), or bypass the voice-clone consent check. Every item must fail safely (disclaimer
added / escalated / refused) — any pass is a release blocker, not a "known issue."

## 4. Production monitoring (continuous)

The `app/core/observability.py` event stream (`AgentCallEvent`) feeds: confidence-score
distribution per agent/language, `needs_human_review` rate, emergency-detection rate vs. false
positives (tracked via human escalation outcomes), and latency against the <1s voice-pipeline
target. A sustained rise in `needs_human_review` rate for one language pair is the signal to add
that pair to the golden set in layer 2, not just a dashboard curiosity.

## What's explicitly out of scope for Phase 1/2

Automated medical-accuracy grading against a clinical ground truth requires licensed-clinician
review capacity and a labeled dataset — that's a process to stand up alongside the first pilot
hospital, not something to fake with an LLM-as-judge and call validated.
