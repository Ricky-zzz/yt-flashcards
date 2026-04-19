"""Generate flashcards endpoint."""
import csv
import logging
import math
import os
import re
import time
from pathlib import Path

from fastapi import APIRouter
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.schemas import (
    GenerateRequest,
    GenerateResponse,
    GenerateResponseData,
    FlashcardObject,
    GenerateMetadata,
    ErrorDetail,
)
from app.services.transcript import extract_transcript, get_video_title
from app.services.cleaner import clean_text
from app.services.chunker import smart_chunk
from app.services.generator import FlashcardGenerator
from app.services.classifier import QuestionClassifier
from app.utils.errors import (
    InvalidYouTubeURLError,
    TranscriptExtractionError,
    NoTranscriptAvailableError,
    ModelError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["generate"])


def get_generator() -> FlashcardGenerator:
    """Lazy load generator on first use."""
    return FlashcardGenerator()


def get_classifier() -> QuestionClassifier:
    """Lazy load classifier on first use."""
    return QuestionClassifier()


def validate_youtube_url(url: str) -> bool:
    """Validate YouTube URL format."""
    return "youtube.com" in url or "youtu.be" in url


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def estimate_target_cards(word_count: int, density: float) -> int:
    words_per_minute = 130
    minutes = max(1.0, word_count / words_per_minute)

    if density < 0.25:
        rate = 1.2
    elif density < 0.4:
        rate = 1.8
    else:
        rate = 2.4

    target = round(minutes * rate)
    return clamp(target, 8, 120)


def estimate_density(text: str) -> float:
    tokens = [token for token in re.findall(r"[a-zA-Z']+", text.lower()) if token]
    if not tokens:
        return 0.0
    unique_ratio = len(set(tokens)) / len(tokens)
    return clamp(unique_ratio, 0, 1)


def append_training_data(flashcards: list[FlashcardObject]) -> None:
    output_path = Path(__file__).resolve().parents[2] / "training_data.csv"
    file_exists = output_path.exists()

    with output_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["question", "answer", "difficulty", "question_type", "topic", "chunk_index"],
        )
        if not file_exists:
            writer.writeheader()

        for card in flashcards:
            writer.writerow(
                {
                    "question": card.question,
                    "answer": card.answer,
                    "difficulty": card.difficulty or "medium",
                    "question_type": card.question_type or "definition",
                    "topic": card.topic or "general",
                    "chunk_index": card.chunk_index,
                }
            )


