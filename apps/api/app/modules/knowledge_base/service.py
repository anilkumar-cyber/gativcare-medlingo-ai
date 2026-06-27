"""No knowledge base table/ingestion pipeline exists yet (Phase 3 continued) -- returning []
is the honest answer ("nothing retrieved") rather than raising, so the orchestrator pipeline
doesn't crash on every request just because no org has uploaded documents yet. The Knowledge
Agent already handles an empty list correctly (flags no_retrieval_hits instead of guessing)."""


async def search_articles(query: str) -> list[str]:
    return []
