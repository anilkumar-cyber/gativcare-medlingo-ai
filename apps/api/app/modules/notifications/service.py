"""Phase 3: implement email/SMS/push/in-app dispatch. notify() is called directly by
app.ai.agents.orchestrator for emergency escalation and human-review flagging -- this signature
is load-bearing, not just a placeholder."""


async def notify(user_id, *, template: str, metadata: dict | None = None):
    raise NotImplementedError
