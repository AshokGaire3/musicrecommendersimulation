"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs


# ── Profile definitions ────────────────────────────────────────────────────────

PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood":  "happy",
        "target_energy":  0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood":  "chill",
        "target_energy":  0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood":  "intense",
        "target_energy":  0.88,
        "likes_acoustic": False,
    },
    # Adversarial: classical + intense + high energy + acoustic — conflicting signals
    "Adversarial (Classical Rage)": {
        "favorite_genre": "classical",
        "favorite_mood":  "intense",
        "target_energy":  0.90,
        "likes_acoustic": True,
    },
    # Edge case: high energy but likes acoustic — two features that rarely co-exist
    "Edge Case (Loud & Acoustic)": {
        "favorite_genre": "folk",
        "favorite_mood":  "warm",
        "target_energy":  0.85,
        "likes_acoustic": True,
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Profile : {profile_name}")
    print(f"  Genre   : {user_prefs['favorite_genre']}  |  "
          f"Mood: {user_prefs['favorite_mood']}  |  "
          f"Energy: {user_prefs['target_energy']}  |  "
          f"Acoustic: {user_prefs['likes_acoustic']}")
    print(f"{'=' * 60}")

    results = recommend_songs(user_prefs, songs, k=5)
    for rank, (song, score, explanation) in enumerate(results, start=1):
        print(f"  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f}")
        print(f"       Why   : {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
