"""
Demo script showcasing TuneVision AI features.
Run this to see the system in action.
"""

import os
import sys
# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from recommender import load_songs
from vector_store import create_music_vector_store
from knowledge_base import create_default_knowledge_base
from rag_engine import MusicRAGEngine
from playlist_generator import create_mood_based_playlist
from taste_analyzer import TasteAnalyzer


def main():
    print("🎵 TuneVision AI - Feature Demo")
    print("=" * 50)

    # Load data
    print("\n📊 Loading music data...")
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs")

    # Create components
    print("\n🧠 Initializing AI components...")
    vector_store = create_music_vector_store(songs, cache_path="data/vector_store.pkl")
    knowledge_base = create_default_knowledge_base()
    rag_engine = MusicRAGEngine(songs, vector_store, knowledge_base)

    print("✅ System ready!")

    # Demo 1: RAG Recommendations
    print("\n🎯 Demo 1: RAG-Powered Recommendations")
    print("-" * 40)

    queries = [
        "I want happy pop music for a sunny day",
        "Find chill lofi for studying",
        "Need intense rock for working out"
    ]

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        results = rag_engine.get_recommendations_with_explanations(query, k=2)

        for i, rec in enumerate(results, 1):
            song = rec['song']
            print(f"  {i}. {song['title']} by {song['artist']}")
            print(f"     Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']:.1f}")
            print(f"     Why: {rec['detailed_explanation'][:100]}...")

    # Demo 2: Mood-Based Playlists
    print("\n🎵 Demo 2: Mood-Based Playlist Generation")
    print("-" * 40)

    moods = ["chill", "happy", "intense"]
    for mood in moods:
        playlist = create_mood_based_playlist(rag_engine, mood, duration=20)
        print(f"\n{mood.title()} Journey Playlist:")
        print(f"  {playlist['description']}")
        print(f"  Duration: {playlist['approximate_duration']}")
        print("  Songs:")
        for i, song in enumerate(playlist['songs'][:3], 1):
            print(f"    {i}. {song['title']} by {song['artist']}")
    print("\n📈 Demo 3: Taste Analysis")
    print("-" * 40)

    # Simulate some liked songs (using song IDs)
    liked_song_ids = [1, 2, 4, 9]  # Mix of pop, lofi, etc.

    analyzer = TasteAnalyzer(songs)
    analysis = analyzer.analyze_taste_from_history(liked_song_ids)

    print("\nBased on your liked songs:")
    print(f"  {analysis['taste_summary']}")
    print(f"  Top genres: {', '.join(analysis['genre_preferences']['top_genres'])}")
    print(f"  Top moods: {', '.join(analysis['mood_preferences']['top_moods'])}")
    print(f"  Energy preference: {analysis['energy_profile']['energy_type']}")
    print(f"  Artist diversity: {analysis['artist_discovery']['artist_diversity']}")

    # Demo 4: Vector Search
    print("\n🔍 Demo 4: Semantic Search")
    print("-" * 40)

    search_queries = [
        "electronic dance music",
        "peaceful instrumental",
        "aggressive guitar music"
    ]

    for query in search_queries:
        results = vector_store.search_similar(query, k=2)
        print(f"\nSearch: '{query}'")
        for song, similarity in results:
            print(".3f")

    print("\n🎉 Demo complete! Try the interactive chat with: python src/main.py --chat")


if __name__ == "__main__":
    main()