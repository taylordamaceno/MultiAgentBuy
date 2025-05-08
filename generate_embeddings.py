import json
import os
from typing import List, Dict
import openai
from tqdm import tqdm
import time

def load_config() -> Dict:
    with open('rag_config.json', 'r') as f:
        return json.load(f)

def get_embedding(text: str, config: Dict) -> List[float]:
    """Get embedding for a text using OpenAI's API."""
    try:
        response = openai.Embedding.create(
            input=text,
            model=config['embedding_settings']['model']
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def process_chunks():
    config = load_config()
    
    # Create embeddings directory
    os.makedirs('data/embeddings', exist_ok=True)
    
    # Get all chunk files
    chunk_files = []
    for root, _, files in os.walk('data/chunks'):
        for file in files:
            if file.endswith('.json'):
                chunk_files.append(os.path.join(root, file))
    
    # Process each chunk file
    for chunk_file in tqdm(chunk_files, desc="Processing chunks"):
        # Read chunk
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk = json.load(f)
        
        # Generate embedding
        embedding = get_embedding(chunk['content'], config)
        
        if embedding:
            # Add embedding to chunk
            chunk['embedding'] = embedding
            
            # Save updated chunk
            embedding_file = os.path.join(
                'data/embeddings',
                os.path.basename(chunk_file)
            )
            with open(embedding_file, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            # Respect rate limits
            time.sleep(0.1)  # 100ms delay between requests

def main():
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    process_chunks()

if __name__ == "__main__":
    main() 