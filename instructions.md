# YouTube Flashcard Generator — Development Guidelines

This document serves as the **development context** for the entire project. Follow these standards to keep the codebase clean and scalable.

---

## 📋 Table of Contents
1. [Project Phases](#project-phases)
2. [Code Organization](#code-organization)
3. [REST API Standards](#rest-api-standards)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Testing & Validation](#testing--validation)
7. [Future Phases](#future-phases)

---

## 🚀 Project Phases

### Phase 1: Core Pipeline (CURRENT) ✅
**Goal:** Validate that the pipeline produces quality JSON flashcards.

- ✅ Extract transcript from YouTube URL
- ✅ Clean and normalize text
- ✅ Chunk text intelligently (200–400 words)
- ✅ Generate Q&A pairs using T5 model
- ✅ Output valid JSON format

**Deliverable:** `tests/pipeline_test.py` working end-to-end

**Success Criteria:**
- Pipeline runs without errors
- JSON output is valid and properly formatted
- Flashcard quality is acceptable (questions make sense, answers are relevant)

---

### Phase 2: FastAPI Backend (NEXT)
**Goal:** Wrap the pipeline behind REST endpoints.

- Create `/generate` endpoint (POST)
- Input validation (YouTube URL format)
- Response streaming for long videos
- Error handling and logging
- Rate limiting (if needed)

**Endpoints:**
```
POST   /api/v1/generate        # Main endpoint
GET    /api/v1/health          # Health check
```

---

### Phase 3: Frontend (Vue + Tailwind)
**Goal:** Interactive UI for generating and viewing flashcards.

- Form to submit YouTube URLs
- Progress indicator during generation
- Flashcard display/edit interface
- Tailwind CSS for styling

---

### Phase 4: Authentication & Database
**Goal:** Persist data and add user accounts.

- User registration/login (JWT tokens)
- Store generated flashcards in database
- Retrieve user's previous flashcard sets
- Edit/delete flashcards

---

## 📁 Code Organization

### Do NOT deviate from this structure:

```
yt-flashcard-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── generate.py              # POST /api/v1/generate
│   │
│   ├── services/                    # Business logic (pipeline)
│   │   ├── __init__.py
│   │   ├── transcript.py            # YouTube transcript extraction
│   │   ├── cleaner.py               # Text normalization
│   │   ├── chunker.py               # Text chunking logic
│   │   └── generator.py             # T5 model integration
│   │
│   ├── schemas/                     # Pydantic validation models (Phase 2)
│   │   ├── __init__.py
│   │   └── flashcard.py             # Request/response schemas
│   │
│   ├── models/                      # Database models (Phase 4)
│   │   ├── __init__.py
│   │   └── flashcard.py             # SQLAlchemy models
│   │
│   └── utils/                       # Helpers
│       ├── __init__.py
│       └── errors.py                # Custom exceptions
│
├── ml/
│   ├── t5_model/                    # Saved/fine-tuned T5 model
│   └── __init__.py
│
├── tests/
│   ├── __init__.py
│   └── pipeline_test.py             # Phase 1 validation script
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore
├── README.md                        # Project documentation
└── instructions.md                  # This file
```

### Naming Conventions:
- **Files:** `snake_case.py`
- **Functions/Variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_CASE`
- **Private methods:** `_private_method()`

---

## 🌐 REST API Standards

### Base URL
```
http://localhost:8000/api/v1
```

### Versioning
- All endpoints start with `/api/v1`
- Future versions: `/api/v2`, etc.

### HTTP Methods
- `POST` — Create/generate something
- `GET` — Retrieve data
- `PUT/PATCH` — Update data (Phase 4)
- `DELETE` — Remove data (Phase 4)

### URL Naming
- Use **nouns, not verbs**: `/generate`, `/results`
- Use **plural for collections**: `/api/v1/flashcards`
- Avoid nested paths: Use query params instead

### Status Codes
- `200` — Success
- `201` — Created (Phase 4)
- `400` — Bad request (validation error)
- `401` — Unauthorized (Phase 4)
- `404` — Not found
- `500` — Server error

---

## 📊 Response Format

### ALL responses must follow this structure:

```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "error": null
}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "flashcards": [
      {
        "question": "What is photosynthesis?",
        "answer": "Process by which plants convert light into energy.",
        "chunk_index": 0
      }
    ],
    "metadata": {
      "total_cards": 15,
      "processing_time": 12.5,
      "video_duration": 45
    }
  },
  "message": "Flashcards generated successfully",
  "error": null
}
```

### Error Response (400)
```json
{
  "success": false,
  "data": null,
  "message": "Invalid YouTube URL format",
  "error": {
    "type": "ValidationError",
    "details": "URL must contain 'youtube.com' or 'youtu.be'"
  }
}
```

### Flashcard Object Structure
```json
{
  "question": "String (concise, clear)",
  "answer": "String (fact-based, relevant to chunk)",
  "chunk_index": "Integer (which chunk generated this)",
  "confidence": "Float 0-1 (optional, Phase 3)"
}
```

---

## ⚠️ Error Handling

### Custom Exceptions (in `app/utils/errors.py`):
```python
class FlashcardGeneratorError(Exception):
    """Base exception for all pipeline errors"""
    pass

class InvalidYouTubeURLError(FlashcardGeneratorError):
    """Raised when URL is not valid"""
    pass

class TranscriptExtractionError(FlashcardGeneratorError):
    """Raised when transcript cannot be extracted"""
    pass

class ModelError(FlashcardGeneratorError):
    """Raised when T5 model fails"""
    pass
```

### Handling in Routes:
```python
@router.post("/generate")
async def generate(url: str):
    try:
        # Your logic
        pass
    except InvalidYouTubeURLError as e:
        return {
            "success": false,
            "data": null,
            "message": str(e),
            "error": {"type": "InvalidYouTubeURLError"}
        }
    except Exception as e:
        # Log this!
        return {
            "success": false,
            "data": null,
            "message": "Internal server error",
            "error": {"type": "UnknownError"}
        }
```

---

## 🧪 Testing & Validation

### Phase 1: Pipeline Testing
**File:** `tests/pipeline_test.py`

```python
# Must include:
# 1. Test with a real YouTube URL
# 2. Validate JSON output structure
# 3. Check flashcard quality (not empty, sensible content)
# 4. Measure processing time

def test_full_pipeline():
    url = "https://www.youtube.com/watch?v=..."
    flashcards = generate_flashcards(url)
    
    assert isinstance(flashcards, list)
    assert len(flashcards) > 0
    assert all("question" in card for card in flashcards)
    assert all("answer" in card for card in flashcards)
```

### Phase 2+: Unit Tests
- Test each service independently: `transcript.py`, `cleaner.py`, `chunker.py`, `generator.py`
- Test API endpoints with mock data
- Use `pytest` for all testing

### Input Validation Rules
- YouTube URL must be valid format (use `youtube-transcript-api` validation)
- Reject URLs that don't have transcripts available
- Validate all API request bodies with Pydantic schemas

---

## 🎯 Best Practices (CRITICAL)

### 1. Separation of Concerns
- **Services** (`app/services/`) — Pure business logic, no HTTP concepts
- **Routes** (`app/routes/`) — HTTP handling, validation, response formatting
- **Models** (`app/models/`) — Database structure (Phase 4)

### 2. Dependency Injection (Phase 2)
```python
# Use FastAPI's dependency system
from fastapi import Depends

def get_model():
    return T5Model()

@router.post("/generate")
async def generate(model = Depends(get_model)):
    pass
```

### 3. Logging (Phase 2)
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("Processing started")
    logger.error("Something failed")
```

### 4. Configuration (Phase 2)
Use environment variables:
```python
# .env
T5_MODEL_SIZE=small
MAX_CHUNK_SIZE=400
MIN_CHUNK_SIZE=100
```

### 5. Documentation
- Every function needs a docstring
- Add type hints to all functions
- Example:
```python
def chunk_text(text: str, max_words: int = 200) -> List[str]:
    """
    Split text into chunks of approximately max_words length.
    
    Args:
        text: Raw text to chunk
        max_words: Maximum words per chunk
        
    Returns:
        List of text chunks
    """
    pass
```

---

## 🔮 Future Phases (Planning)

### Phase 3: Frontend (Vue + Tailwind)
- Use **Tailwind CSS** for all styling (no custom CSS)
- Component structure: `/src/components/`
- Use **Vue 3 Composition API**
- State management: Pinia (or simple context)

### Phase 4: Auth & Database
- **Database:** PostgreSQL (local for dev, cloud for production)
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens, HTTP-only cookies
- **Hashing:** bcrypt for passwords

### Tailwind Convention
```html
<!-- Use utility classes ONLY -->
<div class="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
  <h1 class="text-2xl font-bold text-gray-900">Flashcards</h1>
  <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
    Generate
  </button>
</div>

<!-- NO custom CSS classes -->
<!-- DO NOT: <div class="my-custom-div"></div> -->
```

---

## ✅ Development Checklist

### Getting Started
- [ ] Read this file completely
- [ ] Create folder structure exactly as shown
- [ ] Set up virtual environment
- [ ] Install dependencies from `requirements.txt`
- [ ] Create test video URL for `tests/pipeline_test.py`

### Phase 1 Completion
- [ ] `tests/pipeline_test.py` runs successfully
- [ ] Generates valid JSON flashcards
- [ ] Output quality is acceptable
- [ ] Handles errors gracefully

### Phase 2 Entry
- [ ] Implement Pydantic schemas
- [ ] Create FastAPI routes
- [ ] Test endpoints with Swagger UI
- [ ] Add logging

---

## 📞 Questions to Answer Before Coding

1. **Video Selection:** Which short (<15 min) YouTube video will you test with?
2. **Chunk Size:** Will 200–400 words work, or adjust based on topic?
3. **Output Validation:** How will you measure "good" flashcards?
4. **Error Tolerance:** If 1 out of 50 cards is bad, is that acceptable?

**Answer these before starting Phase 2.**

---

## 🎯 Success Metric (Phase 1)

> **You succeed when:** You can run `python tests/pipeline_test.py` with a real YouTube URL and get back a JSON list of 10+ flashcards that make sense.

That's it. Everything else comes after.
