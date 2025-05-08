import json
import os
from typing import List, Dict
import openai
import numpy as np
from dotenv import load_dotenv
import faiss

# Carrega variáveis de ambiente
load_dotenv()

def load_config() -> Dict:
    with open('rag_config.json', 'r') as f:
        return json.load(f)

def load_embeddings() -> tuple:
    """Carrega todos os embeddings e seus conteúdos."""
    embeddings = []
    contents = []
    metadata = []
    
    # Carrega embeddings do diretório
    for root, _, files in os.walk('data/embeddings'):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    embeddings.append(data['embedding'])
                    contents.append(data['content'])
                    metadata.append(data['metadata'])
    
    return np.array(embeddings), contents, metadata

def create_index(embeddings: np.ndarray) -> faiss.Index:
    """Cria um índice FAISS para busca de similaridade."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def get_embedding(text: str, config: Dict) -> List[float]:
    """Gera embedding para o texto usando OpenAI API."""
    try:
        response = openai.Embedding.create(
            input=text,
            model=config['embedding_settings']['model']
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None

def search_similar_chunks(query: str, index: faiss.Index, 
                         contents: List[str], metadata: List[Dict],
                         config: Dict, k: int = 3) -> List[Dict]:
    """Busca chunks similares à query."""
    # Gera embedding para a query
    query_embedding = get_embedding(query, config)
    if not query_embedding:
        return []
    
    # Busca chunks similares
    distances, indices = index.search(np.array([query_embedding]), k)
    
    # Prepara resultados
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(contents):
            results.append({
                'content': contents[idx],
                'metadata': metadata[idx],
                'similarity': float(1 / (1 + distances[0][i]))  # Converte distância para similaridade
            })
    
    return results

def generate_response(query: str, similar_chunks: List[Dict]) -> str:
    """Gera resposta usando os chunks similares encontrados."""
    # Prepara o contexto com os chunks mais relevantes
    context = "\n\n".join([
        f"Conteúdo: {chunk['content']}\n"
        f"Fonte: {chunk['metadata']['source']}\n"
        f"Seção: {chunk['metadata']['section']}"
        for chunk in similar_chunks
    ])
    
    # Cria o prompt para o modelo
    prompt = f"""Com base nas seguintes informações, responda à pergunta do usuário.
Se a informação não estiver disponível no contexto, diga que não tem informação suficiente.

Contexto:
{context}

Pergunta: {query}

Resposta:"""
    
    try:
        # Gera resposta usando OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em políticas de compras e regras financeiras."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Desculpe, ocorreu um erro ao processar sua pergunta."

def main():
    # Verifica API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Por favor, configure a variável de ambiente OPENAI_API_KEY")
        return
    
    # Carrega configuração
    config = load_config()
    
    # Carrega embeddings e cria índice
    print("Carregando embeddings...")
    embeddings, contents, metadata = load_embeddings()
    index = create_index(embeddings)
    
    print("\nAssistente de Compras Internas com RAG")
    print("Digite 'sair' para encerrar")
    
    while True:
        query = input("\nSua pergunta: ").strip()
        if query.lower() == 'sair':
            break
        
        # Busca chunks similares
        similar_chunks = search_similar_chunks(query, index, contents, metadata, config)
        
        # Gera resposta
        response = generate_response(query, similar_chunks)
        print("\nResposta:", response)

if __name__ == "__main__":
    main() 