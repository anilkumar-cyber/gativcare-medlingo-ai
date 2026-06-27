"""Phase 3: vector-store-backed retrieval over guidelines/hospital/drug/FAQ content. Returns a
list of passage strings; app.ai.agents.knowledge_agent.KnowledgeAgent cites them by index."""


async def search_articles(query: str) -> list[str]:
    raise NotImplementedError
