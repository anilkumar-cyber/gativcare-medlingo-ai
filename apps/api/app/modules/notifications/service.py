"""No email/SMS/push provider is wired yet (Integrations are explicitly out of scope until real
vendor accounts exist -- see README status). notify() logs structurally instead of raising, so
emergency/HITL escalation paths in the orchestrator don't crash; swapping the log line for a real
Twilio/SES/FCM call later doesn't change this function's signature or any caller."""

import logging

logger = logging.getLogger("notifications")


async def notify(user_id, *, template: str, metadata: dict | None = None) -> None:
    logger.info("notification dispatched", extra={"user_id": str(user_id), "template": template, "metadata": metadata or {}})
