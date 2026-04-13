from __future__ import annotations
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
    # Core fields — required (no defaults) so existing test code keeps working
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1: extended attributes — defaults allow tests to omit them
    popularity: int = 50
    release_decade: int = 2020
    liveness: float = 0.10
    instrumentalness: float = 0.10
    mood_tags: str = ""


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    # Core fields — required
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Challenge 1: extended preferences — all optional
    target_popularity: Optional[int] = None
    preferred_decade: Optional[int] = None
    target_liveness: Optional[float] = None
    likes_instrumental: Optional[bool] = None
    mood_tags: Optional[List[str]] = None


# ── OOP wrapper (required by tests) ───────────────────────────────────────────

class Recommender:
    """OOP wrapper around the functional scoring pipeline."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k Song objects ranked by score for this user profile."""
        user_dict = _profile_to_dict(user)
        song_dicts = [asdict(s) for s in self.songs]
        results = recommend_songs(user_dict, song_dicts, k=k)
        songs_by_id = {s.id: s for s in self.songs}
        return [songs_by_id[r[0]["id"]] for r in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why this song was recommended."""
        user_dict = _profile_to_dict(user)
        _, reasons = score_song(user_dict, asdict(song))
        return " | ".join(reasons)


def _profile_to_dict(user: UserProfile) -> Dict:
    """Convert a UserProfile to the flat dict format expected by score_song."""
    d: Dict = {
        "genre":          user.favorite_genre,
        "mood":           user.favorite_mood,
        "target_energy":  user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }
    if user.target_popularity is not None:
        d["target_popularity"] = user.target_popularity
    if user.preferred_decade is not None:
        d["preferred_decade"] = user.preferred_decade
    if user.target_liveness is not None:
        d["target_liveness"] = user.target_liveness
    if user.likes_instrumental is not None:
        d["likes_instrumental"] = user.likes_instrumental
    if user.mood_tags is not None:
        d["mood_tags"] = user.mood_tags
    return d


# ── Challenge 2: Scoring modes (Strategy pattern) ─────────────────────────────
# Each mode is a weight dict. Pass to score_song / recommend_songs via `weights=`.
# Adding a new mode never requires changing score_song — only this dict.

SCORING_MODES: Dict[str, Dict[str, float]] = {
    # All features weighted roughly proportionally
    "balanced": {
        "genre": 2.0, "mood": 1.0, "energy": 2.0, "valence": 1.0,
        "acousticness": 1.0, "popularity": 0.5, "release_decade": 0.5,
        "liveness": 0.5, "instrumentalness": 0.5, "mood_tags": 0.5,
    },
    # Genre identity dominates; everything else is a tiebreaker
    "genre_first": {
        "genre": 5.0, "mood": 1.0, "energy": 1.0, "valence": 0.5,
        "acousticness": 0.5, "popularity": 0.5, "release_decade": 0.5,
        "liveness": 0.25, "instrumentalness": 0.25, "mood_tags": 0.5,
    },
    # Mood label and mood_tags dominate; genre is secondary
    "mood_first": {
        "genre": 1.0, "mood": 4.0, "energy": 1.0, "valence": 1.5,
        "acousticness": 0.5, "popularity": 0.5, "release_decade": 0.5,
        "liveness": 0.25, "instrumentalness": 0.25, "mood_tags": 1.5,
    },
    # How the song actually sounds (energy) matters more than its label
    "energy_focused": {
        "genre": 1.0, "mood": 0.5, "energy": 5.0, "valence": 1.0,
        "acousticness": 1.0, "popularity": 0.5, "release_decade": 0.0,
        "liveness": 0.5, "instrumentalness": 0.5, "mood_tags": 0.5,
    },
    # Surface hidden gems: ignore popularity, reward decade freshness
    "discovery": {
        "genre": 2.0, "mood": 1.5, "energy": 2.0, "valence": 1.0,
        "acousticness": 1.0, "popularity": 0.0, "release_decade": 1.5,
        "liveness": 0.5, "instrumentalness": 0.5, "mood_tags": 1.0,
    },
}

DEFAULT_WEIGHTS: Dict[str, float] = SCORING_MODES["balanced"]


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, converting numerical fields to float/int."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                # Challenge 1 fields
                "popularity":       int(row["popularity"]),
                "release_decade":   int(row["release_decade"]),
                "liveness":         float(row["liveness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "mood_tags":        row["mood_tags"],
            })
    return songs


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; return (total_score, reasons)."""
    w = weights if weights is not None else DEFAULT_WEIGHTS
    score = 0.0
    reasons: List[str] = []

    # ── Core features ─────────────────────────────────────────────────────────

    if song["genre"] == user_prefs.get("genre", ""):
        pts = w["genre"]
        score += pts
        reasons.append(f"genre match ({pts:+.1f})")

    if song["mood"] == user_prefs.get("mood", ""):
        pts = w["mood"]
        score += pts
        reasons.append(f"mood match ({pts:+.1f})")

    target_energy = user_prefs.get("target_energy", 0.5)
    energy_score = w["energy"] * (1.0 - abs(song["energy"] - target_energy))
    score += energy_score
    reasons.append(f"energy ({energy_score:+.2f})")

    target_valence = user_prefs.get("target_valence", 0.5)
    valence_score = w["valence"] * (1.0 - abs(song["valence"] - target_valence))
    score += valence_score
    reasons.append(f"valence ({valence_score:+.2f})")

    if user_prefs.get("likes_acoustic", False):
        acoustic_score = w["acousticness"] * song["acousticness"]
    else:
        acoustic_score = w["acousticness"] * (1.0 - song["acousticness"])
    score += acoustic_score
    reasons.append(f"acoustic ({acoustic_score:+.2f})")

    # ── Challenge 1: extended features ────────────────────────────────────────

    # Popularity proximity: rewards songs close to the user's target fame level
    if "target_popularity" in user_prefs and w.get("popularity", 0) > 0:
        target_pop = user_prefs["target_popularity"]
        pop_score = w["popularity"] * (1.0 - abs(song["popularity"] - target_pop) / 100.0)
        score += pop_score
        reasons.append(f"popularity ({pop_score:+.2f})")

    # Release decade: exact match scores full points; one decade off scores half
    if "preferred_decade" in user_prefs and w.get("release_decade", 0) > 0:
        diff = abs(song["release_decade"] - user_prefs["preferred_decade"])
        if diff == 0:
            dec_score = w["release_decade"]
        elif diff == 10:
            dec_score = w["release_decade"] * 0.5
        else:
            dec_score = 0.0
        if dec_score > 0:
            score += dec_score
            reasons.append(f"decade ({dec_score:+.2f})")

    # Liveness proximity: rewards how "live" the recording sounds
    if "target_liveness" in user_prefs and w.get("liveness", 0) > 0:
        live_score = w["liveness"] * (1.0 - abs(song["liveness"] - user_prefs["target_liveness"]))
        score += live_score
        reasons.append(f"liveness ({live_score:+.2f})")

    # Instrumentalness fit: rewards vocal or instrumental preference
    if "likes_instrumental" in user_prefs and w.get("instrumentalness", 0) > 0:
        if user_prefs["likes_instrumental"]:
            instr_score = w["instrumentalness"] * song["instrumentalness"]
        else:
            instr_score = w["instrumentalness"] * (1.0 - song["instrumentalness"])
        score += instr_score
        reasons.append(f"instrumental ({instr_score:+.2f})")

    # Mood tags: up to 2 matching fine-grained tags contribute points
    if "mood_tags" in user_prefs and user_prefs["mood_tags"] and w.get("mood_tags", 0) > 0:
        user_tags = set(user_prefs["mood_tags"])
        song_tags = {t.strip() for t in song.get("mood_tags", "").split("|") if t.strip()}
        matching = user_tags & song_tags
        if matching:
            tag_score = min(w["mood_tags"] * len(matching), w["mood_tags"] * 2)
            score += tag_score
            reasons.append(f"tags {sorted(matching)} ({tag_score:+.2f})")

    return round(score, 2), reasons


def compute_max_score(user_prefs: Dict, weights: Dict) -> float:
    """Return the theoretical maximum score for this user/weight combination."""
    w = weights
    total = (w.get("genre", 0) + w.get("mood", 0) + w.get("energy", 0)
             + w.get("valence", 0) + w.get("acousticness", 0))
    if "target_popularity" in user_prefs:
        total += w.get("popularity", 0)
    if "preferred_decade" in user_prefs:
        total += w.get("release_decade", 0)
    if "target_liveness" in user_prefs:
        total += w.get("liveness", 0)
    if "likes_instrumental" in user_prefs:
        total += w.get("instrumentalness", 0)
    if "mood_tags" in user_prefs and user_prefs["mood_tags"]:
        total += w.get("mood_tags", 0) * 2  # up to 2 matching tags
    return round(total, 2)


# ── Challenge 3: Diversity penalty ────────────────────────────────────────────

def apply_diversity_penalty(
    ranked: List[Tuple[Dict, float, str]],
    k: int = 5,
    artist_penalty: float = 0.5,
    genre_penalty: float = 0.3,
) -> List[Tuple[Dict, float, str]]:
    """Greedily select top-k songs, penalizing repeat artists and genres.

    Works by re-scoring all remaining candidates after each selection,
    so penalties accumulate as the result list fills up.
    Artist penalty: -0.5 × appearances already selected.
    Genre penalty:  -0.3 × (appearances - 1) when a genre appears 2+ times.
    """
    selected: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    remaining = list(ranked)

    while len(selected) < k and remaining:
        best_adj: float = -1.0
        best_idx: int = 0
        best_entry: Optional[Tuple[Dict, float, str]] = None

        for idx, (song, score, explanation) in enumerate(remaining):
            penalty = 0.0
            notes: List[str] = []

            ac = artist_counts.get(song["artist"], 0)
            if ac > 0:
                p = artist_penalty * ac
                penalty += p
                notes.append(f"repeat artist ({-p:+.1f})")

            gc = genre_counts.get(song["genre"], 0)
            if gc >= 2:
                p = genre_penalty * (gc - 1)
                penalty += p
                notes.append(f"repeat genre ({-p:+.1f})")

            adj = round(max(0.0, score - penalty), 2)
            if adj > best_adj:
                best_adj = adj
                best_idx = idx
                new_exp = explanation + (" | " + " | ".join(notes) if notes else "")
                best_entry = (song, adj, new_exp)

        selected.append(best_entry)
        winner = remaining[best_idx][0]
        artist_counts[winner["artist"]] = artist_counts.get(winner["artist"], 0) + 1
        genre_counts[winner["genre"]] = genre_counts.get(winner["genre"], 0) + 1
        remaining.pop(best_idx)

    return selected


# ── Ranking ───────────────────────────────────────────────────────────────────

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top-k results."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights=weights)
        scored.append((song, score, " | ".join(reasons)))

    # sorted() is non-destructive — preserves original list order for the caller
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
