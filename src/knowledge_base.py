"""
Knowledge base for music domain information.
Contains facts about artists, genres, moods, and music theory.
"""

from typing import Dict, List, Optional
import json
import os


class MusicKnowledgeBase:
    """Knowledge base containing music domain information."""

    def __init__(self):
        self.knowledge = {
            "genres": {},
            "artists": {},
            "moods": {},
            "music_theory": {}
        }

    def add_genre_info(self, genre: str, info: Dict):
        """Add information about a music genre."""
        self.knowledge["genres"][genre.lower()] = info

    def add_artist_info(self, artist: str, info: Dict):
        """Add information about an artist."""
        self.knowledge["artists"][artist.lower()] = info

    def add_mood_info(self, mood: str, info: Dict):
        """Add information about a mood/emotion in music."""
        self.knowledge["moods"][mood.lower()] = info

    def get_genre_info(self, genre: str) -> Optional[Dict]:
        """Retrieve information about a genre."""
        return self.knowledge["genres"].get(genre.lower())

    def get_artist_info(self, artist: str) -> Optional[Dict]:
        """Retrieve information about an artist."""
        return self.knowledge["artists"].get(artist.lower())

    def get_mood_info(self, mood: str) -> Optional[Dict]:
        """Retrieve information about a mood."""
        return self.knowledge["moods"].get(mood.lower())

    def search_relevant_knowledge(self, query: str, limit: int = 3) -> List[str]:
        """Search for knowledge relevant to a query."""
        relevant_facts = []

        query_lower = query.lower()

        # Search genres
        for genre, info in self.knowledge["genres"].items():
            if genre in query_lower or any(tag in query_lower for tag in info.get("tags", [])):
                relevant_facts.append(f"Genre {genre}: {info.get('description', '')}")

        # Search artists
        for artist, info in self.knowledge["artists"].items():
            if artist in query_lower:
                relevant_facts.append(f"Artist {artist}: {info.get('description', '')}")

        # Search moods
        for mood, info in self.knowledge["moods"].items():
            if mood in query_lower or any(tag in query_lower for tag in info.get("tags", [])):
                relevant_facts.append(f"Mood {mood}: {info.get('description', '')}")

        return relevant_facts[:limit]

    def save(self, path: str):
        """Save knowledge base to JSON file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)

    def load(self, path: str):
        """Load knowledge base from JSON file."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)


def create_default_knowledge_base() -> MusicKnowledgeBase:
    """Create a knowledge base with default music information."""
    kb = MusicKnowledgeBase()

    # Add genre information
    kb.add_genre_info("pop", {
        "description": "Popular music characterized by catchy melodies, electronic production, and broad appeal. Often features strong vocals and danceable rhythms.",
        "tags": ["catchy", "mainstream", "electronic", "vocals"],
        "typical_energy": "medium-high",
        "typical_moods": ["happy", "uplifting", "carefree"]
    })

    kb.add_genre_info("rock", {
        "description": "Rock music featuring electric guitars, strong rhythms, and often intense emotional expression. Can range from soft acoustic to heavy electric.",
        "tags": ["guitar", "intense", "driving", "powerful"],
        "typical_energy": "high",
        "typical_moods": ["intense", "aggressive", "powerful"]
    })

    kb.add_genre_info("lofi", {
        "description": "Lo-fi hip hop and chill music, often instrumental or with laid-back vocals. Characterized by vintage sampling and relaxed, study-friendly atmosphere.",
        "tags": ["chill", "instrumental", "focused", "calm", "rainy"],
        "typical_energy": "low-medium",
        "typical_moods": ["chill", "focused", "calm", "peaceful"]
    })

    kb.add_genre_info("ambient", {
        "description": "Atmospheric music designed to create mood and atmosphere. Often instrumental with electronic textures and minimal structure.",
        "tags": ["atmospheric", "meditative", "dreamy", "cosmic"],
        "typical_energy": "low",
        "typical_moods": ["chill", "meditative", "dreamy"]
    })

    kb.add_genre_info("jazz", {
        "description": "Jazz music featuring improvisation, complex harmonies, and often acoustic instrumentation. Known for its sophisticated rhythms and melodies.",
        "tags": ["improvisation", "sophisticated", "acoustic", "cozy", "nostalgic"],
        "typical_energy": "medium",
        "typical_moods": ["relaxed", "cozy", "nostalgic", "mellow"]
    })

    kb.add_genre_info("synthwave", {
        "description": "Retro electronic music inspired by 1980s synth-pop and movie soundtracks. Features heavy use of synthesizers and nostalgic vibes.",
        "tags": ["electronic", "nostalgic", "cinematic", "retro", "night"],
        "typical_energy": "medium-high",
        "typical_moods": ["moody", "nostalgic", "cinematic"]
    })

    # Add mood information
    kb.add_mood_info("happy", {
        "description": "Upbeat, positive music that evokes joy and good feelings. Often features major keys, bright instrumentation, and energetic rhythms.",
        "tags": ["upbeat", "positive", "joyful", "bright", "energetic"],
        "typical_energy": "high",
        "associated_genres": ["pop", "dance", "reggae"]
    })

    kb.add_mood_info("chill", {
        "description": "Relaxed, laid-back music perfect for unwinding. Features slow tempos, smooth melodies, and minimal tension.",
        "tags": ["relaxed", "calm", "peaceful", "smooth", "laid-back"],
        "typical_energy": "low-medium",
        "associated_genres": ["lofi", "ambient", "jazz"]
    })

    kb.add_mood_info("intense", {
        "description": "Powerful, high-energy music that builds tension and excitement. Often features driving rhythms and strong emotional impact.",
        "tags": ["powerful", "driving", "aggressive", "energetic", "emotional"],
        "typical_energy": "high",
        "associated_genres": ["rock", "metal", "electronic"]
    })

    kb.add_mood_info("focused", {
        "description": "Music that helps with concentration and productivity. Often instrumental with steady rhythms and minimal distractions.",
        "tags": ["concentrated", "productive", "steady", "instrumental"],
        "typical_energy": "medium",
        "associated_genres": ["lofi", "classical", "ambient"]
    })

    kb.add_mood_info("moody", {
        "description": "Atmospheric music with emotional depth and introspection. Can evoke mystery, nostalgia, or contemplation.",
        "tags": ["atmospheric", "emotional", "nostalgic", "contemplative"],
        "typical_energy": "medium-low",
        "associated_genres": ["synthwave", "indie", "alternative"]
    })

    # Add some artist information
    kb.add_artist_info("neon echo", {
        "description": "Electronic pop artist known for upbeat, synth-driven tracks with nostalgic 80s influences.",
        "genres": ["pop", "synthwave"],
        "signature_style": "catchy melodies with electronic production"
    })

    kb.add_artist_info("loroom", {
        "description": "Lo-fi hip hop producer specializing in chill, instrumental beats perfect for studying and relaxation.",
        "genres": ["lofi", "hip hop"],
        "signature_style": "vintage samples with smooth, atmospheric production"
    })

    kb.add_artist_info("voltline", {
        "description": "Rock band known for high-energy anthems and powerful guitar-driven sound.",
        "genres": ["rock"],
        "signature_style": "intense rhythms with emotional vocal delivery"
    })

    return kb