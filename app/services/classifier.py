"""Question classifier placeholder for local model usage."""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class QuestionClassifier:
    """
    Classify flashcard questions across multiple dimensions:
    - Difficulty: easy, medium, hard
    - Type: identification, definition, explanation, comparison, computation
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
            return self._basic_difficulty(question)
        
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
            return self._basic_question_type(question)
        
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
        if self._is_english_vocab(question):
            return 'english'

        # Broad-topic heuristic
        domains = {
            'english': ['synonym', 'antonym', 'vocabulary', 'definition', 'meaning'],
            'math': ['number', 'equation', 'function', 'algebra', 'geometry', 'theorem', 'solve', 'calculate'],
            'science': ['cell', 'organism', 'dna', 'protein', 'photosynthesis', 'evolution', 'atom', 'molecule', 'gravity', 'energy', 'planet', 'earth', 'sun', 'core', 'mantle', 'crust', 'physics', 'biology', 'chemistry'],
            'technology': ['computer', 'software', 'algorithm', 'data', 'system', 'network', 'cpu', 'gpu', 'memory'],
            'history': ['war', 'revolution', 'empire', 'dynasty', 'century', 'period'],
            'geography': ['continent', 'ocean', 'mountain', 'river', 'climate', 'latitude', 'longitude'],
            'health': ['disease', 'health', 'medicine', 'virus', 'bacteria', 'anatomy'],
            'business': ['market', 'economy', 'profit', 'revenue', 'finance', 'trade'],
            'arts': ['art', 'music', 'painting', 'sculpture', 'dance', 'design'],
        }
        
        combined_text = (question + ' ' + context).lower()
        
        for topic, keywords in domains.items():
            if any(kw in combined_text for kw in keywords):
                return topic
        
        return 'general'

    def _is_english_vocab(self, question: str) -> bool:
        text = question.lower()
        triggers = [
            'synonym',
            'synonymous',
            'antonym',
            'means the same',
            'another term',
            'word means',
            'word that means',
            'term for',
            'vocabulary'
        ]
        return any(trigger in text for trigger in triggers)

    def _basic_question_type(self, question: str) -> str:
        text = question.lower().strip()

        if any(token in text for token in ['calculate', 'compute', 'solve', 'derive']):
            return 'computation'
        if any(token in text for token in ['compare', 'difference', 'different', 'contrast', 'versus']):
            return 'comparison'
        if text.startswith(('who', 'when', 'where', 'which')):
            return 'identification'
        if text.startswith(('what is', 'what are', 'define', 'identify')):
            return 'definition'
        if 'why' in text or text.startswith('how'):
            return 'explanation'

        return 'definition'

    def _basic_difficulty(self, question: str) -> str:
        text = question.lower()

        hard_markers = ['compare', 'difference', 'explain', 'why', 'how', 'analyze']
        easy_markers = ['what is', 'what are', 'define', 'identify', 'name']

        if any(marker in text for marker in hard_markers):
            return 'hard'
        if any(marker in text for marker in easy_markers):
            return 'easy'

        return 'medium'
    
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
