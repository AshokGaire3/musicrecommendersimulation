# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**VibeFinder 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This system suggests up to 5 songs from an 18-song catalog based on a user's stated genre, mood, energy level, and acoustic preference. It is built for classroom exploration — not real users — to demonstrate how a content-based recommender turns raw data into a ranked list. It assumes the user can fully describe their taste in four fields and does not learn from listening history or adapt over time.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The recommender compares what the user says they like against what each song actually is, using four features. If a song matches the user's favorite genre, it earns 2 points. If it matches the preferred mood, it earns 1 more point. The energy score is a closeness calculation — a song at exactly the user's target energy earns a full extra point, and songs further away earn less. If the user likes acoustic music, songs with higher acoustic quality get a small bonus; if the user dislikes acoustic music, those same songs get a small penalty. Every song in the catalog gets scored this way, and the five highest-scoring songs become the recommendations. I added the acoustic preference bonus and penalty on top of the starter logic, and I kept genre as the strongest weight because it tends to be the clearest signal for what kind of music someone wants.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog has 18 songs across 15 genres and 14 moods. Genres include rock, pop, lofi, metal, classical, jazz, funk, reggae, soul, country, indie pop, synthwave, ambient, hip hop, and electronic. Most genres have only one or two songs. No songs were added or removed from the starter CSV. The data reflects a Western, English-language taste and is missing entire regions of music — K-pop, Latin, Afrobeats, and regional folk traditions are completely absent. With only one song per genre in many cases, the catalog is too narrow to represent real listener diversity.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best when the user's profile is internally consistent. The Chill Lofi profile (lofi + chill + low energy + likes acoustic) reliably surfaces Library Rain and Midnight Coding at #1 and #2 — exactly the expected result. The Deep Intense Rock profile correctly places Storm Runner first by a wide margin. For clear, single-genre listeners, the top result is almost always the song you would intuitively pick. The scoring is also fully transparent: every recommendation includes a plain-language breakdown of exactly how many points each feature contributed, which makes it easy to trace why any result appeared.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The genre weight (2.0 points) is strong enough to crown a poor match as the top recommendation simply because it is the only song in that genre. This was exposed by the "Classical Rage" adversarial profile: Winter Cathedral — a slow, contemplative song with energy 0.22 — ranked #1 for a user who wanted intense, high-energy classical music, because it was the only classical song in the catalog. The system also creates a filter bubble: for the rock profile, no jazz, soul, funk, or reggae songs ever appear in the top 5, even songs that closely match the user's energy and mood. A cross-genre listener whose taste does not fit neatly into one label will consistently get worse recommendations than someone with a narrow, well-represented preference. Additionally, with only one song per genre in many cases, the genre signal becomes an all-or-nothing bet rather than a meaningful measure of fit — it over-rewards rare genre matches and punishes users whose favorite genre is missing from the catalog entirely.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Five user profiles were tested:

| Profile | Genre | Mood | Energy | Acoustic |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | False |
| Chill Lofi | lofi | chill | 0.40 | True |
| Deep Intense Rock | rock | intense | 0.88 | False |
| Adversarial (Classical Rage) | classical | intense | 0.90 | True |
| Edge Case (Loud & Acoustic) | folk | warm | 0.85 | True |

**What matched intuition:** Chill Lofi produced Library Rain and Midnight Coding as #1 and #2. Deep Intense Rock placed Storm Runner first by a wide margin. These results felt exactly right.

**What was surprising:** For High-Energy Pop, Gym Hero (pop, intense) ranked #2 even though the user asked for happy mood — the genre weight outweighed the mood mismatch. For Classical Rage, Winter Cathedral ranked #1 despite being the opposite of what the user wanted in energy and mood. The system had no way to distinguish "wrong kind of classical." For Loud & Acoustic, no folk songs exist in the catalog so the results felt generic.

**Experiment:** Doubling the energy weight and halving the genre weight caused Winter Cathedral to drop from #1 to #3 for the Classical Rage profile, while the well-matched profiles stayed the same. This confirmed that the default weights overfit to genre for unusual profiles.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

- Expand the catalog to at least 5–10 songs per genre so genre matching is meaningful rather than a lottery
- Add a diversity step that prevents the same artist from appearing more than once in the top K
- Allow range-based energy preferences (e.g., "between 0.6 and 0.8") instead of a single point target
- Add support for negative preferences (e.g., "I never want country") to avoid forced genre matches
- Introduce a second pass that injects one "surprise" song from outside the user's genre to break filter bubbles

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this made me realize how much a small design choice — like making genre worth 2 points and mood worth 1 — can completely shape what a user sees. The Classical Rage experiment was genuinely surprising: a song with almost nothing in common with what the user asked for won just because it matched a single categorical field. That made me think differently about how Spotify or TikTok must work. They probably use dozens of signals weighted dynamically, not a fixed recipe. The filter bubble finding stuck with me most. The rock profile never once surfaced a jazz or soul song, even songs that matched well on energy and mood. In a real product used by millions of people, that kind of invisible narrowing would quietly shape what people think music even sounds like — and they would never know it was happening.
