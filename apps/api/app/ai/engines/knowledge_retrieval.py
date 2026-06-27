"""KnowledgeRetrievalEngine — see docs/ARCHITECTURE.md #1 for this engine's place in the pipeline."""

from app.ai.engines import Engine


class KnowledgeRetrievalEngine(Engine):
    name = "knowledge_retrieval"

    async def run(self, payload: dict) -> dict:
        raise NotImplementedError
