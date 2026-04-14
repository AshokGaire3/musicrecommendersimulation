"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.88,
        "likes_acoustic": False,
    }

    print(f"\nUser profile: genre={user_prefs['favorite_genre']} | "
          f"mood={user_prefs['favorite_mood']} | "
          f"energy={user_prefs['target_energy']} | "
          f"acoustic={user_prefs['likes_acoustic']}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop 5 Recommendations\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f}")
        print(f"       Why   : {explanation}")
        print()


if __name__ == "__main__":
    main()
