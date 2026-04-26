"""
User taste analysis and summarization.
Analyzes listening history and preferences to create taste profiles.
"""

from typing import List, Dict, Tuple, Optional, Set
from collections import Counter, defaultdict
import statistics
from recommender import score_song


class TasteAnalyzer:
    """Analyzes user music taste patterns."""

    def __init__(self, songs: List[Dict]):
        self.songs = songs
        self.song_lookup = {song['id']: song for song in songs}

    def analyze_taste_from_history(self, liked_songs: List[int], disliked_songs: Optional[List[int]] = None) -> Dict:
        """Analyze taste from user's liked/disliked song history."""

        liked_songs_data = [self.song_lookup[sid] for sid in liked_songs if sid in self.song_lookup]
        disliked_songs_data = [self.song_lookup[sid] for sid in disliked_songs or [] if sid in self.song_lookup]

        if not liked_songs_data:
            return {"error": "No liked songs found for analysis"}

        analysis = {
            "total_liked": len(liked_songs_data),
            "total_disliked": len(disliked_songs_data),
            "genre_preferences": self._analyze_genre_preferences(liked_songs_data, disliked_songs_data),
            "mood_preferences": self._analyze_mood_preferences(liked_songs_data, disliked_songs_data),
            "energy_profile": self._analyze_energy_profile(liked_songs_data),
            "artist_discovery": self._analyze_artist_discovery(liked_songs_data),
            "decade_preferences": self._analyze_decade_preferences(liked_songs_data),
            "acoustic_preference": self._analyze_acoustic_preference(liked_songs_data),
            "taste_summary": self._generate_taste_summary(liked_songs_data, disliked_songs_data)
        }

        return analysis

    def _analyze_genre_preferences(self, liked: List[Dict], disliked: List[Dict]) -> Dict:
        """Analyze genre preferences."""
        liked_genres = Counter(song['genre'] for song in liked)
        disliked_genres = Counter(song['genre'] for song in disliked)

        # Calculate preference scores
        all_genres = set(liked_genres.keys()) | set(disliked_genres.keys())
        genre_scores = {}

        for genre in all_genres:
            liked_count = liked_genres.get(genre, 0)
            disliked_count = disliked_genres.get(genre, 0)
            total = liked_count + disliked_count

            if total > 0:
                # Wilson score interval approximation for preference strength
                if liked_count > 0:
                    score = (liked_count + 1.96**2/2) / (total + 1.96**2) - 1.96 * ((liked_count * disliked_count / total + 1.96**2/4)**(0.5)) / (total + 1.96**2)
                else:
                    score = 0
                genre_scores[genre] = round(score, 3)

        # Sort by preference score
        sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "top_genres": [genre for genre, score in sorted_genres[:3]],
            "genre_scores": dict(sorted_genres),
            "most_liked_genre": sorted_genres[0][0] if sorted_genres else None
        }

    def _analyze_mood_preferences(self, liked: List[Dict], disliked: List[Dict]) -> Dict:
        """Analyze mood preferences."""
        liked_moods = Counter(song['mood'] for song in liked)
        disliked_moods = Counter(song['mood'] for song in disliked)

        all_moods = set(liked_moods.keys()) | set(disliked_moods.keys())
        mood_scores = {}

        for mood in all_moods:
            liked_count = liked_moods.get(mood, 0)
            disliked_count = disliked_moods.get(mood, 0)
            total = liked_count + disliked_count

            if total > 0:
                score = liked_count / total
                mood_scores[mood] = round(score, 3)

        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "top_moods": [mood for mood, score in sorted_moods[:3]],
            "mood_scores": dict(sorted_moods),
            "signature_mood": sorted_moods[0][0] if sorted_moods else None
        }

    def _analyze_energy_profile(self, liked: List[Dict]) -> Dict:
        """Analyze energy preferences."""
        energies = [song['energy'] for song in liked]

        if not energies:
            return {"average_energy": 0.5, "energy_range": "unknown"}

        avg_energy = statistics.mean(energies)
        energy_std = statistics.stdev(energies) if len(energies) > 1 else 0

        # Classify energy preference
        if avg_energy < 0.4:
            energy_type = "low energy"
        elif avg_energy < 0.7:
            energy_type = "medium energy"
        else:
            energy_type = "high energy"

        # Determine consistency
        if energy_std < 0.1:
            consistency = "very consistent"
        elif energy_std < 0.2:
            consistency = "somewhat consistent"
        else:
            consistency = "varied"

        return {
            "average_energy": round(avg_energy, 2),
            "energy_consistency": consistency,
            "energy_type": energy_type,
            "energy_range": f"{min(energies):.1f} - {max(energies):.1f}",
            "energy_std": round(energy_std, 2)
        }

    def _analyze_artist_discovery(self, liked: List[Dict]) -> Dict:
        """Analyze artist discovery patterns."""
        artist_counts = Counter(song['artist'] for song in liked)

        # Calculate diversity metrics
        unique_artists = len(artist_counts)
        total_songs = len(liked)

        if total_songs == 0:
            return {"artist_diversity": "unknown"}

        # Artist concentration (Herfindahl index)
        concentrations = [(count/total_songs)**2 for count in artist_counts.values()]
        herfindahl = sum(concentrations)

        # Classify discovery pattern
        if herfindahl > 0.3:
            discovery_type = "loyal to few artists"
        elif herfindahl > 0.1:
            discovery_type = "moderate artist exploration"
        else:
            discovery_type = "active artist discovery"

        top_artists = artist_counts.most_common(3)

        return {
            "unique_artists": unique_artists,
            "artist_diversity": discovery_type,
            "top_artists": [{"artist": artist, "count": count} for artist, count in top_artists],
            "artist_concentration": round(herfindahl, 3)
        }

    def _analyze_decade_preferences(self, liked: List[Dict]) -> Dict:
        """Analyze decade preferences."""
        decades = [song.get('release_decade', 2020) for song in liked]
        decade_counts = Counter(decades)

        if not decade_counts:
            return {"preferred_decade": "unknown"}

        preferred_decade = decade_counts.most_common(1)[0][0]

        # Check for nostalgia vs contemporary preference
        current_decade = 2020
        if preferred_decade < current_decade - 10:
            time_preference = "nostalgic"
        elif preferred_decade >= current_decade - 5:
            time_preference = "contemporary"
        else:
            time_preference = "balanced"

        return {
            "preferred_decade": preferred_decade,
            "time_preference": time_preference,
            "decade_distribution": dict(decade_counts.most_common())
        }

    def _analyze_acoustic_preference(self, liked: List[Dict]) -> Dict:
        """Analyze acoustic vs electronic preferences."""
        acoustic_scores = [song.get('acousticness', 0.5) for song in liked]

        if not acoustic_scores:
            return {"acoustic_preference": "unknown"}

        avg_acoustic = statistics.mean(acoustic_scores)

        if avg_acoustic > 0.6:
            preference = "prefers acoustic"
        elif avg_acoustic < 0.3:
            preference = "prefers electronic"
        else:
            preference = "balanced acoustic/electronic"

        return {
            "average_acousticness": round(avg_acoustic, 2),
            "acoustic_preference": preference
        }

    def _generate_taste_summary(self, liked: List[Dict], disliked: List[Dict]) -> str:
        """Generate a natural language summary of taste."""
        if not liked:
            return "Not enough data to analyze taste preferences."

        genre_analysis = self._analyze_genre_preferences(liked, disliked)
        mood_analysis = self._analyze_mood_preferences(liked, disliked)
        energy_analysis = self._analyze_energy_profile(liked)
        artist_analysis = self._analyze_artist_discovery(liked)

        summary_parts = []

        # Genre summary
        if genre_analysis.get("top_genres"):
            top_genre = genre_analysis["top_genres"][0]
            summary_parts.append(f"You have a strong preference for {top_genre} music")

        # Mood summary
        if mood_analysis.get("signature_mood"):
            mood = mood_analysis["signature_mood"]
            summary_parts.append(f"and tend to enjoy {mood} moods")

        # Energy summary
        energy_type = energy_analysis.get("energy_type", "")
        if energy_type:
            summary_parts.append(f"with {energy_type} tracks")

        # Artist diversity
        diversity = artist_analysis.get("artist_diversity", "")
        if diversity:
            summary_parts.append(f"You show {diversity}")

        if summary_parts:
            summary = ". ".join(summary_parts) + "."
        else:
            summary = "Your taste preferences are still being developed."

        return summary

    def recommend_based_on_taste_profile(self, taste_analysis: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
        """Generate recommendations based on taste analysis."""

        # Extract preferences from analysis
        user_prefs = {}

        if taste_analysis.get("genre_preferences", {}).get("most_liked_genre"):
            user_prefs["genre"] = taste_analysis["genre_preferences"]["most_liked_genre"]

        if taste_analysis.get("mood_preferences", {}).get("signature_mood"):
            user_prefs["mood"] = taste_analysis["mood_preferences"]["signature_mood"]

        if taste_analysis.get("energy_profile", {}).get("average_energy"):
            user_prefs["target_energy"] = taste_analysis["energy_profile"]["average_energy"]

        # If we have preferences, use them for recommendations
        if user_prefs:
            from recommender import recommend_songs
            return recommend_songs(user_prefs, songs, k=k)
        else:
            # Fallback to popular songs
            return sorted(
                [(song, song.get("popularity", 50), "Based on general popularity") for song in songs],
                key=lambda x: x[1],
                reverse=True
            )[:k]