from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
            })
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Weights (verified against songs.csv distributions):
      +2.0  genre match       — strongest signal, spread across 15 genres
      +1.0  mood match        — secondary signal, spread across 14 moods
      +0–1  energy proximity  — max(0, 1 - |song_energy - target_energy|)
      ±0–0.5 acoustic pref   — acousticness * 0.5, added or subtracted
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match: +2.0
    if song['genre'] == user_prefs['favorite_genre']:
        score += 2.0
        reasons.append(f"matches your favorite genre ({song['genre']})")

    # Mood match: +1.0
    if song['mood'] == user_prefs['favorite_mood']:
        score += 1.0
        reasons.append(f"matches your preferred mood ({song['mood']})")

    # Energy proximity: 0.0 – 1.0
    energy_points = max(0.0, 1.0 - abs(song['energy'] - user_prefs['target_energy']))
    score += energy_points
    reasons.append(
        f"energy score {energy_points:.2f} "
        f"(song {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f})"
    )

    # Acoustic preference bonus or penalty: ±0.0 – 0.5
    if user_prefs['likes_acoustic']:
        bonus = song['acousticness'] * 0.5
        score += bonus
        if bonus > 0.1:
            reasons.append(f"acoustic quality {song['acousticness']:.2f} fits your taste (+{bonus:.2f})")
    else:
        penalty = song['acousticness'] * 0.5
        score -= penalty
        if penalty > 0.1:
            reasons.append(f"low acousticness {song['acousticness']:.2f} fits your non-acoustic preference (-{penalty:.2f})")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
