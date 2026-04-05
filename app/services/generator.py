"""
Service for generating flashcard Q&A pairs using extractive + template-based approach.
Combines NLP-based extraction with question templates for better quality Q&A pairs.
Avoids poor zero-shot question generation by using proven extractive patterns.
"""
from typing import List, Dict, Optional
import re
from collections import Counter


class FlashcardGenerator:
    """
    Generate high-quality Q&A pairs from text using extractive methods and templates.
    
    This approach:
    1. Extracts key sentences and noun phrases
    2. Generates questions using proven templates
    3. Pairs questions with relevant answers from text
    
    Better than zero-shot LLM generation because it:
    - Avoids model hallucinations
    - Ensures answers are in the text
    - Creates grammatically correct questions
    """
    
    # Question templates that work well with extracted content
    QUESTION_TEMPLATES = [
        "What is {concept}?",
        "How does {concept} work?",
        "What are the properties of {concept}?",
        "Why is {concept} important?",
        "What is the definition of {concept}?",
        "How can {concept} be used?",
        "What are examples of {concept}?",
        "Describe {concept}.",
        "What happens when {concept} occurs?",
        "What are the characteristics of {concept}?",
    ]
    
    @staticmethod
    def generate_qa_pairs(text: str, 
                          num_pairs: int = 3,
                          **kwargs) -> List[Dict[str, str]]:
        """
        Generate question-answer pairs from text using extractive method.
        
        Args:
            text: Input text to generate Q&A from
            num_pairs: Number of Q&A pairs to generate
            **kwargs: Unused (for API compatibility)
        
        Returns:
            List of dicts with 'question' and 'answer' keys
        """
        # Step 1: Extract key concepts and sentences
        concepts = FlashcardGenerator._extract_key_concepts(text)
        key_sentences = FlashcardGenerator._extract_key_sentences(text)
        
        qa_pairs = []
        
        # Step 2: Generate Q&A pairs from concepts
        for i, concept in enumerate(concepts[:num_pairs]):
            question = FlashcardGenerator._generate_question(concept)
            answer = FlashcardGenerator._find_answer(text, concept)
            
            if answer and len(answer.split()) > 3:  # Ensure answer has substance
                qa_pairs.append({
                    'question': question,
                    'answer': answer
                })
        
        # Step 3: Fill remaining pairs with sentence-based Q&A
        if len(qa_pairs) < num_pairs and key_sentences:
            for sentence in key_sentences[len(qa_pairs):num_pairs]:
                qa_pairs.append({
                    'question': FlashcardGenerator._sentence_to_question(sentence),
                    'answer': sentence[:200]
                })
        
        return qa_pairs[:num_pairs]
    
    @staticmethod
    def _extract_key_concepts(text: str, top_n: int = 5) -> List[str]:
        """
        Extract key noun phrases and concepts from text.
        Uses frequency and filtering to find actual content words.
        
        Args:
            text: Input text
            top_n: Number of top concepts to extract
        
        Returns:
            List of key concepts
        """
        # Comprehensive stop words
        stop_words = {
            'you', 'your', 'i', 'me', 'my', 'we', 'us', 'our', 'they', 'them', 'he', 'she', 'it', 'this', 'that',
            'said', 'say', 'make', 'get', 'go', 'come', 'do', 'does', 'did', 'give', 'take', 'take', 'ask',
            'well', 'way', 'thing', 'fact', 'case', 'kind', 'type', 'example', 'reason', 'what', 'which', 'when',
            'time', 'day', 'year', 'part', 'person', 'people', 'man', 'woman', 'boy', 'girl', 'number',
            'first', 'last', 'next', 'other', 'same', 'just', 'also', 'now', 'then', 'here', 'there', 'break',
            'happen', 'happens', 'happened', 'look', 'find', 'found', 'finding', 'question', 'questions', 'answer',
            'stand', 'stop', 'continues', 'imagine', 'wonder', 'believe', 'think', 'tell', 'means', 'says'
        }
        
        # Extract all words
        all_text = text.lower()
        words = re.findall(r'\b[a-z]{4,}\b', all_text)  # 4+ char words
        
        word_freq = Counter(w for w in words if w not in stop_words)
        
        # Get top concepts - must appear at least 2 times
        concepts = [
            word for word, count in word_freq.most_common(top_n * 2) 
            if count >= 2  # Must appear multiple times
        ]
        
        # Fill with high-value single occurrences if needed
        if len(concepts) < top_n:
            single_occurrence = [
                word for word, count in word_freq.most_common(top_n * 5)
                if count == 1 and len(word) > 5  # Longer words likely more meaningful
            ]
            concepts.extend(single_occurrence)
        
        return concepts[:top_n] if concepts else ['atoms', 'elements', 'properties']
    
    @staticmethod
    def _extract_key_sentences(text: str, top_n: int = 5) -> List[str]:
        """
        Extract key sentences from text.
        Prioritizes sentences with important words and proper length.
        
        Args:
            text: Input text
            top_n: Number of sentences to extract
        
        Returns:
            List of key sentences
        """
        # Simple sentence splitting
        raw_sentences = text.split('.')
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        # Score sentences based on importance indicators
        scored_sentences = []
        
        for sentence in sentences:
            score = 0
            word_count = len(sentence.split())
            
            # Length score (prefer medium length sentences)
            if 8 <= word_count <= 40:
                score += 3
            elif 5 <= word_count <= 60:
                score += 1
            
            # Definition/explanation indicators
            definition_words = ['is', 'are', 'means', 'refers to', 'defined as', 'called', 'named', 'known as', 'consists', 'contains', 'example', 'reason', 'because', 'therefore']
            for word in definition_words:
                if word in sentence.lower():
                    score += 2
            
            # Capital letter indicates important concepts
            capital_count = sum(1 for c in sentence if c.isupper())
            score += min(capital_count, 2)  # Max +2 for capitals
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top N
        best_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
        return [s[0] for s in best_sentences[:top_n]]
    
    @staticmethod
    def _generate_question(concept: str) -> str:
        """
        Generate a question from a concept using templates.
        
        Args:
            concept: Key concept/phrase
        
        Returns:
            Generated question
        """
        import random
        
        # Clean concept
        concept = concept.strip().lower()
        
        # Select template
        template = random.choice(FlashcardGenerator.QUESTION_TEMPLATES)
        
        # Fill template
        try:
            question = template.format(concept=concept)
        except:
            question = f"What is {concept}?"
        
        return question
    
    @staticmethod
    def _find_answer(text: str, concept: str, max_length: int = 200) -> str:
        """
        Find the most relevant sentence containing the concept as an answer.
        Prioritizes definition sentences and filters out opening/closing statements.
        
        Args:
            text: Full text
            concept: Key concept to find answer for
            max_length: Maximum answer length
        
        Returns:
            Answer text
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return ""
        
        # Filter out intro/outro sentences (too short or just greetings)
        filtered_sentences = [
            s for s in sentences 
            if len(s.split()) > 5  # Must have substance
            and not any(phrase in s.lower() for phrase in [
                'good morning', 'welcome', 'thank you', 'thanks for watching',
                'subscribe', 'like', 'comment', 'see you', 'goodbye', 'next video',
                'hi everyone', 'hello everyone', 'welcome back', 'thanks guys'
            ])
        ]
        
        if not filtered_sentences:
            filtered_sentences = sentences
        
        # Find sentences containing concept keywords
        concept_words = set(word.lower() for word in concept.split() if len(word) > 2)
        
        best_sentence = ""
        best_score = 0
        
        for i, sentence in enumerate(filtered_sentences):
            sentence_lower = sentence.lower()
            score = 0
            
            # Score based on keyword matches (all keywords > partial keywords)
            matching_words = sum(1 for word in concept_words if word in sentence_lower)
            if matching_words > 0:
                score = matching_words * 3
            else:
                continue  # Skip if no keyword match
            
            # Boost heavily for definition/explanation patterns
            definition_patterns = [
                'is', 'are', 'means', 'refers to', 'defined as', 'called', 
                'named', 'involves', 'includes', 'consists of', 'example of'
            ]
            if any(pattern in sentence_lower for pattern in definition_patterns):
                score += 10
            
            # Slight boost for earlier sentences (usually more general/educational)
            score += max(0, 2 - (i / len(filtered_sentences)))
            
            # Penalize very long sentences (less likely to be clear answers)
            if len(sentence.split()) > 40:
                score -= 2
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        if not best_sentence and filtered_sentences:
            best_sentence = filtered_sentences[0]
        
        return best_sentence.strip()[:max_length] if best_sentence else ""
    
    @staticmethod
    def _sentence_to_question(sentence: str) -> str:
        """
        Convert a statement sentence into a question.
        
        Args:
            sentence: Statement sentence
        
        Returns:
            Question
        """
        sentence = sentence.strip()
        
        # Simple transformations for common patterns
        patterns = [
            (r'^([A-Z][a-z]+)\s+(\w+s)\s+', r'What \2 '),  # "Atoms have" -> "What have atoms?"
            (r'^(.+)\s+is\s+(a|an|the|one|\.)', r'What is \2'),  # "This is a..." -> "What is a..."
            (r'^(.+)\s+are\s+(.+)$', r'What are \2?'),  # "These are..." -> "What are...?"
        ]
        
        for pattern, replacement in patterns:
            if re.match(pattern, sentence):
                question = re.sub(pattern, replacement, sentence)
                if not question.endswith('?'):
                    question += '?'
                return question
        
        # Fallback: just add question mark
        if not sentence.endswith('?'):
            sentence += '?'
        
        return sentence
    
    @classmethod
    def unload_model(cls):
        """
        Placeholder for API compatibility.
        Extractive method doesn't load any models.
        """
        pass


# Keep T5GeneratorService for backward compatibility
class T5GeneratorService(FlashcardGenerator):
    """
    Backward compatibility wrapper.
    Uses FlashcardGenerator (extractive method) instead of T5.
    """
    pass
