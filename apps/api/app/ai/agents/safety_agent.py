"""Safety Agent — the only agent every response passes through. Three jobs: emergency detection
(pre-dispatch), disclaimer injection + confidence/hallucination flagging (post-dispatch). See
docs/AI_ARCHITECTURE.md #safety-agent-detail.

Pattern-based and provider-signal-based by design — no trained classifier required to ship this;
an LLM self-check or a real classifier can replace/augment EMERGENCY_PATTERNS and the confidence
heuristic later without changing the Agent interface."""

import re
from dataclasses import dataclass

from app.ai.agents import Agent, AgentResponse

# Representative, not exhaustive — production lexicon is org/language configurable via
# organizations.ai_config, not hardcoded per docs/ARCHITECTURE.md tenancy rules.
EMERGENCY_PATTERNS = [
    r"\bchest pain\b",
    r"\bcan'?t breathe\b",
    r"\bdifficulty breathing\b",
    r"\bsevere bleeding\b",
    r"\bunconscious\b",
    r"\bsuicid(e|al)\b",
    r"\bself[- ]harm\b",
    r"\bheart attack\b",
    r"\bstroke\b",
    r"\bnot breathing\b",
    r"\bsevere allergic reaction\b",
    r"\banaphylaxis\b",
]

DIAGNOSIS_SHAPED_PATTERNS = [
    r"\byou have\b.*\b(cancer|diabetes|disease|syndrome)\b",
    r"\bi diagnose\b",
    r"\byour diagnosis is\b",
    r"\btake \d+\s?(mg|ml|mcg)\b",
]

CONFIRM_WITH_PHYSICIAN_DISCLAIMER = (
    "This information is for understanding only and is not a diagnosis or prescription — "
    "please confirm with your treating physician."
)

LOW_CONFIDENCE_THRESHOLD = 0.55

_emergency_re = re.compile("|".join(EMERGENCY_PATTERNS), re.IGNORECASE)
_diagnosis_re = re.compile("|".join(DIAGNOSIS_SHAPED_PATTERNS), re.IGNORECASE)


@dataclass
class SafetyPrecheckResult:
    is_emergency: bool
    matched_pattern: str | None = None


class SafetyAgent(Agent):
    name = "safety"
    SYSTEM_PROMPT = "You review content for emergency signals, diagnosis-shaped overreach, and confidence."

    def precheck(self, text: str, *, language: str | None = None) -> SafetyPrecheckResult:
        match = _emergency_re.search(text or "")
        return SafetyPrecheckResult(is_emergency=bool(match), matched_pattern=match.group(0) if match else None)

    def postcheck(self, response: AgentResponse) -> AgentResponse:
        if _diagnosis_re.search(response.content or ""):
            response.content = f"{response.content}\n\n{CONFIRM_WITH_PHYSICIAN_DISCLAIMER}"
            response.flags.append("diagnosis_shaped_disclaimer_added")

        if response.confidence < LOW_CONFIDENCE_THRESHOLD:
            response.flags.append("needs_human_review")

        return response

    async def handle(self, request: dict) -> AgentResponse:
        # Safety is invoked directly by the orchestrator (precheck/postcheck), not dispatched
        # to as a task agent — handle() exists only to satisfy the Agent interface.
        raise NotImplementedError("SafetyAgent is invoked via precheck()/postcheck(), not handle()")
