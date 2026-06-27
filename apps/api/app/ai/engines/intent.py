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
    "hospital": [r"\bhospitals?\b", r"\bwards?\b", r"\bdepartments?\b"],
    "doctor": [r"\bdoctors?\b", r"\bsurgeons?\b", r"\bspecialists?\b", r"\bphysicians?\b"],
    "medication": [r"\bmedicat", r"\bdrugs?\b", r"\bdosages?\b", r"\bprescriptions?\b"],
    "billing": [r"\bbill(ing|s)?\b", r"\binvoices?\b", r"\bpayments?\b"],
    "navigation": [r"\bwhere is\b", r"\bdirections?\b", r"\bhow do i get\b"],
    "recovery": [r"\brecovery\b", r"\brehab", r"\bdischarge\b"],
    "follow_up": [r"\bfollow[- ]up\b", r"\bnext visit\b"],
    "complaint": [r"\bcomplain", r"\bunhappy\b", r"\bdissatisfied\b"],
    "feedback": [r"\bfeedback\b", r"\breviews?\b", r"\bratings?\b"],
    "administration": [r"\baccounts?\b", r"\bsettings?\b", r"\bpermissions?\b", r"\buser management\b"],
    "document_upload": [r"\bupload", r"\battach(ment)?s?\b"],
    "medical_report": [r"\breports?\b", r"\bmri\b", r"\bct scans?\b", r"\bblood tests?\b", r"\bx-?rays?\b", r"\blab results?\b"],
    "video_consultation": [r"\bvideo calls?\b", r"\bvideo consult", r"\bzoom\b", r"\bmeeting links?\b"],
    "voice_call": [r"\bphone calls?\b", r"\bvoice calls?\b", r"\bcall me\b"],
    "medical_question": [r"\bsymptoms?\b", r"\bdiagnos", r"\btreatments?\b", r"\bdiseases?\b", r"\bconditions?\b"],
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
