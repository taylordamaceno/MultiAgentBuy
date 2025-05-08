import json
import os
from typing import List, Dict
from datetime import datetime

def load_config() -> Dict:
    with open('rag_config.json', 'r') as f:
        return json.load(f)

def create_finance_chunks(data: Dict, config: Dict) -> List[Dict]:
    chunks = []
    
    # Process each main section
    for section_name, section_data in data.items():
        if isinstance(section_data, list):
            # Handle list sections
            for item in section_data:
                chunk = {
                    "content": json.dumps(item, ensure_ascii=False),
                    "metadata": {
                        "section": section_name,
                        "category": "finance",
                        "importance": "high",
                        "last_updated": datetime.now().isoformat(),
                        "source": "finance_rules.json",
                        "keywords": extract_keywords_from_dict(item)
                    }
                }
                chunks.append(chunk)
        elif isinstance(section_data, dict):
            # Handle dictionary sections
            for key, value in section_data.items():
                chunk = {
                    "content": json.dumps({key: value}, ensure_ascii=False),
                    "metadata": {
                        "section": section_name,
                        "category": "finance",
                        "importance": "high",
                        "last_updated": datetime.now().isoformat(),
                        "source": "finance_rules.json",
                        "keywords": extract_keywords_from_dict({key: value})
                    }
                }
                chunks.append(chunk)
        else:
            # Handle simple value sections
            chunk = {
                "content": str(section_data),
                "metadata": {
                    "section": section_name,
                    "category": "finance",
                    "importance": "high",
                    "last_updated": datetime.now().isoformat(),
                    "source": "finance_rules.json",
                    "keywords": [section_name]
                }
            }
            chunks.append(chunk)
    
    return chunks

def extract_keywords_from_dict(data: Dict) -> List[str]:
    keywords = set()
    
    def extract_from_value(value):
        if isinstance(value, str):
            # Split string into words and add to keywords
            words = value.lower().split()
            keywords.update(word for word in words if len(word) > 3)
        elif isinstance(value, (int, float)):
            # Add numeric values as keywords
            keywords.add(str(value))
        elif isinstance(value, dict):
            # Recursively process dictionary values
            for v in value.values():
                extract_from_value(v)
        elif isinstance(value, list):
            # Process list items
            for item in value:
                extract_from_value(item)
    
    # Process all values in the dictionary
    for value in data.values():
        extract_from_value(value)
    
    return list(keywords)[:5]  # Return top 5 keywords

def process_finance_file():
    config = load_config()
    
    # Create necessary directories
    os.makedirs('data/chunks', exist_ok=True)
    os.makedirs('data/metadata', exist_ok=True)
    
    # Read finance rules file
    with open('finance_rules.json', 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Create chunks
    chunks = create_finance_chunks(content, config)
    
    # Save chunks
    for i, chunk in enumerate(chunks):
        chunk_file = f'data/chunks/finance_chunk_{i:03d}.json'
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
    
    # Save metadata index
    metadata_index = {
        "total_chunks": len(chunks),
        "sections": list(set(chunk['metadata']['section'] for chunk in chunks)),
        "last_processed": datetime.now().isoformat()
    }
    
    with open('data/metadata/finance_index.json', 'w', encoding='utf-8') as f:
        json.dump(metadata_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_finance_file() 