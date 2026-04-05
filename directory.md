yt-flashcard-generator/
│
├── app/                           # ← FastAPI application (all HTTP stuff)
│   ├── main.py                    # FastAPI app initialization & startup
│   │
│   ├── routes/                    # ← HTTP endpoints (the API handlers)
│   │   └── generate.py            # POST /api/v1/generate endpoint
│   │
│   ├── services/                  # ← Business logic (the pipeline)
│   │   ├── transcript.py          # Extract YouTube captions
│   │   ├── cleaner.py             # Clean/normalize text
│   │   ├── chunker.py             # Split text into chunks
│   │   └── generator.py           # Run T5 model on chunks
│   │
│   ├── schemas/                   # ← Input/output validation (Pydantic)
│   │   └── flashcard.py           # Define request & response structures
│   │
│   ├── models/                    # ← Database models (Phase 4)
│   │   └── flashcard.py           # SQLAlchemy models
│   │
│   └── utils/                     # ← Helper stuff
│       └── errors.py              # Custom exceptions
│
├── ml/                            # ← Machine Learning models
│   └── t5_model/                  # Where T5 model is stored/cached
│
├── tests/                         # ← Testing & validation
│   └── pipeline_test.py           # PHASE 1: Test the whole pipeline works
│
├── requirements.txt               # List of Python packages
├── instructions.md                # Guidelines (what we just created)
└── [other config files]


Data flow

User provides YouTube URL
         ↓
   routes/generate.py (HTTP handler)
         ↓
   services/transcript.py ← Extract captions
         ↓
   services/cleaner.py ← Normalize text
         ↓
   services/chunker.py ← Split into chunks
         ↓
   services/generator.py ← Run T5 model
         ↓
   schemas/flashcard.py ← Format as JSON
         ↓
   HTTP Response (JSON flashcards)