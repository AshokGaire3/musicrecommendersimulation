# Model Card: Music Recommender Simulation

## Model Name

**MusicHealer 1.0**

---

## Goal / Task

This system ranks songs from an 18-song catalog based on how well each song's features match a user's stated preferences. Every song gets a numeric score and the top 5 are returned in order, each with a short plain-language explanation of why it appeared.

---

## Intended Use

This recommender suggests up to 5 songs based on a user's genre, mood, energy level, and acoustic preference. It's built for a classroom project, not real users — the catalog is too small and the scoring too simple for anything production-level. It assumes the user can describe their taste in a few fields and doesn't learn from listening behavior or adapt over time.

It's not a tool for deciding which artists or genres deserve more visibility, and it doesn't represent global or diverse musical taste. If someone used it for real music discovery they'd quickly run into its limits.

---

## How the Model Works

The recommender compares what the user says they like against what each song actually is. There are up to nine signals, split into two groups.

**Core signals:** Genre match earns the most points (flat bonus). Mood match earns half that. Energy uses a closeness formula — the closer a song's energy is to the user's target, the more it scores, down to zero if the gap is too large. Acoustic quality is a small bonus for users who like acoustic music, or a small penalty for those who don't.

**Extended signals:** Popularity closeness (how close the song's chart score is to the user's target), release decade match, detailed mood match (e.g. "euphoric" is more specific than the broad "happy"), and an explicit-content hard filter that subtracts 10 points from any flagged song if the user has opted out.

Every song gets scored using all active signals, then the five highest become the recommendations.

**Scoring modes:** The weight of each signal can be shifted by picking a mode. `genre-first` makes genre worth four times a mood match. `mood-first` makes the detailed mood signal dominate. `energy-focused` triples the energy weight, which works well for workout playlists. `discovery` actually penalizes popular songs so lesser-known tracks come up higher.

**Diversity reranker:** After scoring, there's an optional second pass that picks songs one at a time and applies a penalty before each selection if the next-best song shares an artist or genre with something already chosen. The artist penalty is −1.5 per repeat and the genre penalty is −0.75 per extra appearance beyond the second. This keeps one artist or genre from filling all five slots.

---

## Data

The catalog has 18 songs across 15 genres and 14 moods: rock, pop, lofi, metal, classical, jazz, funk, reggae, soul, country, indie pop, synthwave, ambient, hip hop, and electronic. Most genres have only one or two songs.

Five columns were added beyond the starter CSV: `popularity` (0–100 chart score), `release_decade` (2000s/2010s/2020s), `detailed_mood` (euphoric, nostalgic, aggressive, serene, melancholic, uplifting, romantic, dreamy, triumphant), `language` (english or instrumental), and `explicit` (0 or 1). No songs were added or removed.

The catalog is almost entirely Western and English-language. K-pop, Latin, Afrobeats, and most regional folk traditions aren't represented at all. That's a real gap.

---

## Strengths

The system works best when the user's profile is internally consistent. The Chill Lofi profile (lofi + chill + low energy + acoustic) reliably puts Library Rain and Midnight Coding at #1 and #2. Deep Intense Rock puts Storm Runner first by a wide margin. For single-genre listeners with a clear taste, the top result usually matches intuition.

The output is also fully transparent — every recommendation shows exactly how much each feature contributed, so you can trace why anything appeared.

---

## Limitations and Bias

The genre weight (2.0 points) is strong enough to make a bad match win just because it's the only song in that genre. The "Classical Rage" adversarial profile exposed this clearly: Winter Cathedral (energy 0.22, slow and contemplative) ranked #1 for a user who wanted intense, high-energy classical music. It won just because it was the only classical song in the catalog.

The system also creates filter bubbles. For a rock listener, no jazz, soul, funk, or reggae songs ever appear in the top 5 — even songs that closely match their energy and mood. A listener whose taste crosses genre lines consistently gets worse recommendations than someone with a narrow, well-represented preference. With mostly one song per genre, the genre signal is basically all-or-nothing. It rewards rare matches too heavily and completely fails users whose genre isn't in the catalog at all.

