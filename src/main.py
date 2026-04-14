"""
Command line runner for the Music Recommender Simulation.

Usage:
  python -m src.main                              # all profiles, balanced mode
  python -m src.main "Chill Lofi"                 # single profile
  python -m src.main "Deep Intense Rock" genre-first
  python -m src.main "High-Energy Pop" mood-first --diversity
  python -m src.main --list-modes                 # show available scoring modes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs, SCORING_WEIGHTS

# Challenge 4: use tabulate for the visual summary table if available
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ── User taste profiles ────────────────────────────────────────────────────────

PROFILES = {
    "High-Energy Pop": {
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.85,
        "likes_acoustic":      False,
        "target_popularity":   80,
        "preferred_decade":    "2020s",
        "target_detailed_mood":"euphoric",
        "allow_explicit":      True,
    },
    "Chill Lofi": {
        "favorite_genre":      "lofi",
        "favorite_mood":       "chill",
        "target_energy":       0.40,
        "likes_acoustic":      True,
        "target_popularity":   60,
        "preferred_decade":    "2020s",
        "target_detailed_mood":"serene",
        "allow_explicit":      False,
    },
    "Deep Intense Rock": {
        "favorite_genre":      "rock",
        "favorite_mood":       "intense",
        "target_energy":       0.88,
        "likes_acoustic":      False,
        "target_popularity":   75,
        "preferred_decade":    "2010s",
        "target_detailed_mood":"aggressive",
        "allow_explicit":      True,
    },
    # Adversarial: conflicting signals — classical genre but intense/high-energy mood
    "Adversarial (Classical Rage)": {
        "favorite_genre":      "classical",
        "favorite_mood":       "intense",
        "target_energy":       0.90,
        "likes_acoustic":      True,
        "target_popularity":   50,
        "preferred_decade":    "2000s",
        "target_detailed_mood":"triumphant",
        "allow_explicit":      False,
    },
    # Edge case: high energy desired but also likes acoustic — features rarely co-exist
    "Edge Case (Loud & Acoustic)": {
        "favorite_genre":      "folk",
        "favorite_mood":       "warm",
        "target_energy":       0.85,
        "likes_acoustic":      True,
        "target_popularity":   55,
        "preferred_decade":    "2010s",
        "target_detailed_mood":"nostalgic",
        "allow_explicit":      False,
    },
}


# ── Challenge 4: Visual output helpers ────────────────────────────────────────

def _wrap(text: str, width: int = 45) -> str:
    """Hard-wrap a string to a fixed column width for table cells."""
    words = text.split()
    lines, current_len, current = [], 0, []
    for word in words:
        if current_len + len(word) + (1 if current else 0) > width:
            lines.append(" ".join(current))
            current, current_len = [word], len(word)
        else:
            current.append(word)
            current_len += len(word) + (1 if current_len else 0)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _ascii_table(headers: list, rows: list) -> str:
    """Minimal ASCII table — used when tabulate is not installed."""
    widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"
    lines = [sep, fmt.format(*headers), sep]
    for row in rows:
        for line in zip(*[str(c).split("\n") for c in row]):
            lines.append(fmt.format(*line))
        lines.append(sep)
    return "\n".join(lines)


def print_recommendations(
    profile_name: str,
    user_prefs: dict,
    songs: list,
    mode: str = "balanced",
    use_diversity: bool = False,
) -> None:
    print(f"\n{'=' * 72}")
    print(f"  Profile  : {profile_name}")
    print(f"  Mode     : {mode}"
          + (" + diversity" if use_diversity else ""))
    print(f"  Genre: {user_prefs['favorite_genre']}  "
          f"Mood: {user_prefs['favorite_mood']}  "
          f"Energy: {user_prefs['target_energy']}  "
          f"Acoustic: {user_prefs['likes_acoustic']}")
    print(f"  Detailed mood: {user_prefs.get('target_detailed_mood','—')}  "
          f"Decade: {user_prefs.get('preferred_decade','any')}  "
          f"Popularity target: {user_prefs.get('target_popularity', 70)}  "
          f"Explicit OK: {user_prefs.get('allow_explicit', True)}")
    print(f"{'=' * 72}")

    results = recommend_songs(user_prefs, songs, k=5, mode=mode, use_diversity=use_diversity)

    headers = ["#", "Title", "Artist", "Genre", "Pop", "Decade", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(results, 1):
        rows.append([
            f"#{rank}",
            song['title'],
            song['artist'],
            song['genre'],
            song['popularity'],
            song['release_decade'],
            f"{score:.2f}",
            _wrap(explanation),
        ])

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        print(_ascii_table(headers, rows))


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")

    args = sys.argv[1:]

    if "--list-modes" in args:
        print("Available scoring modes:")
        for m in SCORING_WEIGHTS:
            weights = SCORING_WEIGHTS[m]
            print(f"  {m:<16} genre={weights['genre']}  mood={weights['mood']}  "
                  f"energy={weights['energy']}  detailed_mood={weights['detailed_mood']}")
        return

    use_diversity = "--diversity" in args
    args = [a for a in args if a != "--diversity"]

    # Second positional arg is the scoring mode
    mode = "balanced"
    if len(args) >= 2 and args[1] in SCORING_WEIGHTS:
        mode = args[1]
    elif len(args) >= 2:
        print(f"Unknown mode '{args[1]}'. Use --list-modes to see options.")
        return

    if args and args[0] in PROFILES:
        print_recommendations(args[0], PROFILES[args[0]], songs, mode, use_diversity)
    elif args:
        print(f"Profile '{args[0]}' not found. Available profiles:")
        for p in PROFILES:
            print(f"  - {p}")
    else:
        for profile_name, user_prefs in PROFILES.items():
            print_recommendations(profile_name, user_prefs, songs, mode, use_diversity)


if __name__ == "__main__":
    main()
