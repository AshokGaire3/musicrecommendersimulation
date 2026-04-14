"""
Core recommendation logic for the Music Recommender Simulation.

Challenge 1 – Advanced features: Song dataclass gains 5 new fields
  (popularity, release_decade, detailed_mood, language, explicit).
  UserProfile gains matching preference fields.

Challenge 2 – Scoring modes: SCORING_WEIGHTS maps mode names to
  per-feature weight dicts.  score_song() and Recommender.recommend()
  both accept a `mode` parameter so callers can switch strategies.

Challenge 3 – Diversity: _diversity_rerank() uses a greedy selection
  loop that applies per-artist and per-genre penalties before each pick,
  preventing the top-k from being dominated by one artist or genre.

Challenge 4 – Visual table: handled in src/main.py using tabulate.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter


# ── Challenge 2: Scoring mode weight tables ────────────────────────────────────
#
# Each entry maps a feature name to its multiplier.  Changing the mode
# shifts which signal dominates without rewriting any scoring logic.
#
#   genre         – flat bonus for an exact genre match
#   mood          – flat bonus for an exact broad-mood match
#   energy        – scales the 0-1 energy-proximity term
#   acoustic      – scales the acousticness bonus/penalty
#   popularity    – scales the 0-1 popularity-proximity term
#   decade        – flat bonus for an exact release-decade match
#   detailed_mood – flat bonus for an exact detailed-mood match

SCORING_WEIGHTS: Dict[str, Dict[str, float]] = {
    # Equal weight across all signals — good default
    "balanced": {
        "genre": 2.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5,
        "popularity": 0.5, "decade": 0.5, "detailed_mood": 1.5,
    },
    # Heavily rewards genre alignment; everything else is a tiebreaker
    "genre-first": {
        "genre": 4.0, "mood": 0.5, "energy": 0.5, "acoustic": 0.25,
        "popularity": 0.25, "decade": 0.25, "detailed_mood": 0.5,
    },
    # Prioritises broad + detailed mood match for emotional context
    "mood-first": {
        "genre": 0.5, "mood": 2.0, "energy": 0.5, "acoustic": 0.25,
        "popularity": 0.25, "decade": 0.25, "detailed_mood": 3.0,
    },
    # Maximises energy proximity — ideal for workout/study playlists
    "energy-focused": {
        "genre": 1.0, "mood": 0.5, "energy": 3.0, "acoustic": 0.25,
        "popularity": 0.25, "decade": 0.25, "detailed_mood": 0.5,
    },
    # Down-weights popularity to surface lesser-known tracks
    "discovery": {
        "genre": 1.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5,
        "popularity": -0.3, "decade": 0.5, "detailed_mood": 1.5,
    },
}


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    Challenge 1 fields have defaults so existing tests keep passing.
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
    # Challenge 1: advanced features
    popularity: int = 50          # 0-100 chart score
    release_decade: str = "2020s" # "1980s" | "1990s" | "2000s" | "2010s" | "2020s"
    detailed_mood: str = ""       # e.g. euphoric, nostalgic, aggressive, serene
    language: str = "english"     # english | instrumental | other
    explicit: bool = False


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    Challenge 1 fields are optional with sensible defaults.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Challenge 1: extended preferences
    target_popularity: int = 70   # preferred popularity level (0-100)
    preferred_decade: str = ""    # leave empty to ignore
    target_detailed_mood: str = ""# leave empty to ignore
    allow_explicit: bool = True


# ── Challenge 2: OOP Recommender with mode support ────────────────────────────

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song], mode: str = "balanced"):
        self.songs = songs
        self.mode = mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by weighted score against the user profile."""
        weights = SCORING_WEIGHTS.get(self.mode, SCORING_WEIGHTS["balanced"])

        def _score(song: Song) -> float:
            s = 0.0

            # Genre match
            if song.genre == user.favorite_genre:
                s += weights["genre"]

            # Broad mood match
            if song.mood == user.favorite_mood:
                s += weights["mood"]

            # Energy proximity: 0–1 term scaled by weight
            s += max(0.0, 1.0 - abs(song.energy - user.target_energy)) * weights["energy"]

            # Acoustic preference bonus / penalty
            if user.likes_acoustic:
                s += song.acousticness * weights["acoustic"]
            else:
                s -= song.acousticness * weights["acoustic"]

            # Popularity proximity: 0–1 term scaled by weight
            s += (1.0 - abs(song.popularity - user.target_popularity) / 100.0) * weights["popularity"]

            # Release decade match
            if user.preferred_decade and song.release_decade == user.preferred_decade:
                s += weights["decade"]

            # Detailed mood match
            if user.target_detailed_mood and song.detailed_mood == user.target_detailed_mood:
                s += weights["detailed_mood"]

            # Hard explicit filter
            if not user.allow_explicit and song.explicit:
                s -= 10.0

            return s

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
            reasons.append(f"energy {song.energy:.2f} very close to target {user.target_energy:.2f}")
        elif energy_diff <= 0.3:
            reasons.append(f"energy {song.energy:.2f} near your target {user.target_energy:.2f}")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"acoustic style ({song.acousticness:.2f}) fits your taste")
        elif not user.likes_acoustic and song.acousticness < 0.3:
            reasons.append(f"non-acoustic style ({song.acousticness:.2f}) fits your preference")
        if user.target_detailed_mood and song.detailed_mood == user.target_detailed_mood:
            reasons.append(f"detailed mood '{song.detailed_mood}' matches your target")
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            reasons.append(f"from your preferred era ({song.release_decade})")
        if not reasons:
            reasons.append("general match based on your profile")
        return " | ".join(reasons)