---

## Evaluation

Five profiles were tested:

| Profile | Genre | Mood | Energy | Acoustic |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | False |
| Chill Lofi | lofi | chill | 0.40 | True |
| Deep Intense Rock | rock | intense | 0.88 | False |
| Adversarial (Classical Rage) | classical | intense | 0.90 | True |
| Edge Case (Loud & Acoustic) | folk | warm | 0.85 | True |

Chill Lofi and Deep Intense Rock both matched what I expected. For High-Energy Pop, Gym Hero (pop, but intense mood) ranked #2 even though the user wanted happy — the genre weight beat the mood mismatch. For Classical Rage, Winter Cathedral ranked #1 despite being the opposite of what the user wanted. For Loud & Acoustic, no folk songs exist so the results felt generic.

Doubling the energy weight and halving the genre weight caused Winter Cathedral to drop from #1 to #3 for Classical Rage, while the well-matched profiles stayed the same. That confirmed the default weights overfit to genre for unusual profiles.

---

## Future Work

- Expand the catalog to at least 5–10 songs per genre so genre matching is actually meaningful instead of a lottery
- Allow range-based energy preferences (e.g., "between 0.6 and 0.8") instead of a single target point
- Add support for negative preferences (e.g., "never country") to hard-exclude genres regardless of other scores
- Make the genre weight dynamic based on catalog coverage — if only one song exists in a genre, its weight should drop automatically so it doesn't win by default
- The diversity reranker is working but uses fixed penalty values — making those tunable per context (party playlist vs. study mix) would make it more flexible
- Add a feedback loop that adjusts weights based on what a user actually skips or replays, rather than a fixed recipe

---

## Personal Reflection

Building this made me realize how much a small weight decision shapes what a user sees. Choosing genre = 2.0 and mood = 1.0 is actually saying "what kind of music matters more than how it makes you feel." The Classical Rage experiment was the clearest moment — a song with almost nothing in common with what the user asked for ranked first just because it matched one categorical field. That made me think Spotify and TikTok must use dozens of signals weighted dynamically, not a fixed recipe like this.

The filter bubble finding stuck with me most. The rock profile never surfaced a jazz or soul song, even ones that matched well on energy and mood. In a real product, that invisible narrowing would quietly shape what people think music even sounds like — and most users would never notice it was happening.

---

### Phase 5 Engineering Reflection

**What was the biggest learning moment?**

The adversarial profile test. I built "Classical Rage" expecting weird results, but seeing Winter Cathedral (energy 0.22, slow and quiet) rank first for someone who wanted intense, high-energy classical made it concrete. A scoring system doesn't understand context — it just counts points. The number was "correct" by its own rules, but any human listener would immediately know it was wrong. I didn't expect to see that gap so clearly in something this simple.

**How did AI tools help, and when did you have to double-check?**

They helped me come up with adversarial profiles I wouldn't have thought of on my own — like "what happens when genre, mood, and energy all conflict." They also helped me structure the algorithm before touching code. But I still had to check the math by hand. I calculated scores manually for Storm Runner and Library Rain before trusting the implementation, then compared against the actual function output. If I'd assumed the code was right without checking, a weight bug could have gone unnoticed.

**What surprised you about how simple algorithms feel like recommendations?**

The explanations. When the terminal prints "matches your favorite genre (rock) | energy score 0.97" it reads like the system actually understood something. But it's three additions. The gap between "feels smart" and "is smart" is mostly just the language you wrap around the math. I think a lot of the magic in real apps is probably the same — presentation and confidence, not necessarily deeper understanding.

**What would you try next?**

A feedback loop that adjusts weights based on what a user actually skips or replays. And a dynamic genre weight that shrinks automatically when a genre has fewer than three songs — so the system doesn't win by default just for being the only option in a category.
