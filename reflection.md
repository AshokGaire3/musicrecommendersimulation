# Reflection: Comparing Profiles and Outputs

## High-Energy Pop vs. Chill Lofi

These two profiles are almost perfect opposites, and the outputs reflect that completely. High-Energy Pop pushes songs like Sunrise City and Gym Hero to the top — fast, electronic, high-energy tracks with happy or intense moods. Chill Lofi pushes Library Rain and Midnight Coding to the top — slow, acoustic, low-energy tracks built for studying or relaxing. The reason the gap is so wide is that both genre and energy point in the same direction for each profile. When multiple features agree, the scoring system gets very confident, and the top scores are high and well-separated from the rest.

One interesting observation: Gym Hero (pop, intense, energy 0.93) shows up at #2 for the High-Energy Pop user even though that user asked for a "happy" mood. A non-programmer might ask: "Why am I getting a workout song when I said I wanted happy music?" The answer is that genre (2 points) outweighs mood (1 point) in the current design. So a pop song with the wrong mood still beats a non-pop song with the right mood. It is not wrong exactly, but it shows the system prioritizes what category a song belongs to over how it feels.

---

## Deep Intense Rock vs. Adversarial (Classical Rage)

Both profiles want high energy (0.88 and 0.90) and an intense mood. The difference is genre — one asks for rock, the other asks for classical. The rock profile works beautifully: Storm Runner (rock, intense, energy 0.91) is a near-perfect match and ranks #1 by a wide margin. The classical profile completely breaks down: Winter Cathedral (classical, contemplative, energy 0.22) ranks #1 despite being the slowest, softest song in the entire catalog.

Why does this happen? There is only one classical song in the dataset. The genre weight (2 points) is high enough that matching genre alone is worth more than having the right energy and mood combined. So the system "thinks" it is doing the right thing — it found the classical song — but it has no way to know that classical + high energy + intense mood is a combination the catalog cannot actually serve. This is the clearest example of how a small dataset combined with a strong categorical weight creates a misleading result.

To a non-programmer: imagine asking a music store clerk for "an intense, high-energy classical piece" and they hand you a slow, quiet church hymn and say "that is the only classical CD we have." The genre label matched, but everything else missed.

---

## Edge Case (Loud & Acoustic) — What happens when a genre is missing

The folk profile was designed to find a gap in the catalog. There are no folk songs. With no genre match possible, the scoring falls back on energy proximity and the acoustic bonus. The top 5 end up being a mix of whatever songs have decent energy (0.85 target) and some acoustic content — Golden Fields (country, warm, 0.47 energy) wins because it is the only song with the right mood (warm) and a high acoustic score (0.84), even though its energy (0.47) is far from the target.

This shows a real limitation: when a user's genre is absent, the system does not tell them "we don't have what you want." It quietly substitutes the next best thing based on other features. In a real app, a missing genre should trigger a message or expand the catalog — silently returning mediocre matches is worse than being honest about the gap.

---

## What the Weight-Shift Experiment Taught Me

When I doubled the energy weight and halved the genre weight, the Chill Lofi and Deep Intense Rock profiles barely changed. But the Classical Rage profile flipped — Winter Cathedral dropped from #1 to #3, replaced by Storm Runner and Gym Hero which both matched on mood and energy. This told me that the default weights work well for "normal" profiles where genre, mood, and energy all agree, but they over-trust genre for unusual profiles. The fix is not necessarily to change the weights globally — it might be smarter to make the genre weight dynamic based on how many songs exist in that genre.

---

## Overall Takeaway

The most important thing I learned is that a recommender system is never just math — it is a set of values baked into numbers. Choosing genre = 2.0 and mood = 1.0 is saying "what kind of music matters more than how it makes you feel." That might be right for some users and completely wrong for others. Real platforms like Spotify probably adjust these weights per user based on what they actually skip or replay. My version cannot do that, but building it showed me exactly why that kind of feedback loop matters.
