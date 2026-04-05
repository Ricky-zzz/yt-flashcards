"""
Pipeline test script - Standalone test of the entire Q&A generation pipeline.
Run this to validate the pipeline before integrating into FastAPI.

Usage:
    python tests/pipeline_test.py <youtube_url> [--num_pairs N] [--chunk_size N]
"""
import sys
import json
from pathlib import Path

# Add the parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.transcript import get_transcript
from app.services.cleaner import preprocess_for_chunking
from app.services.chunker import smart_chunk
from app.services.generator import T5GeneratorService


def test_pipeline(youtube_url: str, 
                  num_pairs: int = 3,
                  chunk_size: int = 300,
                  max_chunks: int = 3) -> dict:
    """
    Run the complete pipeline: Extract → Clean → Chunk → Generate.
    
    Args:
        youtube_url: YouTube video URL or video ID
        num_pairs: Number of Q&A pairs per chunk
        chunk_size: Target words per chunk
        max_chunks: Maximum chunks to process (limit for testing)
    
    Returns:
        Dict with results and metadata
    """
    results = {
        'status': 'in_progress',
        'steps': {},
        'video_url': youtube_url,
        'errors': []
    }
    
    try:
        # Step 1: Extract transcript
        print("Step 1: Extracting transcript...")
        transcript = get_transcript(youtube_url)
        results['steps']['extraction'] = {
            'status': 'success',
            'transcript_length': len(transcript),
            'word_count': len(transcript.split())
        }
        print(f"✓ Extracted {len(transcript.split())} words")
        
        # Step 2: Clean text
        print("\nStep 2: Cleaning text...")
        cleaned_text = preprocess_for_chunking(transcript)
        results['steps']['cleaning'] = {
            'status': 'success',
            'cleaned_length': len(cleaned_text),
            'word_count': len(cleaned_text.split())
        }
        print(f"✓ Cleaned text: {len(cleaned_text.split())} words")
        
        # Step 3: Chunk text
        print("\nStep 3: Chunking text...")
        chunks = smart_chunk(cleaned_text, chunk_size=chunk_size)
        results['steps']['chunking'] = {
            'status': 'success',
            'total_chunks': len(chunks),
            'chunk_sizes': [len(c.split()) for c in chunks]
        }
        print(f"✓ Created {len(chunks)} chunks")
        
        # Limit chunks for testing
        chunks_to_process = chunks[:max_chunks]
        
        # Step 4: Generate Q&A pairs
        print(f"\nStep 4: Generating Q&A pairs from {len(chunks_to_process)} chunks...")
        all_flashcards = []
        
        for i, chunk in enumerate(chunks_to_process):
            print(f"  Processing chunk {i+1}/{len(chunks_to_process)}...")
            try:
                qa_pairs = T5GeneratorService.generate_qa_pairs(
                    chunk,
                    num_pairs=num_pairs,
                    model_name='t5-small'
                )
                
                for qa in qa_pairs:
                    all_flashcards.append({
                        'chunk_index': i,
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'source_text_length': len(chunk.split())
                    })
            except Exception as e:
                print(f"  ✗ Error processing chunk {i+1}: {str(e)}")
                results['errors'].append(f"Chunk {i}: {str(e)}")
                continue
        
        results['steps']['generation'] = {
            'status': 'success',
            'flashcards_generated': len(all_flashcards),
            'chunks_processed': len(chunks_to_process)
        }
        print(f"✓ Generated {len(all_flashcards)} flashcards")
        
        results['flashcards'] = all_flashcards
        results['status'] = 'success'
        
    except Exception as e:
        results['status'] = 'failed'
        results['errors'].append(f"Pipeline error: {str(e)}")
        print(f"✗ Pipeline failed: {str(e)}")
    
    return results


def save_results(results: dict, output_file: str = 'pipeline_results.json'):
    """Save pipeline results to JSON file."""
    output_path = Path(__file__).parent.parent / output_file
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")


def print_results(results: dict):
    """Pretty-print pipeline results."""
    print("\n" + "="*60)
    print("PIPELINE TEST RESULTS")
    print("="*60)
    
    print(f"\nStatus: {results['status'].upper()}")
    print(f"Video: {results['video_url']}")
    
    if results.get('steps'):
        print("\nSteps completed:")
        for step, data in results['steps'].items():
            print(f"  • {step}: {data['status']}")
    
    if results.get('flashcards'):
        print(f"\nFlashcards generated: {len(results['flashcards'])}")
        print("\nSample flashcards:")
        for i, card in enumerate(results['flashcards'][:3], 1):
            print(f"\n  Card {i}:")
            print(f"    Q: {card['question'][:80]}...")
            print(f"    A: {card['answer'][:80]}...")
    
    if results.get('errors'):
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  • {error}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the YouTube-to-Flashcards pipeline')
    parser.add_argument('youtube_url', 
                        help='YouTube video URL or video ID')
    parser.add_argument('--num_pairs', type=int, default=3,
                        help='Number of Q&A pairs per chunk (default: 3)')
    parser.add_argument('--chunk_size', type=int, default=300,
                        help='Target words per chunk (default: 300)')
    parser.add_argument('--max_chunks', type=int, default=3,
                        help='Maximum chunks to process (default: 3)')
    parser.add_argument('--output', type=str, default='pipeline_results.json',
                        help='Output JSON file name (default: pipeline_results.json)')
    
    args = parser.parse_args()
    
    # Run pipeline
    results = test_pipeline(
        args.youtube_url,
        num_pairs=args.num_pairs,
        chunk_size=args.chunk_size,
        max_chunks=args.max_chunks
    )
    
    # Save and display results
    save_results(results, args.output)
    print_results(results)
