"""
Agronomy Agent (Upgraded with RAG)
====================================

Smart farming and crop advisory agent with Retrieval-Augmented Generation.

Enhanced capabilities:
    - Semantic document retrieval for crop knowledge
    - RAG-powered recommendations from research papers and reports
    - Multi-source data integration
    - Streaming and non-streaming execution modes

Examples:
    >>> from apps.shared_ai.ai.llm_factory import get_llm
    >>> llm = get_llm()
    >>> agent = AgronomyAgent(llm)
    >>> response = await agent.chat("What crop is best for Khuzestan with 300mm rainfall?")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool

from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.rag_tools import (
    get_knowledge_base_stats,
    get_rag_context,
    search_knowledge_base,
    upload_document,
)
from apps.ai_agents.tools.registry import (
    calculate_irrigation,
    get_crop_recommendation,
    get_weather_data,
)

logger = logging.getLogger(__name__)

# =========================================================================
# System Prompt
# =========================================================================

AGRONOMY_PROMPT: str = """
You are an expert agronomy advisor for the Econojin platform.

Your responsibilities:
1. Provide crop recommendations based on climate, soil, and water availability
2. Analyze farming conditions and suggest optimal planting schedules
3. Answer agricultural questions using both your knowledge and retrieved documents
4. Estimate yields and calculate resource requirements

Guidelines:
- Use get_weather_data and get_crop_recommendation tools when data is needed
- Use calculate_irrigation for precise water requirement estimates
- **Use get_rag_context to retrieve relevant agricultural documents and research**
  This is your primary source for evidence-based recommendations
- search_knowledge_base to find specific agricultural information
- Always cite sources from retrieved documents when available
- If a tool returns an error, fall back to your general knowledge
- Provide actionable, practical advice tailored to the user's region

Available tools:
- get_weather_data: Fetch weather forecast for a location
- get_crop_recommendation: Get crop recommendations for an area
- calculate_irrigation: Calculate water requirements for a crop
- get_rag_context: Retrieve relevant information from the knowledge base
- search_knowledge_base: Search the document repository
- upload_document: Upload new agricultural reference documents

Note: Always prefer evidence from retrieved documents over general knowledge.
"""


class AgronomyAgent:
    """Agricultural advisory agent powered by RAG.

    Integrates weather data, crop models, and a document knowledge
    base to provide evidence-backed farming recommendations.

    Attributes:
        llm: The language model instance.
        tools: LangChain tools available to the agent.
        builder: ModularAgentBuilder for the LangGraph workflow.
        graph: Compiled LangGraph execution graph.
    """

    def __init__(self, llm: Any) -> None:
        """Initialize the agronomy agent.

        Args:
            llm: A LangChain-compatible chat model.
        """
        self.llm: Any = llm
        self.tools: List[BaseTool] = [
            get_weather_data,
            get_crop_recommendation,
            calculate_irrigation,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats,
        ]

        self.builder: ModularAgentBuilder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=AGRONOMY_PROMPT,
        )
        self.graph: Any = self.builder.build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Process a user message and return an AI response.

        Args:
            user_message: The user's question or request.
            context: Optional context dict (e.g., user profile, farm data).

        Returns:
            Generated response string.

        Raises:
            RuntimeError: If the agent fails to produce a response.
        """
        logger.info(
            "AgronomyAgent: processing message (length=%d)", len(user_message)
        )

        result: str = await self.builder.run(user_message, context)

        if not result:
            logger.warning("AgronomyAgent: empty response")
            return "I could not process your request. Please try again."

        return result

    # ------------------------------------------------------------------
    # RAG-specific helpers
    # ------------------------------------------------------------------

    async def answer_with_context(
        self,
        question: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Answer a question with explicit RAG context retrieval.

        Retrieves relevant documents, then generates a response.

        Args:
            question: The user's question.
            top_k: Number of documents to retrieve.

        Returns:
            Dict with keys: answer, sources, context_docs.
        """
        # Retrieve context
        from apps.shared_ai.rag.retriever import get_retriever

        retriever = get_retriever(top_k=top_k)
        context_docs: List[Dict[str, Any]] = retriever.retrieve(
            query=question, top_k=top_k
        )
        context_text: str = retriever.retrieve_context(
            query=question, top_k=top_k, format_as_text=True
        )

        # Build prompt with context
        enriched_prompt: str = (
            f"Use the following retrieved documents to answer the question.\n\n"
            f"{context_text}\n\n"
            f"Question: {question}\n\n"
            f"Provide a detailed answer with citations to the source documents."
        )

        answer: str = await self.chat(enriched_prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "text": doc.get("text", "")[:200],
                    "score": doc.get("score", 0.0),
                    "metadata": doc.get("metadata", {}),
                }
                for doc in context_docs
            ],
            "context_docs": context_docs,
        }

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------

    def ingest_agricultural_document(self, file_path: str) -> int:
        """Ingest an agricultural document into the RAG knowledge base.

        Args:
            file_path: Path to the document file (PDF, TXT, MD).

        Returns:
            Number of chunks ingested.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        from apps.shared_ai.rag.document_loader import DocumentLoader

        loader: DocumentLoader = DocumentLoader()
        chunks: List[Dict[str, Any]] = loader.load_file(
            file_path, metadata={"category": "agriculture", "file_path": file_path}
        )

        from apps.shared_ai.rag.vector_store import get_vector_store

        store = get_vector_store()
        texts: List[str] = [c["content"] for c in chunks]
        metadata_list: List[Dict[str, Any]] = [
            {"source": file_path, **c["metadata"]} for c in chunks
        ]

        store.add_documents(texts=texts, metadata_list=metadata_list)

        logger.info("Ingested %d chunks from '%s'", len(chunks), file_path)
        return len(chunks)

    # ------------------------------------------------------------------
    # Specialized crop analysis
    # ------------------------------------------------------------------

    async def analyze_crop_suitability(
        self,
        province: str,
        soil_type: str,
        water_availability: float,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """Perform a comprehensive crop suitability analysis for a region.

        Args:
            province: Province or region name.
            soil_type: Soil classification.
            water_availability: Available water in mm/year.
            latitude: Geographic latitude.
            longitude: Geographic longitude.

        Returns:
            Comprehensive analysis dict with recommendations.
        """
        logger.info(
            "Analyzing crop suitability for %s (%.2f, %.2f)",
            province,
            latitude,
            longitude,
        )

        # Get weather data
        weather: Any = await get_weather_data.ainvoke(
            {"latitude": latitude, "longitude": longitude, "days": 30}
        )

        # Get crop recommendation
        crops: Any = await get_crop_recommendation.ainvoke(
            {"province": province, "soil_type": soil_type, "water_availability": water_availability}
        )

        # Search knowledge base for regional best practices
        kb_results: Any = await search_knowledge_base.ainvoke(
            {"query": f"agricultural best practices for {province} {soil_type} crops"}
        )

        # Generate comprehensive analysis
        analysis_question: str = (
            f"Analyze crop suitability for {province} province.\n"
            f"Soil type: {soil_type}\n"
            f"Water availability: {water_availability} mm/year\n"
            f"Weather data: {weather}\n"
            f"Recommended crops: {crops}\n"
            f"Knowledge base findings: {kb_results}\n\n"
            f"Provide: 1) Top 3 recommended crops with justification, "
            f"2) Expected yields, 3) Key risks, 4) Best planting windows."
        )

        analysis: str = await self.chat(analysis_question)

        return {
            "province": province,
            "recommended_crops": crops,
            "weather_summary": str(weather)[:500] if weather else "N/A",
            "analysis": analysis,
        }
