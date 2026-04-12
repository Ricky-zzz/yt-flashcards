# Phase 2: FastAPI REST API

## Overview

Phase 2 transforms the pipeline into a working REST API that users can interact with via HTTP requests.

## Goals

✓ Create FastAPI application  
✓ Build POST `/api/generate` endpoint  
✓ Add request/response validation (Pydantic)  
✓ Create Swagger UI for interactive testing  
✓ Improve Q&A generation (optional: use better model)  
✓ Add error handling & logging  

## Architecture

### Endpoint: POST `/api/generate`

**Request:**
```json
{
  "youtube_url": "https://youtu.be/VIDEO_ID",
  "num_pairs": 3,
  "max_chunks": 5
}
```

**Response:**
```json
{
  "status": "success",
  "video_url": "https://youtu.be/VIDEO_ID",
  "flashcards": [
    {
      "chunk_index": 0,
      "question": "What is an atom?",
      "answer": "An atom is the smallest unit of matter..."
    },
    ...
  ],
  "metadata": {
    "words_extracted": 8569,
    "chunks_created": 3,
    "pairs_generated": 9,
    "processing_time": 12.5
  }
}
```

## File Structure (After Phase 2)

```
yt_transcript/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app setup
│   ├── routes/
│   │   └── generate.py      # API routes
│   ├── schemas.py           # Pydantic models
│   ├── services/
│   │   └── (Phase 1 services unchanged)
│   └── utils.py             # Helper functions
├── tests/
│   ├── pipeline_test.py     # Existing
│   └── test_api.py          # New: API tests
├── requirements.txt         # Dependencies
└── main.py                  # Entry point
```

## Key Components

### 1. Schemas (Pydantic Models)

**app/schemas.py**

```python
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    youtube_url: str
    num_pairs: int = 3
    max_chunks: int = 5

class FlashcardItem(BaseModel):
    chunk_index: int
    question: str
    answer: str

class GenerateResponse(BaseModel):
    status: str
    video_url: str
    flashcards: List[FlashcardItem]
    metadata: dict
```

### 2. Routes (API Endpoints)

**app/routes/generate.py**

- POST `/api/generate` - Generate flashcards from YouTube URL
- GET `/api/health` - Health check

### 3. Main Application

**app/main.py**

- Initialize FastAPI app
- Mount routes
- Configure CORS (for future frontend)
- Setup logging

### 4. Entry Point

**main.py** (root)

```python
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## How to Run (Phase 2)

```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # Mac/Linux

# Install new dependencies
pip install -r requirements.txt

# Start server
python main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --port 8000
```

**Access:**
- API: http://localhost:8000/api/generate
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing Phase 2

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click "Try it out" on POST /api/generate
3. Enter request body:
```json
{
  "youtube_url": "https://youtu.be/KyBgxe-rU48",
  "num_pairs": 3,
  "max_chunks": 3
}
```
4. Click "Execute"

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://youtu.be/KyBgxe-rU48",
    "num_pairs": 3,
    "max_chunks": 3
  }'
```

### Automated Tests

```bash
pytest tests/test_api.py -v
```

## Model Integration Options

### Option A: Keep Current Extractive Method
- ✅ Fast, deterministic
- ❌ Lower quality

### Option B: Mistral 7B (Local)
- ✅ High quality, free
- ❌ 5-15 second response time per Q&A
- ❌ Requires Ollama setup

### Option C: ChatGPT API
- ✅ Instant, highest quality
- ✅ Best for demos
- ❌ Costs $0.001-0.01 per request

**Recommendation for Phase 2:** Use current method, add factory pattern to swap models later.

## Error Handling

Expected error scenarios:

```python
{
  "status": "error",
  "error": "No transcripts available for this video",
  "youtube_url": "https://youtu.be/VIDEO_ID"
}
```

Errors to handle:
- Invalid YouTube URL
- No captions/transcripts available
- API rate limiting
- Network timeouts

## Logging

All requests/responses logged to console and `app.log`:

```
[2024-04-05 10:30:15] INFO Processing video: https://youtu.be/KyBgxe-rU48
[2024-04-05 10:30:20] DEBUG Extracted 681 words
[2024-04-05 10:30:25] INFO Generated 9 flashcards in 10.2s
```

## Deliverables

- ✓ Working FastAPI server
- ✓ Fully documented endpoints
- ✓ Swagger UI for manual testing
- ✓ Error handling
- ✓ Clear request/response format
- ✓ Ready for frontend integration

## Timeline

**Estimated:** 1-2 hours

## Next Phase: Phase 3

After Phase 2 works:
- Add PostgreSQL/SQLite database
- User authentication (JWT)
- CRUD operations for flashcards
- Subject/topic grouping

See [PHASE3.md](PHASE3.md) (to be created)
