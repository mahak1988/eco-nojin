"""
Tourism Agent
==============

Intelligent tourism and travel guide agent for the Econojin platform.

Capabilities:
    - Destination recommendations based on user preferences
    - Travel itinerary planning with weather-aware scheduling
    - Local attraction and cultural event information
    - Budget estimation and optimization
    - Multi-modal travel route planning

Examples:
    >>> from apps.shared_ai.ai.llm_factory import get_llm
    >>> llm = get_llm()
    >>> agent = TourismAgent(llm)
    >>> response = await agent.chat("Plan a 3-day trip to Isfahan with historical focus")
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

logger = logging.getLogger(__name__)

# =========================================================================
# System Prompt
# =========================================================================

TOURISM_PROMPT: str = """
You are an expert tourism and travel guide for the Econojin platform.

Your responsibilities:
1. Recommend travel destinations based on preferences, season, and budget
2. Create personalized multi-day itineraries for cities and regions
3. Provide information about historical sites, cultural events, and local cuisine
4. Estimate travel costs including accommodation, transport, food, and activities
5. Advise on best travel seasons, weather considerations, and travel safety
6. Recommend eco-tourism and agricultural tourism opportunities

Guidelines:
- Use get_rag_context to retrieve travel guides, historical information, and local knowledge
- search_knowledge_base to find specific destination information, hotels, or attractions
- Tailor all recommendations to the user's budget, interests, and travel dates
- Include practical details: opening hours, ticket prices, transportation options
- Consider seasonal factors and weather conditions
- Highlight unique cultural experiences and local specialties
- Provide safety tips and cultural etiquette advice
- If a tool returns an error, fall back to your general travel knowledge
- Always cite sources when using retrieved documents

Available tools:
- get_rag_context: Retrieve relevant travel and destination information
- search_knowledge_base: Search the knowledge base for specific topics
- upload_document: Upload new travel guides and reference materials
- get_knowledge_base_stats: View knowledge base statistics