@router.post("/generate", response_model=GenerateResponse)
async def generate_flashcards(request: GenerateRequest) -> GenerateResponse:
    """Generate flashcards from a YouTube video."""
    start_time = time.time()

    generator = get_generator()
    classifier = get_classifier()
    classification_skipped = classifier.classifier is None
    delay_seconds = float(os.getenv("CHUNK_DELAY_SECONDS", "0"))
    max_pairs_per_chunk = 6
    max_chunks_limit = 20

    try:
        if request.transcript_text:
            transcript_text = request.transcript_text.strip()
            if not transcript_text:
                raise NoTranscriptAvailableError("Pasted transcript is empty")
            video_title = "Pasted Transcript"
            logger.info(f"Using pasted transcript: {len(transcript_text)} characters")
        else:
            if not request.youtube_url or not validate_youtube_url(request.youtube_url):
                raise InvalidYouTubeURLError(
                    "Invalid YouTube URL. Must contain 'youtube.com' or 'youtu.be'"
                )

            logger.info(f"Generating flashcards for: {request.youtube_url}")

            try:
                transcript_text = extract_transcript(request.youtube_url)
                if not transcript_text or len(transcript_text.strip()) == 0:
                    raise NoTranscriptAvailableError("Video has no available transcript")
                logger.info(f"Extracted {len(transcript_text)} characters from transcript")
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                raise NoTranscriptAvailableError(
                    f"Video has no available transcript: {str(e)}"
                )
            except Exception as e:
                raise TranscriptExtractionError(f"Failed to extract transcript: {str(e)}")

            try:
                video_title = get_video_title(request.youtube_url)
            except Exception as e:
                logger.warning(f"Could not extract video title: {e}")
                video_title = "Untitled Video"

        cleaned_text = clean_text(transcript_text)
        logger.info(f"Cleaned text: {len(cleaned_text)} characters")

        chunks = smart_chunk(cleaned_text, chunk_size=400, overlap=50)
        total_chunks = len(chunks)

        word_count = len(cleaned_text.split())
        density = estimate_density(cleaned_text)
        target_cards = estimate_target_cards(word_count, density)

        if request.max_chunks:
            planned_chunks = min(request.max_chunks, total_chunks, max_chunks_limit)
        else:
            planned_chunks = min(
                total_chunks,
                max_chunks_limit,
                max(1, math.ceil(target_cards / max_pairs_per_chunk))
            )

        if request.num_pairs:
            pairs_per_chunk = clamp(request.num_pairs, 1, max_pairs_per_chunk)
        else:
            pairs_per_chunk = clamp(
                math.ceil(target_cards / max(1, planned_chunks)),
                1,
                max_pairs_per_chunk
            )

        chunks = chunks[:planned_chunks]

        logger.info(
            "Created %s chunks, processing %s (target cards=%s, pairs/chunk=%s)",
            total_chunks,
            planned_chunks,
            target_cards,
            pairs_per_chunk,
        )

        all_flashcards = []

        for chunk_idx, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {chunk_idx + 1}/{len(chunks)}")

            try:
                qa_pairs = generator.generate_qa_pairs(
                    chunk,
                    num_pairs=pairs_per_chunk
                )

                for qa in qa_pairs:
                    classification = classifier.classify_qa_pair(
                        qa.get("question", ""),
                        qa.get("answer", ""),
                        context=chunk
                    )

                    flashcard = FlashcardObject(
                        question=qa.get("question", ""),
                        answer=qa.get("answer", ""),
                        chunk_index=chunk_idx,
                        difficulty=classification.get("difficulty", "medium"),
                        question_type=classification.get("question_type", "definition"),
                        topic=classification.get("topic", "general")
                    )
                    all_flashcards.append(flashcard)

            except ModelError as e:
                logger.error(f"Model error on chunk {chunk_idx}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error on chunk {chunk_idx}: {e}")
                continue

            if delay_seconds > 0 and chunk_idx < len(chunks) - 1:
                time.sleep(delay_seconds)

        if not all_flashcards:
            raise ModelError("Failed to generate any flashcards from the video")

        try:
            append_training_data(all_flashcards)
        except Exception as e:
            logger.warning("Failed to append training data: %s", e)

        processing_time = time.time() - start_time

        metadata = GenerateMetadata(
            video_title=video_title,
            total_cards=len(all_flashcards),
            processing_time=round(processing_time, 2),
            chunks_processed=len(chunks),
            classification_skipped=classification_skipped,
            model_used="gemini-1.5-flash-latest"
        )

        response_data = GenerateResponseData(
            flashcards=all_flashcards,
            metadata=metadata
        )

        logger.info(
            f"Successfully generated {len(all_flashcards)} flashcards in {processing_time:.2f}s"
        )

        return GenerateResponse(
            success=True,
            data=response_data,
            message="Flashcards generated successfully",
            error=None
        )

    except InvalidYouTubeURLError as e:
        logger.error(f"Invalid YouTube URL: {e}")
        return GenerateResponse(
            success=False,
            data=None,
            message=str(e),
            error=ErrorDetail(type="InvalidYouTubeURLError", details=str(e))
        )
    except NoTranscriptAvailableError as e:
        logger.error(f"No transcript available: {e}")
        return GenerateResponse(
            success=False,
            data=None,
            message=str(e),
            error=ErrorDetail(type="NoTranscriptAvailableError", details=str(e))
        )
    except TranscriptExtractionError as e:
        logger.error(f"Transcript extraction failed: {e}")
        return GenerateResponse(
            success=False,
            data=None,
            message=str(e),
            error=ErrorDetail(type="TranscriptExtractionError", details=str(e))
        )
    except ModelError as e:
        logger.error(f"Model error: {e}")
        return GenerateResponse(
            success=False,
            data=None,
            message=str(e),
            error=ErrorDetail(type="ModelError", details=str(e))
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return GenerateResponse(
            success=False,
            data=None,
            message="Internal server error",
            error=ErrorDetail(type="UnknownError", details=str(e))
        )
