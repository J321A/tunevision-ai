"""
Vector-based retrieval for music recommendations.
Handles song embeddings and semantic search.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import os
import logging

logger = logging.getLogger(__name__)


class MusicVectorStore:
    """Vector store for semantic search over songs."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.songs_data = []
        self.embeddings = None

    def create_embeddings(self, songs: List[Dict]) -> np.ndarray:
        """Create embeddings for songs based on their metadata."""
        try:
            texts = []
            for song in songs:
                # Create rich text representation for embedding
                text_parts = [
                    song['title'],
                    song['artist'],
                    f"genre: {song['genre']}",
                    f"mood: {song['mood']}",
                    f"energy level: {song['energy']:.1f}",
                    f"valence: {song['valence']:.1f}",
                ]

                if song.get('mood_tags'):
                    text_parts.append(f"mood tags: {song['mood_tags']}")

                if song.get('popularity'):
                    text_parts.append(f"popularity: {song['popularity']}")

                if song.get('release_decade'):
                    text_parts.append(f"decade: {song['release_decade']}")

                text = " | ".join(text_parts)
                texts.append(text)

            logger.info(f"Creating embeddings for {len(texts)} songs")
            self.songs_data = songs
            self.embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.info(f"Embeddings created with shape: {self.embeddings.shape}")
            return self.embeddings
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise

    def build_index(self):
        """Build FAISS index for efficient similarity search."""
        if self.embeddings is None:
            raise ValueError("Embeddings not created. Call create_embeddings first.")

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

    def search_similar(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for songs similar to the query."""
        if self.index is None:
            logger.error("Index not built. Call build_index first.")
            raise ValueError("Index not built. Call build_index first.")

        try:
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)

            scores, indices = self.index.search(query_embedding, k)
            logger.info(f"Vector search for '{query}' returned {len(indices[0])} results")

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.songs_data):
                    results.append((self.songs_data[idx], float(score)))

            return results
        except Exception as e:
            logger.error(f"Failed to search similar songs: {e}")
            raise

    def save(self, path: str):
        """Save the vector store to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            'songs_data': self.songs_data,
            'embeddings': self.embeddings,
            'model_name': self.model.get_sentence_embedding_dimension()
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load(self, path: str):
        """Load the vector store from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.songs_data = data['songs_data']
        self.embeddings = data['embeddings']
        self.build_index()


def create_music_vector_store(songs: List[Dict], cache_path: Optional[str] = None) -> MusicVectorStore:
    """Create and optionally cache a music vector store."""
    store = MusicVectorStore()

    if cache_path and os.path.exists(cache_path):
        store.load(cache_path)
        return store

    store.create_embeddings(songs)
    store.build_index()

    if cache_path:
        store.save(cache_path)

    return store