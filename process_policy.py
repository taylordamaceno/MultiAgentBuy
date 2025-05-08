import json
import os
from typing import List, Dict
import re
from datetime import datetime

def load_config() -> Dict:
    with open('rag_config.json', 'r') as f:
        return json.load(f)

def create_chunks(text: str, config: Dict) -> List[Dict]:
    chunks = []
    chunk_size = config['chunk_settings']['chunk_size']
    chunk_overlap = config['chunk_settings']['chunk_overlap']
    
    # Split by sections first
    sections = re.split(r'#{1,6}\s', text)
    
    for section in sections:
        if not section.strip():
            continue
            
        # Get section title
        title_match = re.match(r'^([^\n]+)', section)
        section_title = title_match.group(1) if title_match else "Unknown Section"
        
        # Split into paragraphs
        paragraphs = section.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            "section": section_title,
                            "category": "policy",
                            "importance": "high",
                            "last_updated": datetime.now().isoformat(),
                            "source": "politica.md",
                            "keywords": extract_keywords(current_chunk)
                        }
                    })
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "section": section_title,
                    "category": "policy",
                    "importance": "high",
                    "last_updated": datetime.now().isoformat(),
                    "source": "politica.md",
                    "keywords": extract_keywords(current_chunk)
                }
            })
    
    return chunks

def extract_keywords(text: str) -> List[str]:
    # Simple keyword extraction - can be improved with NLP
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Ignore short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top 5 most frequent words
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return [k[0] for k in keywords]

def process_policy_file():
    config = load_config()
    
    # Create necessary directories
    os.makedirs('data/chunks', exist_ok=True)
    os.makedirs('data/metadata', exist_ok=True)
    
    # Read policy file
    with open('politica.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create chunks
    chunks = create_chunks(content, config)
    
    # Save chunks
    for i, chunk in enumerate(chunks):
        chunk_file = f'data/chunks/policy_chunk_{i:03d}.json'
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
    
    # Save metadata index
    metadata_index = {
        "total_chunks": len(chunks),
        "sections": list(set(chunk['metadata']['section'] for chunk in chunks)),
        "last_processed": datetime.now().isoformat()
    }
    
    with open('data/metadata/policy_index.json', 'w', encoding='utf-8') as f:
        json.dump(metadata_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_policy_file() 