# ── Functional API ─────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to the right type."""
    import csv
    songs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                'id':             int(row['id']),
                'title':          row['title'],
                'artist':         row['artist'],
                'genre':          row['genre'],
                'mood':           row['mood'],
                'energy':         float(row['energy']),
                'tempo_bpm':      float(row['tempo_bpm']),
                'valence':        float(row['valence']),
                'danceability':   float(row['danceability']),
                'acousticness':   float(row['acousticness']),
                # Challenge 1: new fields (graceful defaults if column absent)
                'popularity':     int(row.get('popularity', 50)),
                'release_decade': row.get('release_decade', '2020s'),
                'detailed_mood':  row.get('detailed_mood', ''),
                'language':       row.get('language', 'english'),
                'explicit':       row.get('explicit', '0') == '1',
            })
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences and return (score, reasons).

    Scoring rules (weights come from SCORING_WEIGHTS[mode]):
      genre match       → +weights['genre']
      mood match        → +weights['mood']
      energy proximity  → max(0, 1 - |song_e - target_e|) * weights['energy']
      acoustic pref     → ±acousticness * weights['acoustic']
      popularity prox   → (1 - |pop_diff| / 100) * weights['popularity']
      decade match      → +weights['decade']
      detailed mood     → +weights['detailed_mood']
      explicit filter   → -10 if user disallows explicit content
    """
    weights = SCORING_WEIGHTS.get(mode, SCORING_WEIGHTS["balanced"])
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song['genre'] == user_prefs['favorite_genre']:
        score += weights["genre"]
        reasons.append(f"matches your favorite genre ({song['genre']})")

    # Broad mood match
    if song['mood'] == user_prefs['favorite_mood']:
        score += weights["mood"]
        reasons.append(f"matches your preferred mood ({song['mood']})")

    # Energy proximity
    energy_pts = max(0.0, 1.0 - abs(song['energy'] - user_prefs['target_energy'])) * weights["energy"]
    score += energy_pts
    reasons.append(
        f"energy {energy_pts:.2f} pts "
        f"(song {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f})"
    )

    # Acoustic preference
    if user_prefs['likes_acoustic']:
        bonus = song['acousticness'] * weights["acoustic"]
        score += bonus
        if bonus > 0.05:
            reasons.append(f"acoustic {song['acousticness']:.2f} fits taste (+{bonus:.2f})")
    else:
        penalty = song['acousticness'] * weights["acoustic"]
        score -= penalty
        if penalty > 0.05:
            reasons.append(f"low acoustic {song['acousticness']:.2f} fits taste (-{penalty:.2f})")

    # Popularity proximity
    target_pop = user_prefs.get('target_popularity', 70)
    pop_pts = (1.0 - abs(song['popularity'] - target_pop) / 100.0) * weights["popularity"]
    score += pop_pts
    if pop_pts > weights["popularity"] * 0.65:
        reasons.append(f"popularity {song['popularity']} near target {target_pop}")

    # Release decade match
    preferred_decade = user_prefs.get('preferred_decade', '')
    if preferred_decade and song['release_decade'] == preferred_decade:
        score += weights["decade"]
        reasons.append(f"from preferred era ({song['release_decade']})")

    # Detailed mood match
    target_detailed = user_prefs.get('target_detailed_mood', '')
    if target_detailed and song['detailed_mood'] == target_detailed:
        score += weights["detailed_mood"]
        reasons.append(f"detailed mood '{song['detailed_mood']}' matches target")

    # Explicit filter (hard penalty overrides everything)
    if not user_prefs.get('allow_explicit', True) and song.get('explicit', False):
        score -= 10.0
        reasons.append("explicit content filtered out (-10)")

    return (score, reasons)


# ── Challenge 3: Diversity reranker ───────────────────────────────────────────

def _diversity_rerank(
    scored: List[Tuple[Dict, float, str]],
    k: int,
    max_per_artist: int = 1,
    max_per_genre: int = 2,
    artist_penalty: float = 1.5,
    genre_penalty: float = 0.75,
) -> List[Tuple[Dict, float, str]]:
    """
    Greedy top-k selection with diversity penalties.

    Before each pick the remaining songs are re-scored:
      - Each additional appearance of an artist beyond max_per_artist
        subtracts artist_penalty from that song's score.
      - Each additional appearance of a genre beyond max_per_genre
        subtracts genre_penalty from that song's score.

    This prevents a single artist or genre from dominating the top results,
    creating a "filter bubble" effect common in naive content-based systems.
    """
    artist_count: Counter = Counter()
    genre_count: Counter = Counter()
    selected: List[Tuple[Dict, float, str]] = []
    pool = list(scored)

    while len(selected) < k and pool:
        penalized = []
        for song, base_score, expl in pool:
            penalty = 0.0
            artist_excess = max(0, artist_count[song['artist']] - max_per_artist + 1)
            genre_excess  = max(0, genre_count[song['genre']]  - max_per_genre + 1)
            penalty += artist_excess * artist_penalty
            penalty += genre_excess  * genre_penalty
            note = f" [diversity -{penalty:.1f}]" if penalty > 0 else ""
            penalized.append((song, base_score - penalty, expl + note))

        penalized.sort(key=lambda x: x[1], reverse=True)
        best = penalized[0]
        selected.append(best)
        pool = [(s, sc, e) for s, sc, e in pool if s['id'] != best[0]['id']]
        artist_count[best[0]['artist']] += 1
        genre_count[best[0]['genre']]  += 1

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    use_diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, sort highest to lowest, and return the top k as
    (song_dict, score, explanation) tuples.

    Args:
        user_prefs:    user taste profile dict
        songs:         list of song dicts from load_songs()
        k:             number of recommendations to return
        mode:          scoring mode key from SCORING_WEIGHTS
        use_diversity: if True, apply diversity reranking (Challenge 3)
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = " | ".join(reasons) if reasons else "no matching features"
        scored.append((song, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)

    if use_diversity:
        scored = _diversity_rerank(scored, k)

    return scored[:k]
