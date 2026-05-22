# YouTube Transcript to Flashcard Generator

Convert YouTube videos into study flashcards using AI-powered transcript extraction and question-answer pair generation.

## Overview

A full-stack application that automates flashcard creation from YouTube videos. The backend pipeline extracts transcripts, cleans noise, chunks content semantically, and generates Q&A pairs using machine learning. A Vue.js frontend provides an intuitive interface for users to generate, organize, and review flashcards. Built with FastAPI, SQLAlchemy ORM, and modern AI models.

## What I Learned

- **API Development**: Built RESTful APIs with FastAPI, designed request/response schemas with Pydantic, and structured endpoints for scalability
- **Object-Oriented Design**: Organized code into service classes (transcript extraction, text cleaning, chunking, Q&A generation) with single responsibility principles
- **Database Design & ORM**: Implemented SQLAlchemy models for users, decks, flashcards, and review sessions with migrations using Alembic
- **Text Processing**: Applied NLP techniques including tokenization, semantic chunking with word-count-based overlap, and noise removal from auto-generated captions
- **Machine Learning Integration**: Integrated Hugging Face transformers (T5 model) for Q&A generation with CPU/GPU fallback handling
- **Authentication & Security**: Implemented JWT-based authentication, password hashing, and secure environment variable management
- **Frontend Architecture**: Built a Vue 3 component-based frontend with service layer abstraction, state management patterns, and API integration
- **Full-Stack Workflow**: Managed the complete development lifecycle from data pipeline testing to API endpoints to user-facing features


## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Node.js 18+ (for the Vue frontend)

### Setup (Windows/Mac/Linux)

1. **Clone the repository**
```bash
git clone https://github.com/Ricky-zzz/yt-flashcards.git
cd yt_transcript
```

2. **Create Virtual Environment** (IMPORTANT)
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install fastapi uvicorn youtube-transcript-api transformers torch nltk yt-dlp browser-cookie3
```

4. **Verify Installation**
```bash
python -c "import fastapi; import youtube_transcript_api; import transformers; print('✓ All dependencies installed')"
```

5. **Set environment variables**
```bash
# Create app/.env (see app/.env.example if provided)
# Required:
# GEMINI_API_KEY=your_key
# GROQ_API_KEY=your_key (optional fallback)
# HF_TOKEN=your_hf_token (optional)
```

6. **Run the API server**
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

7. **Install and run the frontend**
```bash
cd frontend
npm install
npm run dev
```

Open the UI at http://localhost:5173

## Project Structure

```
yt_transcript/
├── app/
│   ├── services/
│   │   ├── transcript.py       # YouTube transcript extraction
│   │   ├── cleaner.py          # Text preprocessing
│   │   ├── chunker.py          # Semantic text chunking
│   │   └── generator.py        # Q&A pair generation
│   ├── routes/                 # API endpoints (Phase 2)
│   ├── schemas/                # Pydantic models (Phase 2)
│   └── main.py                 # FastAPI app (Phase 2)
├── tests/
│   └── pipeline_test.py         # End-to-end pipeline testing
├── ml/                         # Model storage (future)
├── requirements.txt            # Dependencies list (future)
└── README.md                   # This file
```

## Phase 1: Pipeline (COMPLETE ✓)

### Current Functionality

The pipeline performs 4 steps:

1. **Extraction** - Downloads YouTube video captions
2. **Cleaning** - Removes artifacts, normalizes text
3. **Chunking** - Splits into semantic chunks (~300 words)
4. **Generation** - Creates Q&A pairs from chunks

### Testing the Pipeline

```bash
# Basic test (2-minute transcript)
python tests/pipeline_test.py "https://youtu.be/VIDEO_ID"

# With custom parameters
python tests/pipeline_test.py "https://youtu.be/cs3B0zcRJco" \
  --chunk_size 600 \
  --num_pairs 3 \
  --max_chunks 5
```

**Examples:**
```bash
# Khan Academy 
python tests/pipeline_test.py "https://youtu.be/KyBgxe-rU48"

# Output
python tests/pipeline_test.py "https://youtu.be/cs3B0zcRJco" --max_chunks 3
```

**Output:** `pipeline_results.json` with extracted flashcards
by word count (~600 words/chunk with overlap)
-  Generates basic Q&A pairs using T5 model
  - Simple keyword extraction + template approach for initial release
  - Will be upgraded to Mistral/ChatGPT in Phase 2

### How Chunking Works

YouTube auto-captions have **zero punctuation**, so we chunk by **word count** not sentences:
- **Default:** 600 words per chunk
- **Overlap:** 75 words between chunks (context preservation)
- **Minimum:** 80 words to generate cards from

Example: 8,500-word transcript → ~12-15 chunks → 30-45 flashcards
- Chunks text semantically
  - Supports: `youtu.be/ID`, `youtube.com/watch?v=ID`, `youtube.com/shorts/ID`
  - Returns: Plain text transcripts or timestamped snippets
  
- **cleaner.py** - Removes noise from auto-captions
  - Removes `[Music]`, `[Applause]` tags
  - Removes fillers (um, uh, like, basically)
  - Collapses whitespace
  
- **chunker.py** - Splits text by word count (not sentences)
  - 600 words/chunk default (configurable)
  - 75-word overlap for context (configurable)
  - Validates minimum chunk size
  
- **generator.py** - T5 model for Q&A generation
  - Uses transformers library
  - CPU- and GPU-friendly
  - Fallback keyword extraction if model unavailable

## Architecture

### Services

- **transcript.py** - Fetches YouTube captions via youtube-transcript-api
- **cleaner.py** - Removes noise, normalizes whitespace
- **chunker.py** - Splits text by sentences while respecting word count targets
- **generator.py** - Extracts concepts, generates questions, finds answers

### Data Flow

```
YouTube URL
    ↓
[Extract Transcript] → 8000 words
    ↓
[Clean Text] → Normalized 8000 words
    ↓
[Chunk] → 3 chunks (300 words each)
    ↓
[Generate Q&A] → 9 flashcards (3 per chunk)
    ↓
JSON Output
```

## License

MIT
