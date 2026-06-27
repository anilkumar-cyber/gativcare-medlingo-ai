"""Single chokepoint for patient-scoped AI memory. No agent or engine queries
AIMemoryFact directly -- everything goes through recall()/recall_all()/remember() so the
consent check can never be accidentally skipped. See docs/AI_ARCHITECTURE.md #memory-architecture."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_memory.models import MEMORY_SCOPES, AIMemoryFact, Consent


class ConsentRequiredError(Exception):
    pass


async def _active_consent(session: AsyncSession, patient_id: uuid.UUID, scope: str) -> Consent | None:
    result = await session.execute(
        select(Consent).where(
            Consent.patient_id == patient_id,
            Consent.scope == scope,
            Consent.revoked_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def recall(session: AsyncSession, patient_id: uuid.UUID, scope: str) -> list[dict]:
    """Returns [] if consent for this scope was never granted or has been revoked --
    revocation must make prior facts unreadable immediately, not just block new writes."""
    consent = await _active_consent(session, patient_id, scope)
    if consent is None:
        return []

    result = await session.execute(
        select(AIMemoryFact).where(
            AIMemoryFact.patient_id == patient_id,
            AIMemoryFact.scope == scope,
        )
    )
    return [row.fact for row in result.scalars().all()]


async def recall_all(session: AsyncSession, patient_id: uuid.UUID) -> dict[str, list[dict]]:
    return {scope: await recall(session, patient_id, scope) for scope in MEMORY_SCOPES}


async def remember(
    session: AsyncSession,
    *,
    org_id: uuid.UUID,
    patient_id: uuid.UUID,
    scope: str,
    fact: dict,
    source_turn_id: uuid.UUID | None = None,
) -> AIMemoryFact:
    consent = await _active_consent(session, patient_id, scope)
    if consent is None:
        raise ConsentRequiredError(f"no active consent for scope={scope!r}, patient={patient_id}")

    row = AIMemoryFact(
        id=uuid.uuid4(),
        org_id=org_id,
        patient_id=patient_id,
        scope=scope,
        fact=fact,
        source_turn_id=source_turn_id,
        consent_id=consent.id,
        created_at=datetime.utcnow(),
    )
    session.add(row)
    await session.flush()
    return row


async def grant_consent(session: AsyncSession, *, patient_id: uuid.UUID, scope: str) -> Consent:
    consent = Consent(id=uuid.uuid4(), patient_id=patient_id, scope=scope, granted_at=datetime.utcnow())
    session.add(consent)
    await session.flush()
    return consent


async def revoke_consent(session: AsyncSession, *, patient_id: uuid.UUID, scope: str) -> None:
    consent = await _active_consent(session, patient_id, scope)
    if consent is not None:
        consent.revoked_at = datetime.utcnow()
        await session.flush()
