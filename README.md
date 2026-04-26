# 🎵 TuneVision AI

## Original Project Background

This project began as the original Modules 1-3 music recommender: a lightweight Python system that scored songs by genre, mood, energy, and acoustic attributes. Its original goals were to help users discover tracks from a static catalog, explain why a recommendation matched their mood, and provide a foundation for more advanced music discovery features.

## Title and Summary

**TuneVision AI** is an interactive music recommendation system that blends traditional music recommender logic with modern AI. It matters because it turns song metadata into meaningful discovery: users can ask for music in natural language, receive curated recommendations, and get explanations powered by retrieval-augmented generation.

## Architecture Overview

The system is organized around a small set of core components, with clear input/output flow and human validation points:

- **User Interface**: CLI and chat interfaces accept natural-language requests.
- **Chat Agent**: Orchestrates conversation state and routes requests to retrieval and recommendation logic.
- **RAG Engine**: Combines a traditional recommender, a vector semantic search store, and a domain knowledge base.
- **LLM**: Generates conversational responses and explanation text using OpenAI.
- **Extensions**: Mood-based playlist generation and taste analysis provide added personalization.

Data flows like this:

1. User submits a query.
2. The chat agent sends it to the RAG engine.
3. The RAG engine retrieves relevant songs from the vector store, uses background music knowledge, and applies hybrid scoring.
4. The LLM generates a response that explains the recommendation and asks follow-up questions.
5. The result is returned to the user and logged for validation.

For a visual version, see `assets/system_architecture.mmd`.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key for chat features

### Install and Run

```bash
cd tunevision-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Run Modes

- CLI demo:
  ```bash
  python src/main.py
  ```
- RAG demo:
  ```bash
  python src/main.py --rag-demo
  ```
- Interactive chat:
  ```bash
  python src/main.py --chat
  ```
  (Note: The chat interface will automatically find an available port starting from 7860)
- Full feature demo:
  ```bash
  python demo.py
  ```

## Sample Interactions

### Example 1
**Input:** `I want some happy pop music for a sunny day`

**Output:**
- `Sunrise City by Neon Echo`
- `Gym Hero by Max Pulse`
- `Rooftop Lights by Indigo Parade`

**Explanation:** "This song scores 4.8 points because: genre match, energy, valence, and acoustic balance make it a strong happy pop fit."

### Example 2
**Input:** `Find chill lofi beats to study to`

**Output:**
- `Midnight Coding by LoRoom`
- `Crimson Alley by Delta Howl`
- `Focus Flow by LoRoom`

**Explanation:** "Lofi music typically features chill textures and steady energy that supports concentration."

### Example 3
**Input:** `Need intense rock songs for working out`

**Output:**
- `Storm Runner by Voltline`
- `Gym Hero by Max Pulse`
- `Desert Caravan by Nomad Atlas`

**Explanation:** "These tracks are chosen because they match high energy, strong intensity, and dynamic momentum appropriate for workouts."

## Design Decisions

- **Hybrid approach**: I kept the original recommender logic and added vector search so the system works both with rules and semantic similarity.
- **RAG architecture**: Retrieval-augmented generation ensures the LLM has concrete song context and domain facts before answering.
- **Modular design**: Each feature lives in its own file so new functionality can be added without breaking core recommendation flow.
- **Reproducible setup**: Pinning package versions and providing `.env.example` reduces onboarding friction.

### Trade-offs

- I prioritized clarity and stability over a fully production-ready service.
- The system uses a static catalog rather than live streaming metadata, which keeps it easier to inspect and test.
- The OpenAI integration is powerful, but it also depends on API availability and key management.

## Testing Summary

- **What worked:**
  - The full demo script runs end-to-end.
  - `python src/main.py --rag-demo` now completes successfully.
  - Vector-based retrieval, playlist generation, and taste analysis all produce results.

- **What needed attention:**
  - Relative imports had to be converted to absolute imports for CLI execution.
  - LangChain version compatibility required adjustments to memory and prompt handling.

- **What I learned:**
  - Small architecture changes can break execution paths, so consistent import structure matters.
  - Logging and graceful error handling are essential for debugging AI pipelines.
  - Explicit setup instructions make the repo easier for a future reviewer to run without guessing.

## Reliability and Evaluation

- **Automated tests:** `python3 -m pytest -q tests/test_recommender.py` passes `2/2` unit tests, validating core scoring and explanation logic.
- **Score-based confidence:** The recommender returns numeric song scores that can act as proxy confidence values for ranking and reranking decisions.
- **Logging and error handling:** The system logs activity and failures, including API errors, data loading issues, and recommendation failures, making root cause analysis repeatable.
- **Human evaluation:** Sample interaction examples and manual review of generated responses help verify that the output is reasonable and aligned with user intent.

## Reflection

This project taught me how to turn an educational recommender prototype into a more complete AI system by integrating retrieval, generation, and domain knowledge. It also reinforced the importance of designing for maintainability, reproducibility, and human-readable explanations when building AI systems for real users.

## Ethics and Responsible AI

### Limitations and Biases
The system relies on a static song catalog, which may not reflect current music trends or diverse cultural representations. The scoring algorithm assumes certain genre-mood correlations that could perpetuate stereotypes (e.g., assuming all "rock" music is high-energy). Additionally, the LLM component depends on OpenAI's training data, which may contain biases in how it interprets music preferences or generates responses.

### Potential Misuse and Prevention
The AI could be misused to generate biased recommendations or spread misinformation about music/artists. To prevent this, I've implemented input validation, comprehensive logging for audit trails, and clear disclaimers in the interface. In a production setting, I'd add rate limiting, content moderation, and user feedback loops to identify and correct problematic outputs.

### Surprises in Testing
I was surprised by how import path issues could break the entire system despite the code being functionally correct—small architectural decisions like relative vs. absolute imports had outsized impacts on reliability. The RAG system also performed better than expected on straightforward queries but struggled with ambiguous ones, highlighting the importance of robust fallback mechanisms.

### Collaboration with AI
Throughout this project, I collaborated extensively with AI tools like GitHub Copilot for code suggestions and debugging. One helpful instance was when Copilot suggested the correct Mermaid syntax for the system architecture diagram, saving me time on formatting. However, it once suggested using deprecated LangChain memory classes, which led to import errors that required manual fixes—reminding me to always verify AI-generated code against current documentation.

---

## Additional Notes

- The repository is intended for portfolio review and demonstration rather than large-scale deployment.
- The design supports future extensions such as collaborative filtering, Spotify integration, and richer conversational memory.
- See `model_card.md` for more detail on capabilities and limitations.

**Built with:** Python, Sentence Transformers, FAISS, LangChain, Gradio, OpenAI
