"""Question classifier placeholder for local model usage."""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class QuestionClassifier:
    """
    Classify flashcard questions across multiple dimensions:
    - Difficulty: easy, medium, hard
    - Type: definition, explanation, application, synthesis, analysis
    - Topic: extracted from context or general
    """
    
    def __init__(self):
        """Disable classifier until a local model is added."""
        self.classifier = None
        logger.info("Classifier disabled; using default labels until a local model is added.")
    
    def classify_difficulty(self, question: str) -> str:
        """
        Classify question difficulty.
        
        Args:
            question: Question text
        
        Returns:
            One of: 'easy', 'medium', 'hard'
        """
        if not self.classifier:
            return 'medium'  # Default if classifier unavailable
        
        try:
            labels = ['easy', 'medium', 'hard']
            result = self.classifier(question, labels, multi_class=False)
            return result['labels'][0]
        except Exception as e:
            logger.warning(f"Difficulty classification failed: {e}")
            return 'medium'
    
    def classify_question_type(self, question: str) -> str:
        """
        Classify question type (Bloom's taxonomy).
        
        Args:
            question: Question text
        
        Returns:
            One of: 'definition', 'explanation', 'application', 'synthesis', 'analysis'
        """
        if not self.classifier:
            return 'definition'  # Default if classifier unavailable
        
        try:
            labels = [
                'definition',      # What is X? Define X
                'explanation',     # Why? How? What causes?
                'application',     # Apply, use, implement
                'analysis',        # Compare, contrast, break down
                'synthesis'        # Create, combine, imagine
            ]
            result = self.classifier(question, labels, multi_class=False)
            return result['labels'][0]
        except Exception as e:
            logger.warning(f"Question type classification failed: {e}")
            return 'definition'
    
    def extract_topic(self, question: str, context: str = '') -> str:
        """
        Attempt to extract topic from question and context.
        Falls back to 'general' if unclear.
        
        Args:
            question: Question text
            context: Additional context (chunk text, etc.)
        
        Returns:
            Topic name or 'general'
        """
        # Simple heuristic: look for common STEM domains in question/context
        domains = {
            'biology': ['cell', 'organism', 'dna', 'protein', 'photosynthesis', 'evolution'],
            'chemistry': ['atom', 'molecule', 'element', 'reaction', 'bond', 'compound'],
            'physics': ['force', 'energy', 'motion', 'wave', 'gravity', 'velocity'],
            'math': ['number', 'equation', 'function', 'algebra', 'geometry', 'theorem'],
            'history': ['war', 'revolution', 'empire', 'dynasty', 'century', 'period'],
            'literature': ['author', 'novel', 'poem', 'character', 'theme', 'plot'],
            'technology': ['computer', 'software', 'algorithm', 'data', 'system', 'network'],
        }
        
        combined_text = (question + ' ' + context).lower()
        
        for topic, keywords in domains.items():
            if any(kw in combined_text for kw in keywords):
                return topic
        
        return 'general'
    
    def classify_qa_pair(self, question: str, answer: str, context: str = '') -> Dict[str, str]:
        """
        Classify a Q&A pair across all dimensions.
        
        Args:
            question: Question text
            answer: Answer text
            context: Optional context (chunk, etc.)
        
        Returns:
            Dict with keys: difficulty, question_type, topic
        """
        return {
            'difficulty': self.classify_difficulty(question),
            'question_type': self.classify_question_type(question),
            'topic': self.extract_topic(question, context)
        }
    
    def classify_flashcards(self,
                           flashcards: List[Dict[str, str]],
                           context: str = '') -> List[Dict[str, str]]:
        """
        Classify a batch of flashcards.
        
        Args:
            flashcards: List of {"question": ..., "answer": ...} dicts
            context: Optional shared context for all cards
        
        Returns:
            List of flashcards with added classification fields
        """
        classified = []
        
        for card in flashcards:
            question = card.get('question', '')
            answer = card.get('answer', '')
            chunk_index = card.get('chunk_index', 0)
            
            # Classify this card
            labels = self.classify_qa_pair(question, answer, context)
            
            # Add to output
            classified_card = {
                'question': question,
                'answer': answer,
                'chunk_index': chunk_index,
                'difficulty': labels['difficulty'],
                'question_type': labels['question_type'],
                'topic': labels['topic']
            }
            classified.append(classified_card)
        
        return classified
