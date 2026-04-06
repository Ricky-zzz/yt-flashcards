"""
Phase 1: Complete pipeline test - Extract → Clean → Chunk → Generate → Classify.
Uses Gemini Flash for Q&A generation and DistilBERT for classification.
Saves results to JSON and collects training data in CSV format.

Usage:
    python tests/pipeline_test.py <youtube_url> [--num-pairs N] [--max-chunks N]

Example:
    python tests/pipeline_test.py https://youtu.be/dQw4w9WgXcQ --num-pairs 3 --max-chunks 3

Note: Requires GEMINI_API_KEY environment variable set.
Get free key at https://aistudio.google.com/apikey
"""
import sys
import json
import csv
import logging
import time
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv(Path(__file__).parent.parent / 'app' / '.env')
load_dotenv(Path(__file__).parent.parent / '.env')

# Add the parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.transcript import get_transcript
from app.services.cleaner import preprocess_for_chunking
from app.services.chunker import smart_chunk
from app.services.generator import FlashcardGenerator
from app.services.classifier import QuestionClassifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pipeline(youtube_url: str,
                  num_pairs: int = 3,
                  chunk_size: int = 600,
                  max_chunks: int = 3) -> dict:
    """
    Run complete pipeline: Extract → Clean → Chunk → Generate → Classify.

    Args:
        youtube_url: YouTube video URL or ID
        num_pairs: Q&A pairs per chunk (default: 3)
        chunk_size: Words per chunk (default: 600, tuned for Gemini)
        max_chunks: Maximum chunks to process (default: 3, for testing)

    Returns:
        Dict with results, metadata, and classified flashcards
    """
    results = {
        'status': 'in_progress',
        'steps': {},
        'video_url': youtube_url,
        'flashcards': [],
        'errors': [],
        'timing': {}
    }

    try:
        # Step 1: Extract transcript
        print("Step 1: Extracting transcript...")
        start = time.time()
        transcript = get_transcript(youtube_url)
        word_count = len(transcript.split())
        results['steps']['extraction'] = {
            'status': 'success',
            'word_count': word_count
        }
        results['timing']['extraction'] = time.time() - start
        print(f"✓ Extracted {word_count} words in {results['timing']['extraction']:.1f}s")

        # Step 2: Clean text
        print("\nStep 2: Cleaning text...")
        start = time.time()
        cleaned_text = preprocess_for_chunking(transcript)
        cleaned_word_count = len(cleaned_text.split())
        results['steps']['cleaning'] = {
            'status': 'success',
            'word_count': cleaned_word_count
        }
        results['timing']['cleaning'] = time.time() - start
        print(f"✓ Cleaned text: {cleaned_word_count} words in {results['timing']['cleaning']:.1f}s")

        # Step 3: Chunk text
        print("\nStep 3: Chunking text...")
        start = time.time()
        chunks = smart_chunk(cleaned_text, chunk_size=chunk_size)
        chunks_to_process = chunks[:max_chunks]
        results['steps']['chunking'] = {
            'status': 'success',
            'total_chunks': len(chunks),
            'chunks_to_process': len(chunks_to_process),
            'chunk_sizes': [len(c.split()) for c in chunks_to_process]
        }
        results['timing']['chunking'] = time.time() - start
        print(f"✓ Created {len(chunks)} total chunks, processing {len(chunks_to_process)}")

        # Step 4: Generate Q&A pairs with Gemini
        print(f"\nStep 4: Generating Q&A pairs using Gemini Flash...")
        start = time.time()
        generator = FlashcardGenerator()
        all_flashcards = []

        for i, chunk in enumerate(chunks_to_process):
            print(f"  Chunk {i+1}/{len(chunks_to_process)} ({len(chunk.split())} words)...")
            try:
                qa_pairs = generator.generate_qa_pairs(chunk, num_pairs=num_pairs)
                for qa in qa_pairs:
                    qa['chunk_index'] = i
                    all_flashcards.append(qa)
                print(f"    ✓ Generated {len(qa_pairs)} Q&A pairs")
            except Exception as e:
                logger.error(f"Generation failed for chunk {i}: {e}")
                results['errors'].append(f"Chunk {i} generation: {str(e)}")

        results['steps']['generation'] = {
            'status': 'success',
            'flashcards_generated': len(all_flashcards),
            'chunks_processed': len(chunks_to_process)
        }
        results['timing']['generation'] = time.time() - start
        print(f"✓ Generated {len(all_flashcards)} flashcards in {results['timing']['generation']:.1f}s")

        # Step 5: Classify with DistilBERT
        print(f"\nStep 5: Classifying questions (difficulty, type, topic)...")
        start = time.time()
        classifier = QuestionClassifier()
        classified_flashcards = classifier.classify_flashcards(all_flashcards, context=cleaned_text[:2000])

        results['steps']['classification'] = {
            'status': 'success',
            'flashcards_classified': len(classified_flashcards)
        }
        results['timing']['classification'] = time.time() - start
        print(f"✓ Classified {len(classified_flashcards)} flashcards in {results['timing']['classification']:.1f}s")

        results['flashcards'] = classified_flashcards
        results['status'] = 'success'

    except Exception as e:
        results['status'] = 'failed'
        results['errors'].append(f"Pipeline error: {str(e)}")
        logger.error(f"Pipeline failed: {str(e)}")
        print(f"✗ Pipeline failed: {str(e)}")

    return results


def save_results_json(results: dict, output_file: str = 'pipeline_results.json'):
    """Save full pipeline results to JSON."""
    output_path = Path(__file__).parent.parent / output_file
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Full results saved to {output_path}")


