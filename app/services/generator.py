"""
Flashcard Q&A generator using Google Gemini Flash API.
Generates high-quality question-answer pairs from transcript chunks.
"""
import json
import logging
import os
import time
from typing import List, Dict, Optional

import google.generativeai as genai

try:
    from groq import Groq
except Exception:
    Groq = None

logger = logging.getLogger(__name__)


class FlashcardGenerator:
    """
    Generate flashcard Q&A pairs using Google Gemini Flash.
    
    Gemini Flash understands raw unpunctuated text natively and generates
    high-quality questions and answers without additional training.
    
    Free tier: 15 requests/minute, 1M tokens/day (sufficient for demos).
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "gemini-flash-latest",
                 provider: Optional[str] = None,
                 fallback_provider: Optional[str] = None):
        """
        Initialize Gemini Flash client.
        
        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY env var)
            model: Model to use (default: gemini-flash-latest)
        """
        self.provider = (provider or os.getenv("LLM_PROVIDER") or "gemini").lower()
        self.fallback_provider = (fallback_provider or os.getenv("LLM_FALLBACK_PROVIDER") or "groq").lower()

        self.gemini_api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.gemini_model_name = model or os.getenv("GEMINI_MODEL") or "gemini-flash-latest"
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model_name = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"

        self.gemini_model = None
        self.groq_client = None

        if self.provider == "gemini" or self.fallback_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY not set. Get free key at "
                    "https://aistudio.google.com/apikey and set as env variable."
                )
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(self.gemini_model_name)

        if self.provider == "groq" or self.fallback_provider == "groq":
            if not self.groq_api_key:
                logger.warning("GROQ_API_KEY not set; Groq fallback disabled.")
            elif Groq is None:
                raise ValueError("Groq SDK not installed. Add 'groq' to requirements and install it.")
            else:
                self.groq_client = Groq(api_key=self.groq_api_key)
    
    def generate_qa_pairs(self,
                         text: str,
                         num_pairs: int = 3,
                         retries: int = 2) -> List[Dict[str, str]]:
        """
        Generate Q&A pairs from a text chunk using Gemini.
        
        Args:
            text: Transcript chunk (any length, will be truncated if needed)
            num_pairs: Target number of Q&A pairs (default: 3)
            retries: Retry attempts on parse failure (default: 2)
        
        Returns:
            List of {"question": str, "answer": str} dicts
        
        Raises:
            Exception: If Gemini API fails after retries
        """
        # Truncate to ~2000 chars to stay in free tier token limits
        if len(text) > 2000:
            text = text[:2000]
        
        prompt = f"""From this transcript excerpt, generate exactly {num_pairs} high-quality flashcard Q&A pairs.

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "pairs": [
    {{
      "question": "Clear, concise question",
      "answer": "Detailed, accurate answer from the text"
    }}
  ]
}}

Transcript:
{text}

Generate only the JSON response, nothing else:"""
        
        for attempt in range(retries):
            try:
                response_text = self._generate_with_provider(prompt, self.provider)

                pairs = self._parse_pairs(response_text, num_pairs)
                if pairs:
                    return pairs

                if attempt < retries - 1:
                    logger.warning(f"Parse failed on attempt {attempt + 1}, retrying...")

            except Exception as e:
                # If rate-limited, attempt fallback once before retrying
                if self._is_rate_limit_error(e) and self._fallback_ready():
                    logger.warning("Rate limit hit; switching to fallback provider.")
                    try:
                        response_text = self._generate_with_provider(prompt, self.fallback_provider)
                        pairs = self._parse_pairs(response_text, num_pairs)
                        if pairs:
                            return pairs
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider failed: {fallback_error}")

                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise
        
        return []

    def _parse_pairs(self, response_text: str, num_pairs: int) -> List[Dict[str, str]]:
        try:
            data = json.loads(response_text)
            pairs = data.get('pairs', [])
            if pairs:
                return pairs[:num_pairs]
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0]
            else:
                json_str = response_text

            data = json.loads(json_str)
            pairs = data.get('pairs', [])
            if pairs:
                return pairs[:num_pairs]

        return []

    def _generate_with_provider(self, prompt: str, provider: str) -> str:
        if provider == "gemini":
            if not self.gemini_model:
                raise ValueError("Gemini model not configured.")
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                # Log full error details to help diagnose quota/enablement issues.
                logger.error("Gemini generation failed: %s", e, exc_info=True)
                raise

        if provider == "groq":
            if not self.groq_client:
                raise ValueError("Groq client not configured.")
            response = self.groq_client.chat.completions.create(
                model=self.groq_model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        raise ValueError(f"Unsupported provider: {provider}")

    def _is_rate_limit_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "429" in message or "rate limit" in message or "quota" in message

    def _fallback_ready(self) -> bool:
        return self.fallback_provider in {"gemini", "groq"} and (
            (self.fallback_provider == "gemini" and self.gemini_model) or
            (self.fallback_provider == "groq" and self.groq_client)
        )
    
    def generate_from_chunks(self,
                            chunks: List[str],
                            cards_per_chunk: int = 3) -> List[Dict[str, str]]:
        """
        Generate flashcards from a list of text chunks.
        Respects Gemini free tier rate limits (15 req/min = 4 sec sleep).
        
        Args:
            chunks: List of text chunks
            cards_per_chunk: Flashcards to generate per chunk (default: 3)
        
        Returns:
            List of all generated flashcards
        """
        all_cards = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)}...")
            try:
                cards = self.generate_qa_pairs(chunk, num_pairs=cards_per_chunk)
                # Add chunk index to each card
                for card in cards:
                    card['chunk_index'] = i
                all_cards.extend(cards)
            except Exception as e:
                logger.error(f"Failed to generate cards for chunk {i}: {e}")
            
            # Rate limiting: 4 second sleep between requests (15 req/min limit)
            if i < len(chunks) - 1:
                time.sleep(4)
        
        return all_cards


# Backward compatibility alias
T5GeneratorService = FlashcardGenerator