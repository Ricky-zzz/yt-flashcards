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

YouTube URL → Transcript → Clean → Chunk → T5 Model → Flashcards

````

### Tasks
- [ ] Extract transcript using `youtube-transcript-api`
- [ ] Clean transcript (remove noise, normalize text)
- [ ] Split text into chunks (200–400 words)
- [ ] Integrate T5 model (`t5-small` or `t5-base`)
- [ ] Generate Q&A pairs from chunks
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

