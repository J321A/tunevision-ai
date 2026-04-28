# 🎵 TuneVision AI

## Project Goals

**TuneVision AI** transforms a basic music recommender into a comprehensive AI-powered system that combines traditional recommendation algorithms with modern machine learning techniques. The project demonstrates how to build production-ready AI systems that are:

- **Conversational:** Users can ask for music in natural language
- **Explainable:** Every recommendation comes with detailed reasoning
- **Hybrid:** Combines rule-based scoring with semantic vector search
- **Modular:** Clean architecture supporting easy extensions
- **Reproducible:** Well-documented setup and comprehensive testing

## New Features (Beyond Original Recommender)

- **🤖 AI Chat Interface:** Conversational music recommendations powered by OpenAI GPT
- **🔍 Vector Search:** Semantic similarity search using Sentence Transformers and FAISS
- **📚 RAG Architecture:** Retrieval-Augmented Generation combining knowledge base with LLM responses
- **🎯 Hybrid Scoring:** Traditional recommender logic enhanced with vector similarity
- **📊 Taste Analysis:** User preference tracking and personalized insights
- **🎵 Playlist Generation:** Mood-based playlist creation
- **🌐 Web Interface:** Gradio-based chat UI with real-time interactions
- **📈 Comprehensive Testing:** Unit tests, integration tests, and performance validation

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
- OpenAI API key for chat features (optional - system works without it)

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd tunevision-ai
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key (optional)
   ```

5. **Run the system:**
   ```bash
   # Basic CLI demo
   python src/main.py

   # Interactive chat interface
   python src/main.py --chat

   # Run tests
   python -m pytest tests/
   ```

### Run Modes

- **CLI demo** (`python src/main.py`):
  Shows sample recommendations with different user profiles and scoring modes.

- **RAG demo** (`python src/main.py --rag-demo`):
  Demonstrates the retrieval-augmented generation system with natural language queries.

- **Interactive chat** (`python src/main.py --chat`):
  Launches a web-based chat interface for conversational music recommendations.

- **Full feature demo** (`python demo.py`):
  Runs comprehensive demonstrations of all system capabilities.

## Sample Interactions

### CLI Mode Examples

**Input Profile:** Happy pop music for a sunny day
```
════════════════════════════════════════════════════════════════════
  2020 Pop Hits
  Mode: BALANCED  |  Max score: 9.5
  genre=pop | mood=happy | energy=0.8 | decade=2020 | tags=['uplifting', 'carefree']
════════════════════════════════════════════════════════════════════

Top Recommendations:
#1 Sunrise City by Neon Echo (pop, happy) - Score: 9.22/9.5
   Genre match (+2.0) | Mood match (+1.0) | Energy (+1.96) | Valence (+0.96) | Acoustic (+0.82)

#2 Gym Hero by Max Pulse (pop, intense) - Score: 7.12/9.5
   Genre match (+2.0) | Energy (+1.74) | Valence (+0.97) | Acoustic (+0.95)

#3 Rooftop Lights by Indigo Parade (indie pop, happy) - Score: 6.00/9.5
   Mood match (+1.0) | Energy (+1.92) | Valence (+0.99) | Acoustic (+0.65)
```

### Chat Interface Examples

**User Input:** "I want upbeat pop music for working out"

**System Response:**
```
Based on your request for upbeat pop music for working out, here are some recommendations:

**Recommended Songs:**
1. **Sunrise City** by *Neon Echo*
   - Genre: pop | Mood: happy | Energy: 0.82
   - Why it fits: This energetic pop track with high valence and moderate acoustic elements would be perfect for a workout session.

2. **Gym Hero** by *Max Pulse*
   - Genre: pop | Mood: intense | Energy: 0.93
   - Why it fits: High-energy pop music that matches your workout intensity preference.

3. **Rooftop Lights** by *Indigo Parade*
   - Genre: indie pop | Mood: happy | Energy: 0.76
   - Why it fits: Upbeat indie pop with good energy levels for maintaining workout motivation.
```

**User Input:** "Find me some chill lofi beats to study to"

**System Response:**
```
For chill lofi beats to study to, I've found these tracks that match your preferences:

**Recommended Songs:**
1. **Midnight Coding** by *LoRoom*
   - Genre: lofi | Mood: chill | Energy: 0.42
   - Why it fits: Perfect lofi chill vibes with moderate energy that won't distract from studying.

2. **Library Rain** by *Paper Lanterns*
   - Genre: lofi | Mood: chill | Energy: 0.35
   - Why it fits: Very chill lofi with low energy, ideal for focused study sessions.

3. **Focus Flow** by *LoRoom*
   - Genre: lofi | Mood: focused | Energy: 0.40
   - Why it fits: Lofi music designed for concentration and productivity.
```

### RAG Demo Examples

**Natural Language Query:** "Need intense rock songs for driving"

**System Analysis:**
```
Query parsed as: genre=rock, mood=intense, energy=high, context=driving
Retrieving relevant songs from vector store...
Applying hybrid scoring with domain knowledge...

Top matches:
1. Storm Runner by Voltline (rock, intense) - Score: 8.80
2. Gym Hero by Max Pulse (pop, intense) - Score: 5.35
3. Desert Caravan by Nomad Atlas (world fusion, adventurous) - Score: 5.18
```

## Demo Walkthrough

> A short video walkthrough of the system in action.

[![Demo](assets/demo-thumbnail.png)](https://www.loom.com/share/1a914014972546af994d3654fb3a6254)


## Design Decisions

- **Hybrid approach**: I kept the original recommender logic and added vector search so the system works both with rules and semantic similarity.
- **RAG architecture**: Retrieval-augmented generation ensures the LLM has concrete song context and domain facts before answering.
- **Modular design**: Each feature lives in its own file so new functionality can be added without breaking core recommendation flow.
- **Reproducible setup**: Pinning package versions and providing `.env.example` reduces onboarding friction.

### Trade-offs

- I prioritized clarity and stability over a fully production-ready service.
- The system uses a static catalog rather than live streaming metadata, which keeps it easier to inspect and test.
- The OpenAI integration is powerful, but it also depends on API availability and key management.

## Testing

### Automated Tests

Run the test suite to verify system functionality:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_recommender.py -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Expected Results:**
- `2/2 tests pass` for the recommender unit tests
- All core functionality (scoring, recommendations, explanations) validated

### Manual Testing

1. **CLI Mode:** Run `python src/main.py` and verify sample profiles produce reasonable recommendations
2. **Chat Interface:** Run `python src/main.py --chat` and test natural language queries
3. **RAG Demo:** Run `python src/main.py --rag-demo` and verify vector search + recommendations work
4. **Full Demo:** Run `python demo.py` for comprehensive feature demonstration

### Performance Validation

- **Response Time:** Chat queries should respond within 5-10 seconds
- **Accuracy:** Top recommendations should match user preferences (genre, mood, energy)
- **Robustness:** System should handle edge cases gracefully (empty queries, invalid preferences)

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

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Chat interface won't start:**
```bash
# Kill any existing processes on port 7860
lsof -ti:7860 | xargs kill -9
# Try again
python src/main.py --chat
```

**OpenAI API errors:**
- Check your API key in `.env` file
- Verify your OpenAI account has credits
- The system works without API key (limited chat features)

**Import errors:**
- Ensure you're running from the project root directory
- Check that all files are in `src/` directory
- Try: `PYTHONPATH=src python src/main.py`

### Performance Tips

- First run may be slow due to model downloads
- Chat responses take 5-10 seconds with API calls
- System works offline for basic recommendations