Note: Your recommendations should be practical, detailed, and culturally sensitive.
"""


class TourismAgent:
    """Intelligent tourism and travel planning agent.

    Provides personalized travel recommendations, itinerary planning,
    and destination information powered by RAG document retrieval.

    Attributes:
        llm: The language model instance.
        tools: LangChain tools for the agent workflow.
        builder: ModularAgentBuilder for the LangGraph workflow.
        graph: Compiled LangGraph execution graph.
    """

    def __init__(self, llm: Any) -> None:
        """Initialize the tourism agent.

        Args:
            llm: A LangChain-compatible chat model.
        """
        self.llm: Any = llm
        self.tools: List[BaseTool] = [
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats,
        ]

        self.builder: ModularAgentBuilder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=TOURISM_PROMPT,
        )
        self.graph: Any = self.builder.build()

        logger.info("TourismAgent initialized")

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
            context: Optional context dict (e.g., user preferences, location).

        Returns:
            Generated response string.
        """
        logger.info(
            "TourismAgent: processing message (length=%d)", len(user_message)
        )

        result: str = await self.builder.run(user_message, context)

        if not result:
            logger.warning("TourismAgent: empty response")
            return "I could not process your travel query. Please try again."

        return result

    # ------------------------------------------------------------------
    # Destination recommendation
    # ------------------------------------------------------------------

    async def recommend_destinations(
        self,
        preferences: Dict[str, Any],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Recommend destinations based on user preferences.

        Args:
            preferences: Dict with keys like:
                - budget: Budget range (e.g., "low", "medium", "high")
                - interests: List of interests (e.g., ["history", "nature"])
                - season: Preferred travel season
                - duration: Trip duration in days
                - travelers: Number of travelers
            top_k: Number of destinations to recommend.

        Returns:
            Dict with recommended destinations and reasoning.
        """
        budget: str = preferences.get("budget", "medium")
        interests: List[str] = preferences.get("interests", ["history"])
        season: str = preferences.get("season", "spring")
        duration: int = preferences.get("duration", 3)
        travelers: int = preferences.get("travelers", 2)

        # Retrieve relevant destination guides
        from apps.shared_ai.rag.retriever import get_retriever

        retriever = get_retriever(top_k=top_k * 2)
        interest_query: str = " ".join(interests)
        context_text: str = retriever.retrieve_context(
            query=f"best travel destinations for {interest_query} in {season} budget {budget}",
            top_k=top_k * 2,
            format_as_text=True,
        )

        # Generate recommendations
        rec_question: str = (
            f"Based on the following travel context and user preferences, "
            f"recommend {top_k} destinations:\n\n"
            f"Context:\n{context_text}\n\n"
            f"User Preferences:\n"
            f"- Budget: {budget}\n"
            f"- Interests: {', '.join(interests)}\n"
            f"- Season: {season}\n"
            f"- Duration: {duration} days\n"
            f"- Travelers: {travelers}\n\n"
            f"For each destination, provide:\n"
            f"1) Name and brief description\n"
            f"2) Why it matches the user's preferences\n"
            f"3) Estimated cost range\n"
            f"4) Best time to visit\n"
            f"5) Top 3 attractions\n"
            f"6) Practical tips"
        )

        recommendations: str = await self.chat(rec_question)

        return {
            "preferences": preferences,
            "recommendations": recommendations,
            "context_used": context_text[:500] if isinstance(context_text, str) else "",
        }

    # ------------------------------------------------------------------
    # Itinerary planning
    # ------------------------------------------------------------------

    async def plan_itinerary(
        self,
        destination: str,
        duration_days: int,
        interests: Optional[List[str]] = None,
        budget: str = "medium",
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Plan a detailed multi-day travel itinerary.

        Args:
            destination: City or region name.
            duration_days: Number of days for the trip.
            interests: List of interests (history, food, nature, etc.).
            budget: Budget level ("low", "medium", "high").
            start_date: Optional start date in ISO format (YYYY-MM-DD).

        Returns:
            Dict with detailed day-by-day itinerary.
        """
        interests = interests or ["history", "culture", "food"]

        # Retrieve local guides
        from apps.shared_ai.rag.retriever import get_retriever

        retriever = get_retriever(top_k=10)
        local_context: str = retriever.retrieve_context(
            query=f"{destination} travel guide attractions restaurants "
                  f"{' '.join(interests)} budget {budget}",
            top_k=10,
            format_as_text=True,
        )

        date_context: str = ""
        if start_date:
            date_context = f"Travel dates: starting {start_date}, for {duration_days} days.\n"

        itinerary_question: str = (
            f"Create a detailed {duration_days}-day itinerary for {destination}.\n"
            f"{date_context}"
            f"Interests: {', '.join(interests)}\n"
            f"Budget level: {budget}\n"
            f"Local travel context:\n{local_context}\n\n"
            f"For each day, provide:\n"
            f"- Morning activity (with time recommendation)\n"
            f"- Afternoon activity\n"
            f"- Evening activity / dinner recommendation\n"
            f"- Transportation between locations\n"
            f"- Estimated costs for the day\n"
            f"- Practical tips (dress code, tickets, etc.)\n\n"
            f"Also include:\n"
            f"- Total trip cost estimate\n"
            f"- Packing recommendations\n"
            f"- Safety and cultural etiquette tips"
        )

        itinerary: str = await self.chat(itinerary_question)

        return {
            "destination": destination,
            "duration_days": duration_days,
            "interests": interests,
            "budget": budget,
            "start_date": start_date,
            "itinerary": itinerary,
        }

    # ------------------------------------------------------------------
    # Local information
    # ------------------------------------------------------------------

    async def get_local_info(
        self,
        location: str,
        info_type: str = "general",
    ) -> Dict[str, Any]:
        """Get detailed information about a specific location.

        Args:
            location: City, region, or attraction name.
            info_type: Type of information:
                - "general": Overview and key facts
                - "history": Historical background
                - "food": Local cuisine and restaurants
                - "events": Upcoming events and festivals
                - "transport": Transportation options
                - "accommodation": Hotels and lodging
                - "safety": Safety tips and advisories

        Returns:
            Dict with categorized information about the location.
        """
        from apps.shared_ai.rag.retriever import get_retriever

        retriever = get_retriever(top_k=8)
        local_context: str = retriever.retrieve_context(
            query=f"{location} {info_type} travel guide information",
            top_k=8,
            format_as_text=True,
        )

        info_question: str = (
            f"Provide detailed {info_type} information about {location}.\n"
            f"Context:\n{local_context}\n\n"
            f"Format the response with clear sections and practical details."
        )

        info: str = await self.chat(info_question)

        return {
            "location": location,
            "info_type": info_type,
            "information": info,
            "sources_consulted": len(local_context) > 0 if isinstance(local_context, str) else False,
        }

    # ------------------------------------------------------------------
    # Budget estimation
    # ------------------------------------------------------------------

    async def estimate_trip_cost(
        self,
        destination: str,
        duration_days: int,
        travelers: int = 2,
        style: str = "medium",
        include_flights: bool = False,
        origin_city: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Estimate the total cost of a trip.

        Args:
            destination: Trip destination.
            duration_days: Number of days.
            travelers: Number of people.
            style: Travel style ("budget", "medium", "luxury").
            include_flights: Whether to include flight costs.
            origin_city: Departure city (required if include_flights=True).

        Returns:
            Dict with detailed cost breakdown.
        """
        flight_context: str = ""
        if include_flights and origin_city:
            flight_context = f"Round-trip flights from {origin_city} to {destination}.\n"

        cost_question: str = (
            f"Estimate the total cost for a {duration_days}-day trip "
            f"to {destination} for {travelers} traveler(s), {style} style.\n"
            f"{flight_context}"
            f"Provide a detailed breakdown:\n"
            f"1) Accommodation (per night)\n"
            f"2) Food and dining (per person per day)\n"
            f"3) Transportation (local)\n"
            f"4) Activities and entrance fees\n"
            f"5) Flights (if applicable)\n"
            f"6) Miscellaneous (tips, souvenirs, etc.)\n"
            f"7) Total estimate with 10% contingency\n\n"
            f"Include both per-person and total costs."
        )

        cost_estimate: str = await self.chat(cost_question)

        return {
            "destination": destination,
            "duration_days": duration_days,
            "travelers": travelers,
            "style": style,
            "cost_estimate": cost_estimate,
        }

    # ------------------------------------------------------------------
    # Agricultural tourism
    # ------------------------------------------------------------------

    async def recommend_agritourism(
        self,
        region: str,
        season: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Recommend agricultural tourism experiences.

        Specializes in farm stays, harvest festivals, wine tours,
        and other agriculture-related tourism activities.

        Args:
            region: Region or province name.
            season: Preferred season for agritourism.

        Returns:
            Dict with agritourism recommendations.
        """
        season_filter: str = f"in {season}" if season else ""

        from apps.shared_ai.rag.retriever import get_retriever

        retriever = get_retriever(top_k=8)
        agri_context: str = retriever.retrieve_context(
            query=f"agritourism farm stays harvest festivals {region} {season_filter}",
            top_k=8,
            format_as_text=True,
        )

        agri_question: str = (
            f"Recommend agricultural tourism experiences in {region} {season_filter}.\n"
            f"Context:\n{agri_context}\n\n"
            f"Include:\n"
            f"1) Farm stays and rural accommodations\n"
            f"2) Harvest festivals and seasonal events\n"
            f"3) Wine tasting and vineyard tours\n"
            f"4) Organic farm visits and workshops\n"
            f"5) Traditional food experiences\n"
            f"6) Best times to visit\n"
            f"7) Practical information (booking, transport, costs)"
        )

        recommendations: str = await self.chat(agri_question)

        return {
            "region": region,
            "season": season or "all year",
            "recommendations": recommendations,
            "category": "agritourism",
        }

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------

    def ingest_travel_guide(self, file_path: str) -> int:
        """Ingest a travel guide document into the RAG knowledge base.

        Args:
            file_path: Path to the document (PDF, TXT, MD).

        Returns:
            Number of chunks ingested.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        from apps.shared_ai.rag.document_loader import DocumentLoader

        loader: DocumentLoader = DocumentLoader()
        chunks: List[Dict[str, Any]] = loader.load_file(
            file_path,
            metadata={"category": "tourism", "file_path": file_path},
        )

        from apps.shared_ai.rag.vector_store import get_vector_store

        store = get_vector_store()
        texts: List[str] = [c["content"] for c in chunks]
        metadata_list: List[Dict[str, Any]] = [
            {"source": file_path, **c["metadata"]} for c in chunks
        ]

        store.add_documents(texts=texts, metadata_list=metadata_list)

        logger.info(
            "TourismAgent: ingested %d chunks from '%s'", len(chunks), file_path
        )
        return len(chunks)
