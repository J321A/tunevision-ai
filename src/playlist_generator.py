"""
Mood-based playlist generation extension.
Creates cohesive playlists based on mood transitions and energy flow.
"""

from typing import List, Dict, Tuple, Optional
import random
from recommender import recommend_songs, score_song, DEFAULT_WEIGHTS
from rag_engine import MusicRAGEngine


class MoodPlaylistGenerator:
    """Generates mood-based playlists with smooth transitions."""

    def __init__(self, rag_engine: MusicRAGEngine):
        self.rag_engine = rag_engine

    def generate_mood_playlist(self, target_mood: str, duration_minutes: int = 30, k: int = 10) -> Dict:
        """Generate a playlist that maintains a specific mood with smooth energy transitions."""

        # Get songs matching the mood
        user_prefs = {
            'mood': target_mood,
            'target_energy': self._get_typical_energy_for_mood(target_mood),
        }

        recommendations = self.rag_engine.get_hybrid_recommendations(user_prefs, f"{target_mood} music", k=k*2)

        # Sort by energy for smooth transitions
        songs_with_energy = [(rec[0], rec[0]['energy']) for rec in recommendations]
        songs_with_energy.sort(key=lambda x: x[1])  # Sort by energy ascending

        # Create energy flow: start medium, peak in middle, end medium
        playlist_songs = []
        total_songs = min(k, len(songs_with_energy))

        if total_songs >= 3:
            # Build energy curve
            energies = [s[1] for s in songs_with_energy[:total_songs]]
            min_energy, max_energy = min(energies), max(energies)

            # Create smooth energy progression
            energy_curve = []
            for i in range(total_songs):
                if i < total_songs // 3:
                    # Rising energy
                    energy_curve.append(min_energy + (max_energy - min_energy) * (i / (total_songs // 3)))
                elif i < 2 * total_songs // 3:
                    # Peak energy
                    energy_curve.append(max_energy)
                else:
                    # Falling energy
                    remaining = total_songs - i
                    total_fall = total_songs // 3
                    energy_curve.append(max_energy - (max_energy - min_energy) * ((total_fall - remaining) / total_fall))

            # Select songs closest to energy curve
            selected_songs = []
            available_songs = songs_with_energy[:total_songs]

            for target_energy in energy_curve:
                # Find song with closest energy to target
                best_match = min(available_songs, key=lambda x: abs(x[1] - target_energy))
                selected_songs.append(best_match[0])
                available_songs.remove(best_match)

            playlist_songs = selected_songs
        else:
            # Just take the top songs
            playlist_songs = [s[0] for s in songs_with_energy[:total_songs]]

        # Calculate approximate duration (assuming 3-4 minutes per song)
        avg_song_length = 3.5  # minutes
        total_duration = len(playlist_songs) * avg_song_length

        return {
            'name': f"{target_mood.title()} Journey",
            'description': f"A {total_songs}-song playlist designed to maintain a {target_mood} mood with smooth energy transitions.",
            'songs': playlist_songs,
            'total_songs': len(playlist_songs),
            'approximate_duration': f"{total_duration:.1f} minutes",
            'mood': target_mood,
            'energy_flow': 'smooth transitions' if len(playlist_songs) >= 3 else 'consistent'
        }

    def generate_energy_progression_playlist(self, start_energy: float, end_energy: float, genre: str = None, k: int = 8) -> Dict:
        """Generate a playlist with energy progression from start to end."""

        # Get base recommendations
        user_prefs = {
            'target_energy': (start_energy + end_energy) / 2,  # Middle energy
        }
        if genre:
            user_prefs['genre'] = genre

        query = f"music with energy progression from {start_energy:.1f} to {end_energy:.1f}"
        if genre:
            query += f" in {genre} genre"

        recommendations = self.rag_engine.get_hybrid_recommendations(user_prefs, query, k=k*2)

        # Sort by energy
        songs_with_energy = [(rec[0], rec[0]['energy']) for rec in recommendations]
        songs_with_energy.sort(key=lambda x: x[1])

        # Create linear energy progression
        playlist_songs = []
        if songs_with_energy:
            energy_range = end_energy - start_energy
            for i in range(k):
                target_energy = start_energy + (energy_range * i / max(1, k-1))
                # Find closest match
                best_match = min(songs_with_energy, key=lambda x: abs(x[1] - target_energy))
                playlist_songs.append(best_match[0])
                songs_with_energy.remove(best_match)

        total_duration = len(playlist_songs) * 3.5  # Assume 3.5 min per song

        progression_type = "ascending" if end_energy > start_energy else "descending"

        return {
            'name': f"Energy {progression_type.title()}",
            'description': f"A {len(playlist_songs)}-song playlist progressing from energy {start_energy:.1f} to {end_energy:.1f}.",
            'songs': playlist_songs,
            'total_songs': len(playlist_songs),
            'approximate_duration': f"{total_duration:.1f} minutes",
            'energy_progression': f"{start_energy:.1f} → {end_energy:.1f}",
            'genre_filter': genre or 'mixed'
        }

    def _get_typical_energy_for_mood(self, mood: str) -> float:
        """Get typical energy level for a mood."""
        mood_energy_map = {
            'happy': 0.75,
            'chill': 0.35,
            'intense': 0.85,
            'focused': 0.45,
            'moody': 0.55,
            'relaxed': 0.40,
            'upbeat': 0.70,
            'calm': 0.30,
            'aggressive': 0.90,
            'peaceful': 0.25
        }
        return mood_energy_map.get(mood.lower(), 0.5)


def create_mood_based_playlist(rag_engine: MusicRAGEngine, mood: str, duration: int = 30) -> Dict:
    """Convenience function to create a mood-based playlist."""
    generator = MoodPlaylistGenerator(rag_engine)
    return generator.generate_mood_playlist(mood, duration)