"""Intent Engine -- classifies a request into one of the PRD's 20 intent categories so the
orchestrator dispatches only the agents that intent actually needs. Keyword/regex first pass by
design (cheap, deterministic, testable); ambiguous/unmatched text falls back to "unknown", which
routes to the Knowledge agent rather than guessing. An LLM-based classifier can replace/augment
this later without changing the Engine interface or the orchestrator's routing table.
"""

import re

from app.ai.engines import Engine

INTENT_PATTERNS: dict[str, list[str]] = {
    "emergency": [r"\bchest pain\b", r"\bcan'?t breathe\b", r"\bsevere bleeding\b", r"\bstroke\b", r"\bemergency\b"],
    "appointment": [r"\bappointment\b", r"\bbook(ing)?\b", r"\breschedul", r"\bschedule\b"],
    "translation": [r"\btranslat", r"\binterpret"],
    "travel": [r"\bflight\b", r"\bvisa\b", r"\btravel\b", r"\bairport\b", r"\bhotel\b"],
    "insurance": [r"\binsurance\b", r"\bclaim\b", r"\bcoverage\b", r"\bpre-?auth"],
    "hospital": [r"\bhospital\b", r"\bward\b", r"\bdepartment\b"],
    "doctor": [r"\bdoctor\b", r"\bsurgeon\b", r"\bspecialist\b", r"\bphysician\b"],
    "medication": [r"\bmedicat", r"\bdrug\b", r"\bdosage\b", r"\bprescription\b"],
    "billing": [r"\bbill(ing)?\b", r"\binvoice\b", r"\bpayment\b"],
    "navigation": [r"\bwhere is\b", r"\bdirections?\b", r"\bhow do i get\b"],
    "recovery": [r"\brecovery\b", r"\brehab", r"\bdischarge\b"],
    "follow_up": [r"\bfollow[- ]up\b", r"\bnext visit\b"],
    "complaint": [r"\bcomplain", r"\bunhappy\b", r"\bdissatisfied\b"],
    "feedback": [r"\bfeedback\b", r"\breview\b", r"\brating\b"],
    "administration": [r"\baccount\b", r"\bsettings\b", r"\bpermission\b", r"\buser management\b"],
    "document_upload": [r"\bupload\b", r"\battach(ment)?\b"],
    "medical_report": [r"\breport\b", r"\bmri\b", r"\bct scan\b", r"\bblood test\b", r"\bx-?ray\b", r"\blab result"],
    "video_consultation": [r"\bvideo call\b", r"\bvideo consult", r"\bzoom\b", r"\bmeeting link\b"],
    "voice_call": [r"\bphone call\b", r"\bvoice call\b", r"\bcall me\b"],
    "medical_question": [r"\bsymptom", r"\bdiagnos", r"\btreatment\b", r"\bdisease\b", r"\bcondition\b"],
}

# Checked first, in this order, because an emergency match must win over any other intent
# (e.g. "chest pain during my follow-up appointment" routes to emergency, not follow_up).
PRIORITY_ORDER = ["emergency"] + [k for k in INTENT_PATTERNS if k != "emergency"]

_compiled = {intent: re.compile("|".join(patterns), re.IGNORECASE) for intent, patterns in INTENT_PATTERNS.items()}


class IntentEngine(Engine):
    name = "intent"

    async def run(self, payload: dict) -> dict:
        text = payload.get("text", "") or ""
        for intent in PRIORITY_ORDER:
            if _compiled[intent].search(text):
                return {"intent": intent, "confidence": 0.8}
        return {"intent": "unknown", "confidence": 0.0}
