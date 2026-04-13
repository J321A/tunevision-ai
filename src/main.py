"""
Music Recommender Simulation — CLI runner

Run from the project root:
    python3 src/main.py
Or from inside src/:
    python3 main.py
"""

import os
import sys
import textwrap

# Ensure src/ is on the path regardless of invocation style
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommender import (
    load_songs, recommend_songs, apply_diversity_penalty,
    compute_max_score, SCORING_MODES, DEFAULT_WEIGHTS,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_PATH = os.path.join(_HERE, "..", "data", "songs.csv")

# ── Challenge 4: tabulate display ─────────────────────────────────────────────
try:
    from tabulate import tabulate as _tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def print_results(
    label: str,
    user_prefs: dict,
    recs: list,
    max_sc: float,
    mode: str,
    diversity: bool = False,
) -> None:
    """Print a labelled recommendation block using tabulate or ASCII fallback."""
    div_tag = "  [diversity on]" if diversity else ""
    print(f"\n{'═' * 68}")
    print(f"  {label}")
    print(f"  Mode: {mode.upper()}{div_tag}  |  Max score: {max_sc:.1f}")
    prefs_line = (
        f"  genre={user_prefs.get('genre')} | mood={user_prefs.get('mood')} | "
        f"energy={user_prefs.get('target_energy')} | "
        f"decade={user_prefs.get('preferred_decade', '—')} | "
        f"tags={user_prefs.get('mood_tags', '—')}"
    )
    print(prefs_line)
    print(f"{'═' * 68}")

    if _HAS_TABULATE:
        rows = []
        for rank, (song, score, _) in enumerate(recs, start=1):
            rows.append([
                f"#{rank}",
                _trunc(song["title"], 26),
                _trunc(song["artist"], 18),
                song["genre"],
                song["mood"],
                song["energy"],
                f"{score:.2f}/{max_sc:.1f}",
            ])
        headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score"]
        print(_tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # ASCII fallback when tabulate is not installed
        fmt = "  {:<3} {:<26} {:<18} {:<12} {:<10} {:<7} {}"
        print(fmt.format("#", "Title", "Artist", "Genre", "Mood", "Energy", "Score"))
        print("  " + "-" * 64)
        for rank, (song, score, _) in enumerate(recs, start=1):
            print(fmt.format(
                f"#{rank}",
                _trunc(song["title"], 26),
                _trunc(song["artist"], 18),
                song["genre"],
                song["mood"],
                song["energy"],
                f"{score:.2f}/{max_sc:.1f}",
            ))

    print("\n  Reasons:")
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        prefix = f"  #{rank} "
        wrapped = textwrap.fill(
            f"{prefix}{explanation}",
            width=72,
            subsequent_indent=" " * len(prefix),
        )
        print(wrapped)
    print()


def run_profile(
    label: str,
    user_prefs: dict,
    songs: list,
    mode: str = "balanced",
    diversity: bool = False,
    k: int = 5,
) -> None:
    """Score, optionally apply diversity, then display results."""
    w = SCORING_MODES.get(mode, DEFAULT_WEIGHTS)
    max_sc = compute_max_score(user_prefs, w)
    # Fetch extra candidates so diversity has more to choose from
    pool = recommend_songs(user_prefs, songs, k=k * 2, weights=w)
    recs = apply_diversity_penalty(pool, k=k) if diversity else pool[:k]
    print_results(label, user_prefs, recs, max_sc, mode, diversity)


# ── User profiles ─────────────────────────────────────────────────────────────

PROFILES = {
    "2020 Pop Hits": {
        "genre":            "pop",
        "mood":             "happy",
        "target_energy":    0.80,
        "target_valence":   0.80,
        "likes_acoustic":   False,
        "target_popularity": 80,
        "preferred_decade": 2020,
        "mood_tags":        ["uplifting", "carefree"],
        "likes_instrumental": False,
    },
    "Deep Focus Study": {
        "genre":            "lofi",
        "mood":             "chill",
        "target_energy":    0.38,
        "target_valence":   0.58,
        "likes_acoustic":   True,
        "target_popularity": 60,
        "preferred_decade": 2020,
        "mood_tags":        ["focused", "calm"],
        "likes_instrumental": True,
    },
    "Retro Intense Rock": {
        "genre":            "rock",
        "mood":             "intense",
        "target_energy":    0.92,
        "target_valence":   0.45,
        "likes_acoustic":   False,
        "preferred_decade": 2010,
        "mood_tags":        ["powerful", "driving"],
        "likes_instrumental": False,
    },
}


def main() -> None:
    songs = load_songs(_DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    # ── Section 1: Three profiles, balanced mode ──────────────────────────────
    print("\n" + "▓" * 68)
    print("  SECTION 1 — Three Profiles  (balanced mode, all new features)")
    print("▓" * 68)
    for label, prefs in PROFILES.items():
        run_profile(label, prefs, songs, mode="balanced")

    # ── Section 2: Mode comparison (same profile, three modes) ────────────────
    print("\n" + "▓" * 68)
    print("  SECTION 2 — Scoring Mode Comparison  (2020 Pop Hits profile)")
    print("▓" * 68)
    pop_prefs = PROFILES["2020 Pop Hits"]
    for mode in ("genre_first", "mood_first", "energy_focused"):
        run_profile("2020 Pop Hits", pop_prefs, songs, mode=mode)

    # ── Section 3: Diversity comparison ───────────────────────────────────────
    print("\n" + "▓" * 68)
    print("  SECTION 3 — Diversity Penalty  (Deep Focus Study profile)")
    print("▓" * 68)
    focus_prefs = PROFILES["Deep Focus Study"]
    run_profile("Deep Focus  [no diversity]",  focus_prefs, songs, mode="balanced", diversity=False)
    run_profile("Deep Focus  [diversity on]",   focus_prefs, songs, mode="balanced", diversity=True)


if __name__ == "__main__":
    main()
