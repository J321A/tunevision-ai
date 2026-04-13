# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder tries to answer one question: *"Given what a user says they like, which songs in the catalog are the closest match?"*

It does not learn from listening history or past behavior. It takes a user's stated preferences — genre, mood, energy level, emotional brightness, and acoustic preference — and uses a scoring formula to find songs that match those preferences as closely as possible. The output is a ranked list of up to 5 songs with an explanation for each result.

---

## 3. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based recommender systems work
- Learning how weighted scoring, proximity math, and feature matching translate into ranked results
- Understanding where simple algorithms succeed and where they break down

**Not intended for:**
- Real users making real music decisions — the catalog is too small (20 songs) to be genuinely useful
- Replacing professional recommendation systems like Spotify or Apple Music
- Making decisions about artists or their music (e.g., "this artist's music is low quality because it scores poorly")
- Any commercial or production use

---

## 4. Data Used

- **Catalog size:** 20 songs
- **Features per song:** genre (text label), mood (text label), energy (0.0–1.0), tempo in BPM (number), valence (0.0–1.0), danceability (0.0–1.0), acousticness (0.0–1.0)
- **Genres represented:** pop, lofi, rock, metal, blues, jazz, ambient, synthwave, indie pop, folk, edm, reggae, classical, world fusion, cinematic, indie folk, experimental (17 total)
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, melancholic, euphoric, aggressive, laid-back, nostalgic, hopeful, serene, adventurous, epic (15 total)

**Limits of the data:**
- 15 of the 17 genres have only one song. A user who prefers blues or classical will always get that single song at #1, then see unrelated songs for the remaining slots.
- The data was manually constructed for a classroom exercise. It does not reflect real-world listening patterns or cultural diversity in music.
- Features like energy and valence are made-up numbers — they are not measured from actual audio.

---

## 5. Algorithm Summary

Each song gets a score from 0 to 7. The score is the sum of five signals:

| Signal | Max Points | How it works |
|---|---|---|
| Genre match | 2.0 | Full 2 points if the song's genre exactly matches the user's preferred genre; otherwise 0 |
| Mood match | 1.0 | Full 1 point if the song's mood exactly matches the user's preferred mood; otherwise 0 |
| Energy closeness | 2.0 | Up to 2 points based on how close the song's energy is to the user's target. A song that is 0.1 away loses about 0.2 points. |
| Valence closeness | 1.0 | Up to 1 point based on how close the song's emotional brightness is to the user's target. Same math as energy. |
| Acoustic fit | 1.0 | Up to 1 point: if the user likes acoustic music, songs with higher acousticness score higher. If the user prefers electronic, the reverse applies. |

The "closeness" formula is: `points = weight × (1 − distance)`. If a song is a perfect energy match, distance is 0 and the full 2 points are awarded. If it is at the opposite extreme (distance of 1.0), it gets 0 points.

After every song in the catalog is scored, they are sorted from highest to lowest and the top 5 are returned with a written explanation for each.

---

## 6. Observed Behavior and Biases

**Genre is too powerful for niche listeners.**
When a user wants blues music, the one blues song in the catalog gets 3 points just from matching genre and mood — more than any other song can earn from energy or valence closeness. This means the blues song always ranks #1 even if its tempo and energy are completely wrong for that user. The system creates a "lock-in" effect for underrepresented genres.

**One high-energy song appears in too many results.**
Gym Hero (pop, intense, energy 0.93) shows up in the top 5 for both the happy-pop profile and the intense-rock profile. Because it has the highest energy in the catalog and is almost fully electronic, it earns high scores for any user who wants high energy and doesn't prefer acoustic music — regardless of genre. A good recommender should not let one song dominate across very different profiles.

**The system cannot handle conflicting preferences.**
Testing an "adversarial" profile — someone who wants melancholic blues but with very high energy — showed that the system picks the right genre first, then fills the remaining slots with unrelated aggressive metal songs. There is no way for the scoring formula to recognize that the user's preferences are in tension with each other.