def save_training_data_csv(results: dict, output_file: str = 'training_data.csv'):
    """Save classified flashcards to CSV for DistilBERT fine-tuning."""
    output_path = Path(__file__).parent.parent / output_file
    flashcards = results.get('flashcards', [])

    if not flashcards:
        print("No flashcards to save")
        return

    fieldnames = ['question', 'answer', 'difficulty', 'question_type', 'topic', 'chunk_index']

    # Check if file exists to avoid re-writing header
    file_exists = output_path.exists()

    try:
        with open(output_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            for card in flashcards:
                writer.writerow({
                    'question': card.get('question', ''),
                    'answer': card.get('answer', ''),
                    'difficulty': card.get('difficulty', 'medium'),
                    'question_type': card.get('question_type', 'definition'),
                    'topic': card.get('topic', 'general'),
                    'chunk_index': card.get('chunk_index', 0)
                })

        print(f"✓ Training data saved to {output_path} ({len(flashcards)} rows)")
    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")


def print_results(results: dict):
    """Pretty-print pipeline results."""
    print("\n" + "="*70)
    print(" PHASE 1: COMPLETE PIPELINE TEST RESULTS")
    print("="*70)

    print(f"\n📊 Status: {results['status'].upper()}")
    print(f"🎬 Video: {results['video_url']}")

    # Timing summary
    if results.get('timing'):
        total_time = sum(results['timing'].values())
        print(f"\n⏱️  Execution Times:")
        for step, duration in results['timing'].items():
            print(f"   {step:20s}: {duration:6.1f}s")
        print(f"   {'TOTAL':20s}: {total_time:6.1f}s")

    # Steps summary
    if results.get('steps'):
        print(f"\n✅ Steps Completed:")
        for step, data in results['steps'].items():
            status = "✓" if data.get('status') == 'success' else "✗"
            print(f"   {status} {step}")

    # Flashcards summary
    if results.get('flashcards'):
        cards = results['flashcards']
        print(f"\n🎓 Flashcards Generated: {len(cards)}")

        # Classification breakdown
        difficulties = {}
        question_types = {}
        topics = {}

        for card in cards:
            diff = card.get('difficulty', 'unknown')
            qtype = card.get('question_type', 'unknown')
            topic = card.get('topic', 'general')

            difficulties[diff] = difficulties.get(diff, 0) + 1
            question_types[qtype] = question_types.get(qtype, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1

        print(f"\n  Difficulty Breakdown:")
        for diff, count in sorted(difficulties.items()):
            print(f"    • {diff:10s}: {count:3d} cards")

        print(f"\n  Question Type Breakdown:")
        for qtype, count in sorted(question_types.items()):
            print(f"    • {qtype:15s}: {count:3d} cards")

        print(f"\n  Topic Breakdown:")
        for topic, count in sorted(topics.items()):
            print(f"    • {topic:15s}: {count:3d} cards")

        # Sample flashcards
        print(f"\n📝 Sample Flashcards (first 3):")
        for i, card in enumerate(cards[:3], 1):
            print(f"\n  Card {i}:")
            print(f"    Chunk: {card.get('chunk_index', 0)}")
            print(f"    Level: {card.get('difficulty', 'unknown').upper()}")
            print(f"    Type:  {card.get('question_type', 'unknown').upper()}")
            print(f"    Topic: {card.get('topic', 'general').upper()}")
            q = card.get('question', '')[:70]
            a = card.get('answer', '')[:70]
            print(f"    Q: {q}{'...' if len(card.get('question', '')) > 70 else ''}")
            print(f"    A: {a}{'...' if len(card.get('answer', '')) > 70 else ''}")

    # Errors
    if results.get('errors'):
        print(f"\n⚠️  Errors ({len(results['errors'])}):")
        for error in results['errors'][:5]:
            print(f"    • {error}")
        if len(results['errors']) > 5:
            print(f"    ... and {len(results['errors']) - 5} more")

    print("\n" + "="*70)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Phase 1: Test complete pipeline (Extract → Clean → Chunk → Generate → Classify)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/pipeline_test.py https://youtu.be/dQw4w9WgXcQ
  python tests/pipeline_test.py https://youtu.be/dQw4w9WgXcQ --num-pairs 5 --max-chunks 5
  python tests/pipeline_test.py KyBgxe-rU48 --num-pairs 3 --max-chunks 2
        """
    )
    parser.add_argument('youtube_url',
                        help='YouTube video URL or video ID')
    parser.add_argument('--num-pairs', type=int, default=3,
                        help='Q&A pairs per chunk (default: 3)')
    parser.add_argument('--chunk-size', type=int, default=600,
                        help='Words per chunk (default: 600, tuned for Gemini)')
    parser.add_argument('--max-chunks', type=int, default=3,
                        help='Max chunks to process (default: 3, for testing)')
    parser.add_argument('--skip-csv', action='store_true',
                        help='Skip saving training data CSV')
    parser.add_argument('--json-output', type=str, default='pipeline_results.json',
                        help='JSON output file (default: pipeline_results.json)')
    parser.add_argument('--csv-output', type=str, default='training_data.csv',
                        help='CSV training data file (default: training_data.csv)')

    args = parser.parse_args()

    print("\n🚀 PHASE 1: YOUTUBE TO FLASHCARDS PIPELINE")
    print("─" * 70)
    print(f"   Using: Gemini Flash (Q&A generation)")
    print(f"           DistilBERT (question classification)")
    print(f"           Training data collection for fine-tuning")
    print("─" * 70)

    # Run pipeline
    results = test_pipeline(
        args.youtube_url,
        num_pairs=args.num_pairs,
        chunk_size=args.chunk_size,
        max_chunks=args.max_chunks
    )

    # Save and display results
    save_results_json(results, args.json_output)
    if not args.skip_csv:
        save_training_data_csv(results, args.csv_output)
    print_results(results)

