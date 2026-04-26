"""
Conversational AI agent for music recommendations.
Handles multi-turn conversations with memory and context.
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import logging

from rag_engine import MusicRAGEngine
from vector_store import create_music_vector_store
from knowledge_base import create_default_knowledge_base

logger = logging.getLogger(__name__)


class MusicChatAgent:
    """Conversational agent for music recommendations."""

    def __init__(self, rag_engine: MusicRAGEngine, openai_api_key: Optional[str] = None):
        self.rag_engine = rag_engine

        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key

        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500
        )

        # Simple conversation memory (list of message tuples)
        self.conversation_history: List[Dict[str, str]] = []

        # Custom prompt for music recommendations
        self.music_prompt = PromptTemplate(
            input_variables=["history", "input", "context"],
            template="""You are a friendly music recommendation assistant with access to a comprehensive music database. You use retrieved information about songs, artists, and music knowledge to provide personalized, accurate recommendations.

Previous conversation:
{history}

Additional context from music database:
{context}

Current user message: {input}

Your task is to:
1. Use the provided context to give informed, specific recommendations
2. Explain WHY each song fits based on the detailed information available
3. Be conversational and ask follow-up questions to refine recommendations
4. Reference specific song features (genre, mood, energy, artist style) from the context
5. If no specific recommendations are provided, help the user clarify their preferences

Keep your response natural and engaging. When recommending songs, explain the specific reasons they match.

Response:"""
        )

    def _build_rag_context(self, user_message: str, recommendations: List[Dict]) -> str:
        """Build rich context from RAG results for the LLM."""
        if not recommendations:
            return "No specific recommendations found."

        context_parts = [
            f"User query: '{user_message}'",
            "",
            "RECOMMENDED SONGS WITH DETAILS:"
        ]

        for i, rec in enumerate(recommendations, 1):
            song = rec['song']
            context_parts.extend([
                f"{i}. {song['title']} by {song['artist']}",
                f"   - Genre: {song['genre']}",
                f"   - Mood: {song['mood']}",
                f"   - Energy: {song['energy']:.1f} (0=very calm, 1=very energetic)",
                f"   - Valence: {song['valence']:.1f} (0=very sad, 1=very happy)",
                f"   - Popularity: {song.get('popularity', 'N/A')}",
                f"   - Release decade: {song.get('release_decade', 'N/A')}",
                f"   - Mood tags: {song.get('mood_tags', 'none')}",
                f"   - Detailed explanation: {rec['detailed_explanation']}",
                ""
            ])

        # Add relevant knowledge from knowledge base
        relevant_knowledge = self.rag_engine.knowledge_base.search_relevant_knowledge(user_message, limit=3)
        if relevant_knowledge:
            context_parts.extend([
                "RELEVANT MUSIC KNOWLEDGE:",
                "\n".join(f"- {fact}" for fact in relevant_knowledge),
                ""
            ])

        return "\n".join(context_parts)

    def _get_llm_response(self, user_message: str, context: str) -> str:
        """Get response from LLM with context."""
        try:
            # Build conversation history
            history_text = ""
            if self.conversation_history:
                history_text = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in self.conversation_history[-3:]])  # Last 3 exchanges

            # Create prompt with history and context
            full_prompt = f"""You are a helpful music recommendation assistant. Use the following context to provide informed recommendations.

Previous conversation:
{history_text}

Additional context from music database:
{context}

Current user message: {user_message}

Your task is to:
1. Use the provided context to give informed, specific recommendations
2. Explain WHY each song fits based on the detailed information available
3. Be conversational and ask follow-up questions to refine recommendations
4. Reference specific song features (genre, mood, energy, artist style) from the context
5. If no specific recommendations are provided, help the user clarify their preferences

Keep your response natural and engaging. When recommending songs, explain the specific reasons they match.

Response:"""

            response = self.llm.invoke(full_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return "I'm having trouble generating a response right now. Could you try rephrasing your request?"

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message and return response with recommendations if appropriate."""

        try:
            # Check if user is asking for recommendations
            recommendation_keywords = [
                "recommend", "suggest", "find", "looking for", "want to listen",
                "like to hear", "play", "music for", "songs for"
            ]

            is_recommendation_request = any(keyword in user_message.lower() for keyword in recommendation_keywords)

            response_data = {
                "response": "",
                "recommendations": [],
                "user_preferences": {},
                "is_recommendation": is_recommendation_request
            }

            enhanced_context = ""

            if is_recommendation_request:
                logger.info(f"Processing recommendation request: {user_message}")
                # Get recommendations using RAG engine
                recommendations = self.rag_engine.get_recommendations_with_explanations(user_message, k=3)
                response_data["recommendations"] = recommendations
                response_data["user_preferences"] = recommendations[0]["user_preferences"] if recommendations else {}

                # Build rich context for LLM using RAG results
                if recommendations:
                    enhanced_context = self._build_rag_context(user_message, recommendations)
                    logger.info(f"Generated RAG context with {len(recommendations)} recommendations")
                else:
                    enhanced_context = f"I couldn't find specific recommendations for '{user_message}', but I can help you discover music!"
            else:
                logger.info(f"Processing general message: {user_message}")

            # Get LLM response with enhanced context
            llm_response = self._get_llm_response(user_message, enhanced_context)
            response_data["response"] = llm_response

            # Add to conversation history
            self.conversation_history.append({
                "user": user_message,
                "assistant": llm_response,
                "timestamp": datetime.now().isoformat()
            })

            return response_data

        except Exception as e:
            logger.error(f"Error processing message '{user_message}': {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "recommendations": [],
                "user_preferences": {},
                "is_recommendation": False,
                "error": str(e)
            }

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history."""
        return self.conversation_history

    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []

    def get_user_taste_summary(self) -> Dict[str, Any]:
        """Summarize user's music taste based on conversation history."""
        history = self.get_conversation_history()

        # Simple analysis - in a real system, this could be more sophisticated
        preferences = {
            "mentioned_genres": set(),
            "mentioned_moods": set(),
            "mentioned_artists": set(),
            "energy_preferences": [],
            "conversation_length": len(history)
        }

        for message in history:
            if hasattr(message, 'content'):
                content = message.content.lower()

                # Extract mentioned genres, moods, artists from conversation
                # This is a simplified version - could use NLP for better extraction
                for genre in ["pop", "rock", "lofi", "jazz", "ambient", "synthwave"]:
                    if genre in content:
                        preferences["mentioned_genres"].add(genre)

                for mood in ["happy", "chill", "intense", "focused", "moody"]:
                    if mood in content:
                        preferences["mentioned_moods"].add(mood)

                # Look for energy mentions
                if "energetic" in content or "high energy" in content:
                    preferences["energy_preferences"].append("high")
                elif "chill" in content or "relaxed" in content:
                    preferences["energy_preferences"].append("low")

        return preferences


def create_music_chat_agent(songs: List[Dict], openai_api_key: Optional[str] = None) -> MusicChatAgent:
    """Factory function to create a music chat agent with all components."""

    # Create vector store
    vector_store = create_music_vector_store(songs, cache_path="data/vector_store.pkl")

    # Create knowledge base
    knowledge_base = create_default_knowledge_base()

    # Create RAG engine
    rag_engine = MusicRAGEngine(songs, vector_store, knowledge_base)

    # Create chat agent
    agent = MusicChatAgent(rag_engine, openai_api_key)

    return agent