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
        """Return the top k songs ranked by weighted score against the user profile."""
        def _score(song: Song) -> float:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += 2.0
            if song.mood == user.favorite_mood:
                score += 1.0
            score += max(0.0, 1.0 - abs(song.energy - user.target_energy))
            if user.likes_acoustic:
                score += song.acousticness * 0.5
            else:
                score -= song.acousticness * 0.5
            return score

        return sorted(self.songs, key=_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why this song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"matches your preferred mood ({song.mood})")
        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.1:
            reasons.append(f"energy {song.energy:.2f} is very close to your target {user.target_energy:.2f}")
        elif energy_diff <= 0.3:
            reasons.append(f"energy {song.energy:.2f} is near your target {user.target_energy:.2f}")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"acoustic style ({song.acousticness:.2f}) fits your taste")
        elif not user.likes_acoustic and song.acousticness < 0.3:
            reasons.append(f"non-acoustic style ({song.acousticness:.2f}) fits your preference")
        if not reasons:
            reasons.append("general match based on your profile")
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float/int."""
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
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return (score, reasons) for one song using genre/mood/energy/acoustic weights."""
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
    """Score every song, sort highest to lowest, and return the top k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons) if reasons else "no matching features"
        scored.append((song, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
