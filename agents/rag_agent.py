"""
Agente responsável por buscar informações relevantes nos documentos.
Utiliza RAG (Retrieval Augmented Generation) para encontrar e processar informações.
"""

import json
import os
from typing import List, Dict
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
import faiss

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa o cliente OpenAI
client = OpenAI()

class RAGAgent:
    """Agente responsável por buscar informações relevantes nos documentos."""
    
    def __init__(self):
        """Inicializa o agente RAG."""
        self.config = self._load_config()
        self.embeddings, self.contents, self.metadata = self._load_embeddings()
        self.index = self._create_index(self.embeddings) if len(self.embeddings) > 0 else None
    
    def _load_config(self) -> Dict:
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
    
    def _load_embeddings(self) -> tuple:
        """Carrega todos os embeddings e seus conteúdos."""
        embeddings = []
        contents = []
        metadata = []
        
        try:
            # Carrega embeddings do diretório
            for root, _, files in os.walk('data/embeddings'):
                for file in files:
                    if file.endswith('.json'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            embeddings.append(data['embedding'])
                            contents.append(data['content'])
                            metadata.append(data['metadata'])
        except Exception as e:
            print(f"Erro ao carregar embeddings: {e}")
        
        if not embeddings:
            print("Nenhum embedding encontrado. Execute o setup.py primeiro.")
            return np.array([]), [], []
        
        return np.array(embeddings), contents, metadata
    
    def _create_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Cria um índice FAISS para busca de similaridade."""
        if len(embeddings) == 0:
            return None
            
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index
    
    def _get_embedding(self, text: str) -> List[float]:
        """Gera embedding para o texto usando OpenAI API."""
        try:
            response = client.embeddings.create(
                input=text,
                model=self.config['embedding_settings']['model']
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            return None
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Busca chunks similares à query."""
        if not self.index or len(self.contents) == 0:
            print("Nenhum embedding disponível para busca. Execute o setup.py primeiro.")
            return []
            
        # Gera embedding para a query
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
        
        # Busca chunks similares
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        # Prepara resultados
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.contents):
                results.append({
                    'content': self.contents[idx],
                    'metadata': self.metadata[idx],
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
        response = client.chat.completions.create(
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
        exit(1)
    
    # Inicializa o agente
    agent = RAGAgent()
    
    print("\nAssistente de Compras Internas com RAG")
    print("Digite 'sair' para encerrar")
    
    while True:
        query = input("\nSua pergunta: ").strip()
        if query.lower() == 'sair':
            break
        
        # Busca chunks similares
        similar_chunks = agent.search(query)
        
        # Mostra resultados
        if similar_chunks:
            print("\nInformações encontradas:")
            for chunk in similar_chunks:
                print(f"\nConteúdo: {chunk['content']}")
                print(f"Fonte: {chunk['metadata']['source']}")
                print(f"Seção: {chunk['metadata']['section']}")
                print(f"Similaridade: {chunk['similarity']:.2f}")
        else:
            print("\nNenhuma informação relevante encontrada.")

if __name__ == "__main__":
    main() 