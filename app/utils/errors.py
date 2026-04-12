"""Custom exceptions for the flashcard generator."""


class FlashcardGeneratorError(Exception):
    """Base exception for all pipeline errors."""
    pass


class InvalidYouTubeURLError(FlashcardGeneratorError):
    """Raised when URL is not valid YouTube URL."""
    pass


class TranscriptExtractionError(FlashcardGeneratorError):
    """Raised when transcript cannot be extracted from video."""
    pass


class NoTranscriptAvailableError(FlashcardGeneratorError):
    """Raised when video has no available transcript."""
    pass


class ModelError(FlashcardGeneratorError):
    """Raised when the LLM generator fails."""
    pass