**Labels are all-or-nothing.**
"indie pop" and "pop" are treated as completely unrelated, even though a pop fan would probably enjoy both. Any genre or mood that doesn't exactly match the user's preference gets zero points, with no partial credit for nearby categories.

---

## 7. Evaluation Process

Four user profiles were tested:

1. **High-Energy Pop** (genre=pop, mood=happy, energy=0.80) — tested whether the most common profile produces intuitive results. It did: Sunrise City ranked first at 6.74/7.00, which is exactly what a pop/happy listener should see.

2. **Chill Lofi Study Session** (genre=lofi, mood=chill, energy=0.38) — tested a well-represented niche. Results were very accurate: the two chill lofi songs ranked first and second with high scores.

3. **Deep Intense Rock** (genre=rock, mood=intense, energy=0.92) — tested whether the system handles a genre with only one catalog entry. Storm Runner was correctly #1. Gym Hero (pop, intense) was an unexpected but somewhat logical #2 — shared mood and energy without any genre overlap.

4. **Adversarial: Blues + Melancholic + High Energy** — tested what happens when preferences conflict. The system correctly found the one blues song but completely failed for slots #2–5, filling them with aggressive metal and rock songs that share only high energy with the user's request.

**Experiment:** Running the pop profile again with energy weight doubled (4.0) and genre weight halved (1.0) caused the ranking to shift: Rooftop Lights (indie pop) jumped from #3 to #2, passing Gym Hero. This confirmed that the original weights favor genre identity over how the song actually sounds.

**What I looked for:** Whether the #1 result "felt right," whether the same songs dominated multiple profiles (they did — Gym Hero), and whether changing weights produced meaningfully different results (they did).

---

## 8. Ideas for Improvement

- **Add tempo as a scored feature.** Right now, two songs at 60 BPM and 150 BPM can score identically if their energy values happen to be similar. Tempo would help distinguish a slow ballad from a fast dance track, which are very different listening experiences.

- **Replace the binary acoustic preference with a float target.** Saying `likes_acoustic = True/False` loses information. A user who wants "slightly acoustic" gets treated the same as one who wants "fully unplugged folk guitar," and the scoring cannot tell them apart.

- **Reduce the genre weight when catalog coverage is low.** If a genre has only one song, the genre match should be worth less — not more. Penalizing the genre bonus based on how many songs represent it would reduce the filter-bubble effect for niche listeners.

---

## 9. Personal Reflection

**Biggest learning moment:**
The adversarial profile test was the clearest lesson. A user who asks for "energetic blues" gets a slow blues song at #1 and then aggressive metal for every other slot. That is not a bad result because the math is wrong — the math is doing exactly what it was told. The real problem is that the formula has no way to know when the user's own preferences conflict. Writing a scoring function is easy; writing one that handles human nuance is the hard part that real AI systems spend enormous resources on.

**How AI tools helped and when I needed to verify them:**
AI-assisted suggestions were most useful for the structure — how to set up the data flow, what a proximity formula should look like, and how to organize the weight table. But I had to verify every specific number. The AI would suggest a weight or formula that "looked right" but produced a max score of 8.0 instead of 7.0, or use `.sort()` where `sorted()` was needed. The most important lesson: AI tools can propose a design quickly, but you still have to run the code, check the output, and ask "does this number actually make sense?"

**What surprised me about simple algorithms feeling like recommendations:**
The lofi profile was the most surprising moment. Library Rain and Midnight Coding ranked first and second almost perfectly — and seeing the formula return those two songs felt like the system genuinely "understood" what a chill study session sounds like. It doesn't understand anything, of course. It just matched numbers to numbers. But that experience made it easy to see why people trust recommendation systems: when they work, they produce results that feel personal and intuitive, even though the underlying logic is entirely mechanical.

**What I would try next:**
The most interesting next step would be to let users rate a few songs (liked / disliked), then automatically adjust the weights based on those ratings. If a user skips every high-energy song the system recommends, the energy weight should decrease. That feedback loop is the bridge between a hand-tuned formula like this one and a real learning system — and it would make the recommender feel much more adaptive over time.
