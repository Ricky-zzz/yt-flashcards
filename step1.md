# YouTube → Flashcard Generator (Initial Development Plan)

## 🎯 Project Goal
Build a system that converts YouTube lecture videos into interactive flashcards using NLP.

---

## 🧠 Development Strategy

> Focus on the **ML pipeline first**, then backend, then frontend.

---

## 📌 Phase 1 — Core Pipeline (CRITICAL)

### Objective
Validate that the system can generate meaningful flashcards from a YouTube video.

### Pipeline Flow
```

YouTube URL → Transcript → Clean → Chunk → LLM (Gemini/Groq) → Flashcards → Classifier

````

### Tasks
- [ ] Extract transcript using `youtube-transcript-api`
- [ ] Clean transcript (remove noise, normalize text)
- [ ] Split text into chunks (200–400 words)
- [ ] Integrate LLM generator (Gemini as primary, Groq fallback)
- [ ] Add API keys to `.env` and verify loading
- [ ] Generate Q&A pairs from chunks (JSON)
- [ ] Classify questions (difficulty, type, topic)
- [ ] Combine outputs into flashcard list

### Output Format
```json
[
  {
    "question": "What is photosynthesis?",
    "answer": "Process by which plants convert light into energy."
  }
]
````

### Deliverable

* Working Python script (`pipeline_test.py`)
* Console output of generated flashcards
* No quota errors with fallback in place

---

## ✅ Plan For Tomorrow (Phase 1 finish)

- Get new Gemini key for the new project and wait for free-tier quota to show
- Create Groq key and add `GROQ_API_KEY` to `.env`
- Re-run pipeline test (2 chunks, 3 pairs)
- Confirm fallback works on 429 (Gemini → Groq)
- Save sample outputs for demo and review quality

