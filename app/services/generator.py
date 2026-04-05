"""
Flashcard Q&A generator using T5 model.
Extracts key concepts and generates question-answer pairs from text chunks.
"""
import logging
from typing import List, Dict, Optional

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

logger = logging.getLogger(__name__)


class T5GeneratorService:
    """
    Generate flashcard Q&A pairs using T5 model.
    
    T5 is a text-to-text transformer that can be prompted to generate
    questions and answers from transcript chunks.
    """
    
    _model = None
    _tokenizer = None
    _device = None
    
    @classmethod
    def load_model(cls, model_name: str = 't5-small'):
        """Load T5 model and tokenizer (cached for reuse)."""
        if cls._model is None:
            cls._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Loading {model_name} onto {cls._device}...")
            cls._tokenizer = T5Tokenizer.from_pretrained(model_name)
            cls._model = T5ForConditionalGeneration.from_pretrained(model_name)
            cls._model.to(cls._device)
        return cls._model, cls._tokenizer, cls._device
    
    @classmethod
    def generate_qa_pairs(cls,
                         text: str,
                         num_pairs: int = 3,
                         model_name: str = 't5-small') -> List[Dict[str, str]]:
        """
        Generate Q&A pairs from a text chunk using T5.
        
        Args:
            text: Transcript chunk
            num_pairs: Target number of Q&A pairs
            model_name: T5 model to use (t5-small, t5-base, etc.)
        
        Returns:
            List of {"question": ..., "answer": ...} dicts
        """
        model, tokenizer, device = cls.load_model(model_name)
        
        # Truncate if too long (T5 input limit)
        max_input_length = 512
        words = text.split()
        if len(words) > max_input_length:
            text = ' '.join(words[:max_input_length])
        
        # Prepare prompt: ask T5 to generate questions
        # Format: "generate questions: <text>"
        prompt = f"generate questions: {text}"
        
        try:
            # Encode and generate
            inputs = tokenizer.encode(prompt, return_tensors='pt', max_length=512, truncation=True)
            inputs = inputs.to(device)
            
            outputs = model.generate(
                inputs,
                max_length=150,
                num_beams=2,
                temperature=0.9,
                early_stopping=True
            )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse output into Q&A pairs (simple heuristic)
            # T5 might generate "question 1: ... answer 1: ..." pattern
            pairs = []
            lines = generated_text.split('.')
            
            # Create placeholder Q&A pairs from generated content
            for i, line in enumerate(lines[:num_pairs]):
                if line.strip():
                    pairs.append({
                        'question': f"Concept {i+1}: {line.strip()[:100]}?",
                        'answer': f"Generated from source text."
                    })
            
            return pairs if pairs else _generate_fallback_pairs(text, num_pairs)
        
        except Exception as e:
            logger.error(f"T5 generation failed: {e}")
            return _generate_fallback_pairs(text, num_pairs)
    
    @classmethod
    def unload_model(cls):
        """Clear cached model to free memory."""
        cls._model = None
        cls._tokenizer = None


def _generate_fallback_pairs(text: str, num_pairs: int) -> List[Dict[str, str]]:
    """
    Generate simple Q&A pairs as fallback when T5 fails.
    Uses keyword extraction from text.
    """
    import re
    
    sentences = text.split('. ')
    pairs = []
    
    # Extract key nouns/concepts from sentences
    for i, sentence in enumerate(sentences[:num_pairs]):
        if len(sentence.split()) > 4:
            # Simple heuristic: first noun/concept as question basis
            words = sentence.strip().split()
            concept = ' '.join(words[:3])
            
            pairs.append({
                'question': f"What is {concept}?",
                'answer': sentence.strip()[:150]
            })
    
    return pairs