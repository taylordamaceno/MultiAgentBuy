"""
Processa as regras financeiras e gera embeddings para busca semântica.
"""

import json
import os
from typing import List, Dict, Any
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa o cliente OpenAI
client = OpenAI()

def load_config() -> Dict:
    """Carrega configuração do arquivo."""
    try:
        with open('config/rag_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return {
            "embedding_settings": {
                "model": "text-embedding-ada-002"
            }
        }

def get_embedding(text: str, config: Dict) -> List[float]:
    """Gera embedding para o texto usando OpenAI API."""
    try:
        response = client.embeddings.create(
            input=text,
            model=config['embedding_settings']['model']
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None

def extract_keywords_from_dict(data: Any) -> List[str]:
    """Extrai palavras-chave de um dicionário ou lista."""
    keywords = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            keywords.append(key)
            if isinstance(value, (dict, list)):
                keywords.extend(extract_keywords_from_dict(value))
            elif isinstance(value, str):
                keywords.extend(value.split())
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                keywords.extend(extract_keywords_from_dict(item))
            elif isinstance(item, str):
                keywords.extend(item.split())
    
    return list(set(keywords))

def process_finance():
    """Processa as regras financeiras e gera embeddings."""
    # Carrega configuração
    config = load_config()
    
    # Cria diretórios se não existirem
    os.makedirs('data/chunks', exist_ok=True)
    os.makedirs('data/embeddings', exist_ok=True)
    os.makedirs('data/metadata', exist_ok=True)
    
    try:
        # Lê o arquivo de regras financeiras
        with open('data/raw/finance_rules.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # Processa cada regra
        for i, rule in enumerate(rules):
            # Converte regra para texto
            rule_text = json.dumps(rule, ensure_ascii=False)
            
            # Gera embedding
            embedding = get_embedding(rule_text, config)
            if not embedding:
                continue
            
            # Extrai palavras-chave
            keywords = extract_keywords_from_dict(rule)
            
            # Prepara metadados
            metadata = {
                'source': 'finance_rules.json',
                'rule_id': i,
                'keywords': keywords
            }
            
            # Salva chunk
            chunk_data = {
                'content': rule_text,
                'metadata': metadata
            }
            with open(f'data/chunks/finance_chunk_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
            
            # Salva embedding
            embedding_data = {
                'embedding': embedding,
                'content': rule_text,
                'metadata': metadata
            }
            with open(f'data/embeddings/finance_embedding_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(embedding_data, f, ensure_ascii=False, indent=2)
            
            # Salva metadados
            with open(f'data/metadata/finance_metadata_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print("Regras financeiras processadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao processar regras financeiras: {e}")
        print("\nVerifique se:")
        print("1. O arquivo data/raw/finance_rules.json existe")
        print("2. A chave da API OpenAI está configurada no arquivo .env")
        print("3. Todas as dependências estão instaladas")

if __name__ == "__main__":
    process_finance() 