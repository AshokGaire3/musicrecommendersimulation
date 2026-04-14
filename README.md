# 🎵 Music Recommender Simulation

## Project Summary

This project builds a simple content-based music recommender that simulates what apps like Spotify or TikTok do at a small scale. Instead of machine learning or user history, my version uses a fixed taste profile and scores every song in the catalog against a few key features: genre, mood, energy level, and acoustic quality. The goal was to understand how raw song data actually gets turned into a ranked list of recommendations — and to think honestly about where a system this simple might go wrong.

---

## How The System Works

Real recommendation systems like Spotify's Discover Weekly or TikTok's For You page combine signals from listening history, what similar users liked, and the audio features of songs themselves. My version skips all of that and focuses on just one part: content-based filtering. That means I compare what the user says they like directly against what each song actually is — no learning from behavior, no crowd data.

My version prioritizes songs that match the user's genre and mood preferences first, then uses energy as a tiebreaker, and factors in acoustic quality as a small bonus or penalty. The tradeoff is simplicity and transparency — you can trace exactly why a song ranked where it did — but it also means the system is completely frozen around whatever the user profile says. It will only ever reward what the profile explicitly lists.

### Song Features Used

After analyzing the feature distributions across all 18 songs in the catalog, I chose these four features for scoring:

| Feature | Type | Spread in catalog | Why it matters |
|---|---|---|---|
| `genre` | string | 15 unique values | Strongest categorical signal — it captures the broadest style preference |
| `mood` | string | 14 unique values | Secondary signal — more fluid than genre, but still a strong differentiator |
| `energy` | float 0.0–1.0 | 0.22 – 0.96 (spread 0.74) | Wide numeric range makes it useful for proximity scoring |
| `acousticness` | float 0.0–1.0 | 0.04 – 0.97 (spread 0.93) | Widest spread of any numeric feature — great for separating electronic from acoustic |

`tempo_bpm`, `valence`, and `danceability` are stored in the CSV but not used in the scoring formula. Tempo overlaps heavily with energy as a signal, and valence/danceability have narrower spreads (0.55 and 0.69 respectively) that add complexity without much payoff at this scale.

### User Profile

The `UserProfile` stores the listener's stated preferences. For this simulation it is:

```python
user_prefs = {
  "favorite_genre": "rock",
  "favorite_mood": "intense",
  "target_energy": 0.88,
  "likes_acoustic": False,
}
```

This profile is strong enough to separate intense rock from chill lofi because it lines up genre, mood, and energy all pointing in the same direction. It is intentionally narrow — that makes it a clear test case, but it would not work well for someone whose taste crosses multiple genres or moods.

### Algorithm Recipe

**Scoring Rule (applied to one song at a time):**

The total score for a single song is the sum of these weighted points:

- `+2.0` for a genre match — genre gets the highest weight because it is the strongest signal for what kind of music someone wants
- `+1.0` for a mood match — mood matters but is more flexible, so it gets half the genre weight
- `+0.0 to +1.0` for energy proximity: `energy_points = max(0, 1 - abs(song_energy - target_energy))`
  - A song at exactly the target energy scores 1.0; songs further away score less and hit 0 if they differ by 1.0 or more
- `+0.0 to +0.5` acoustic bonus when `likes_acoustic` is True: `acousticness * 0.5`
- `-0.0 to -0.5` acoustic penalty when `likes_acoustic` is False: `acousticness * 0.5` subtracted
  - This reflects that a non-acoustic listener would actively dislike a very acoustic song

I verified the weights against the actual catalog before implementing them. For the rock/intense profile, **Storm Runner** (rock, intense, energy 0.91, acousticness 0.10) scores **3.92**, while **Library Rain** (lofi, chill, energy 0.35, acousticness 0.86) scores **0.04**. That spread of nearly 4 points confirms the weights clearly separate the target songs from the opposite end of the catalog.

**Ranking Rule (applied after all songs are scored):**

Once every song in the catalog has an individual score, the system sorts all scores from highest to lowest and returns the top K. Scoring and ranking are kept as two separate steps on purpose — a song can be evaluated on its own, but ranking only makes sense after the whole catalog has been compared.

**Expected Biases:**

