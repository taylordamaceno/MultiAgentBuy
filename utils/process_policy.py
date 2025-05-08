"""
Processa a política de compras e gera embeddings para busca semântica.
"""

import json
import os
from typing import List, Dict
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

def process_policy():
    """Processa a política de compras e gera embeddings."""
    # Carrega configuração
    config = load_config()
    
    # Cria diretórios se não existirem
    os.makedirs('data/chunks', exist_ok=True)
    os.makedirs('data/embeddings', exist_ok=True)
    os.makedirs('data/metadata', exist_ok=True)
    
    try:
        # Lê o arquivo da política
        with open('data/raw/politica.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Divide o conteúdo em chunks
        chunks = content.split('\n\n')
        
        # Processa cada chunk
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            # Gera embedding
            embedding = get_embedding(chunk, config)
            if not embedding:
                continue
            
            # Prepara metadados
            metadata = {
                'source': 'politica.md',
                'section': f'secao_{i+1}',
                'chunk_id': i
            }
            
            # Salva chunk
            chunk_data = {
                'content': chunk,
                'metadata': metadata
            }
            with open(f'data/chunks/chunk_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
            
            # Salva embedding
            embedding_data = {
                'embedding': embedding,
                'content': chunk,
                'metadata': metadata
            }
            with open(f'data/embeddings/embedding_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(embedding_data, f, ensure_ascii=False, indent=2)
            
            # Salva metadados
            with open(f'data/metadata/metadata_{i}.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print("Política de compras processada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao processar política: {e}")
        print("\nVerifique se:")
        print("1. O arquivo data/raw/politica.md existe")
        print("2. A chave da API OpenAI está configurada no arquivo .env")
        print("3. Todas as dependências estão instaladas")

if __name__ == "__main__":
    process_policy() 