"""Human-in-the-Loop (HITL). When AI confidence drops below threshold or the Safety Agent flags
clinical complexity, invite a qualified human interpreter/coordinator into the session rather
than continuing AI-only. should_escalate() is pure and unit-testable; request_human_handoff()
is the Phase 3 seam into real session/notification state.
"""

from dataclasses import dataclass

DEFAULT_CONFIDENCE_THRESHOLD = 0.55
COMPLEXITY_FLAGS = {"needs_human_review", "diagnosis_shaped_disclaimer_added", "emergency_flagged", "insufficient_data"}


@dataclass
class EscalationDecision:
    should_escalate: bool
    reason: str | None = None


def should_escalate(
    *, confidence: float, flags: list[str], org_confidence_threshold: float | None = None
) -> EscalationDecision:
    threshold = org_confidence_threshold if org_confidence_threshold is not None else DEFAULT_CONFIDENCE_THRESHOLD

    matched_flags = COMPLEXITY_FLAGS.intersection(flags)
    if matched_flags:
        return EscalationDecision(should_escalate=True, reason=f"flagged: {', '.join(sorted(matched_flags))}")

    if confidence < threshold:
        return EscalationDecision(should_escalate=True, reason=f"confidence {confidence:.2f} below threshold {threshold:.2f}")

    return EscalationDecision(should_escalate=False)


async def request_human_handoff(*, conversation_session_id, reason: str):
    """Phase 3: marks the session as awaiting a human interpreter/coordinator, notifies the
    available pool, and surfaces a 'human joining' indicator to all participants. Until a human
    accepts, the AI continues assisting -- HITL augments, it doesn't pause, communication."""
    raise NotImplementedError
