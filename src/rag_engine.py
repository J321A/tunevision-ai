"""
RAG (Retrieval-Augmented Generation) engine for music recommendations.
Combines traditional recommender with vector search and knowledge retrieval.
"""

from typing import List, Dict, Tuple, Optional, Any
import re
from recommender import recommend_songs, score_song, DEFAULT_WEIGHTS
from vector_store import MusicVectorStore
from knowledge_base import MusicKnowledgeBase


class MusicRAGEngine:
    """RAG engine that combines multiple retrieval methods for music recommendations."""

    def __init__(self, songs: List[Dict], vector_store: MusicVectorStore, knowledge_base: MusicKnowledgeBase):
        self.songs = songs
        self.vector_store = vector_store
        self.knowledge_base = knowledge_base
        self.song_lookup = {song['id']: song for song in songs}

    def parse_user_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to extract preferences."""
        preferences = {}

        # Extract genre preferences
        genre_patterns = [
            r"i like (\w+)",
            r"(\w+) music",
            r"(\w+) songs",
            r"genre: (\w+)",
        ]

        for pattern in genre_patterns:
            match = re.search(pattern, query.lower())
            if match:
                potential_genre = match.group(1)
                # Check if it's a known genre
                if self.knowledge_base.get_genre_info(potential_genre):
                    preferences['genre'] = potential_genre
                    break

        # Extract mood preferences
        mood_patterns = [
            r"feeling (\w+)",
            r"i want (\w+) music",
            r"mood: (\w+)",
            r"for (\w+) times",
        ]

        for pattern in mood_patterns:
            match = re.search(pattern, query.lower())
            if match:
                potential_mood = match.group(1)
                if self.knowledge_base.get_mood_info(potential_mood):
                    preferences['mood'] = potential_mood
                    break

        # Extract energy preferences
        if "energetic" in query.lower() or "high energy" in query.lower():
            preferences['target_energy'] = 0.8
        elif "chill" in query.lower() or "relaxed" in query.lower() or "calm" in query.lower():
            preferences['target_energy'] = 0.4
        elif "medium" in query.lower():
            preferences['target_energy'] = 0.6

        # Extract acoustic preferences
        if "acoustic" in query.lower() or "unplugged" in query.lower():
            preferences['likes_acoustic'] = True
        elif "electronic" in query.lower() or "electronic" in query.lower():
            preferences['likes_acoustic'] = False

        # Extract instrumental preferences
        if "instrumental" in query.lower() or "no vocals" in query.lower():
            preferences['likes_instrumental'] = True

        # Extract decade preferences
        decade_match = re.search(r"(\d{4})s?", query)
        if decade_match:
            decade = int(decade_match.group(1))
            if 1950 <= decade <= 2030:
                preferences['preferred_decade'] = decade

        return preferences

    def get_hybrid_recommendations(self, user_prefs: Dict, query: str = "", k: int = 5) -> List[Tuple[Dict, float, str]]:
        """Get recommendations using hybrid approach: traditional + vector search."""

        # Start with traditional recommender
        traditional_recs = recommend_songs(user_prefs, self.songs, k=k*2)

        # If we have a query, also get vector-based recommendations
        vector_recs = []
        if query:
            vector_results = self.vector_store.search_similar(query, k=k*2)
            # Convert to same format as traditional recs
            for song, similarity_score in vector_results:
                score, reasons = score_song(user_prefs, song)
                # Combine similarity with traditional score
                combined_score = score * 0.7 + similarity_score * 10 * 0.3  # Normalize similarity
                vector_recs.append((song, combined_score, f"semantic match | {reasons}"))

        # Combine and deduplicate
        all_recs = traditional_recs + vector_recs
        seen_ids = set()
        unique_recs = []

        for song, score, explanation in all_recs:
            song_id = song['id']
            if song_id not in seen_ids:
                seen_ids.add(song_id)
                unique_recs.append((song, score, explanation))

        # Sort by score and return top k
        unique_recs.sort(key=lambda x: x[1], reverse=True)
        return unique_recs[:k]

    def generate_explanation(self, song: Dict, user_prefs: Dict, query: str = "") -> str:
        """Generate a detailed explanation for why a song fits."""
        explanations = []

        # Basic scoring explanation
        score, reasons = score_song(user_prefs, song)
        explanations.append(f"This song scores {score:.1f} points because: {', '.join(reasons)}")

        # Add knowledge-based insights
        genre_info = self.knowledge_base.get_genre_info(song['genre'])
        if genre_info:
            explanations.append(f"{song['genre'].title()} music typically features {genre_info.get('description', '').lower()}")

        mood_info = self.knowledge_base.get_mood_info(song['mood'])
        if mood_info:
            explanations.append(f"The {song['mood']} mood is characterized by {mood_info.get('description', '').lower()}")

        artist_info = self.knowledge_base.get_artist_info(song['artist'])
        if artist_info:
            explanations.append(f"{song['artist']} is known for {artist_info.get('description', '').lower()}")

        # Add query-specific insights
        if query:
            relevant_knowledge = self.knowledge_base.search_relevant_knowledge(query, limit=2)
            if relevant_knowledge:
                explanations.append("Additional context: " + " ".join(relevant_knowledge))

        return " ".join(explanations)

    def get_recommendations_with_explanations(self, query: str, k: int = 5) -> List[Dict]:
        """Main method: parse query, get recommendations, add explanations."""
        user_prefs = self.parse_user_query(query)

        # If no preferences extracted, use defaults
        if not user_prefs:
            user_prefs = {
                'genre': 'pop',
                'mood': 'happy',
                'target_energy': 0.7,
                'likes_acoustic': False
            }

        recommendations = self.get_hybrid_recommendations(user_prefs, query, k)

        results = []
        for song, score, basic_explanation in recommendations:
            detailed_explanation = self.generate_explanation(song, user_prefs, query)

            result = {
                'song': song,
                'score': score,
                'basic_explanation': basic_explanation,
                'detailed_explanation': detailed_explanation,
                'user_preferences': user_prefs
            }
            results.append(result)

        return results