One thing I noticed while planning this: because genre gets 2.0 points and mood only gets 1.0, a song that matches the genre but completely misses the mood will still outrank a song that nails the mood but is in the wrong genre. That could frustrate users whose taste crosses genre lines. There is also a filter bubble risk — a profile locked to "rock + intense" will never surface jazz, soul, or reggae songs, even if they score well on energy and mood. The system only rewards what the profile explicitly says; anything outside those categories gets silently passed over.

### Data Flow Diagram

```mermaid
flowchart TD
    A["Input: User Taste Profile
    favorite_genre = 'rock'
    favorite_mood = 'intense'
    target_energy = 0.88
    likes_acoustic = False"]

    B["load_songs('data/songs.csv')
    → 18 song dicts
    (genre, mood, energy, acousticness, ...)"]

    C{"For each of the 18 songs:
    score_song(user_prefs, song)"}

    D["Scoring formula per song:
    +2.0 if genre matches
    +1.0 if mood matches
    +max(0, 1 - abs(energy - 0.88))
    ± acousticness × 0.5"]

    E["18 scored songs
    e.g. Storm Runner → 3.92
         Library Rain → 0.04"]

    F["Sort by score descending
    → ranked list of all 18"]

    G["Return top K
    (song_dict, score, explanation)"]

    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

This diagram matches the actual code path: `load_songs` feeds 18 dicts into a loop, each goes through `score_song` which applies the four-part formula, and then all scores are sorted to produce the final top-K list. The scoring step is independent — any single song can be scored in isolation — but the ranking step requires the full set.

---

## CLI Output

Running `python -m src.main` produces the following terminal output:

![CLI terminal output showing top 5 recommendations](asset/main_sc.png)

---

## Stress Test: Diverse Profile Outputs

Each profile below was run independently to observe how the recommender behaves across different listener types and edge cases.

**Profile 1 — High-Energy Pop**
![High-Energy Pop recommendations](asset/Profile1.png)

**Profile 2 — Chill Lofi**
![Chill Lofi recommendations](asset/Profile2.png)

**Profile 3 — Deep Intense Rock**
![Deep Intense Rock recommendations](asset/Profile3.png)

**Profile 4 — Adversarial (Classical Rage)**
![Adversarial Classical Rage recommendations](asset/Profile4.png)

**Profile 5 — Edge Case (Loud & Acoustic)**
![Edge Case Loud and Acoustic recommendations](asset/Profile5.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

**Weight shift (genre halved, energy doubled):** For well-matched profiles like Chill Lofi and Deep Intense Rock the top 5 barely changed. For the adversarial Classical Rage profile, Winter Cathedral dropped from #1 to #3 — replaced by Storm Runner and Gym Hero which matched on mood and energy. This confirmed the default weights overfit to genre for rare profiles.

**Profile diversity test:** Ran 5 profiles including two adversarial edge cases. The Loud & Acoustic edge case (folk + high energy + acoustic) returned generic results because no folk songs exist in the catalog. The system silently substituted the nearest acoustic songs rather than flagging the gap.

**Manual score verification:** Calculated scores by hand for Storm Runner (3.92) and Library Rain (0.04) before writing the implementation, then confirmed the function output matched — this caught a potential logic error early.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

- Works only on an 18-song catalog — most genres have just one song, making genre matching an all-or-nothing bet
- The genre weight (2.0) is strong enough to surface the wrong song from the right genre, as proven by the Classical Rage adversarial test
- Creates filter bubbles: a rock listener never sees jazz or soul songs, even songs that match well on energy and mood
- Does not understand lyrics, cultural context, or listening history — only the four features it was given
- Missing entire regions of global music (K-pop, Latin, Afrobeats) — the catalog reflects a narrow Western taste

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Building this system taught me that a recommender is never just math — it is a set of values baked into numbers. Choosing genre = 2.0 and mood = 1.0 is a design decision that says "what kind of music matters more than how it makes you feel." What surprised me most is how much the plain-language explanations made the system feel intelligent, even though the logic underneath is just three additions. A user reading "matches your favorite genre | energy score 0.97" might trust that result far more than they should.

The bias finding is what stuck with me. The rock profile never once surfaced a jazz, soul, or reggae song — not because those songs were bad matches, but because the scoring formula had no way to value cross-genre similarity. In a real product used by millions of people, that kind of invisible narrowing would quietly shape what people think music sounds like, and most users would never know it was happening. That is what makes filter bubbles dangerous: they do not feel like a limitation, they just feel like good recommendations.



