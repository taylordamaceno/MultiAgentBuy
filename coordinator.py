"""
Coordenador principal do sistema.
Gerencia a comunicação entre os diferentes agentes e coordena o fluxo de processamento.
"""

from typing import Dict, List, Optional
from agents.rag_agent import RAGAgent
from agents.procurement_agent import ProcurementAgent
from agents.finance_agent import FinanceAgent
from openai import OpenAI

# Inicializa o cliente OpenAI
client = OpenAI()

class Coordinator:
    def __init__(self):
        """Inicializa o coordenador e seus agentes."""
        # Inicializa os agentes
        self.rag_agent = RAGAgent()
        self.procurement_agent = ProcurementAgent()
        self.finance_agent = FinanceAgent()
        
        # Cache para respostas similares
        self.response_cache: Dict[str, str] = {}
        
    def classify_question(self, question: str) -> Dict[str, float]:
        """
        Classifica o tipo da pergunta usando GPT-3.5.
        Retorna um dicionário com as probabilidades para cada tipo.
        """
        prompt = f"""
        Classifique a seguinte pergunta em uma das categorias:
        - procurement: Perguntas sobre processos, regras e políticas de compras
        - finance: Perguntas sobre orçamento, custos e aprovações financeiras
        - combined: Perguntas que precisam de ambos os aspectos

        Pergunta: {question}

        Responda apenas com o nome da categoria mais apropriada.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um classificador de perguntas."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            category = response.choices[0].message.content.strip().lower()
            return {"category": category}
            
        except Exception as e:
            print(f"Erro ao classificar pergunta: {e}")
            return {"category": "combined"}
    
    def process_question(self, question: str) -> str:
        """
        Processa uma pergunta do usuário e retorna uma resposta apropriada.
        """
        # Verifica cache
        if question in self.response_cache:
            return self.response_cache[question]
        
        try:
            # 1. Busca contexto relevante usando RAG
            context = self.rag_agent.search(question)
            
            # 2. Classifica o tipo da pergunta
            classification = self.classify_question(question)
            category = classification["category"]
            
            # 3. Processa com o agente apropriado
            if category == "procurement":
                response = self.procurement_agent.answer(question, context)
            elif category == "finance":
                response = self.finance_agent.answer(question, context)
            else:  # combined
                # Obtém respostas de ambos os agentes
                proc_response = self.procurement_agent.answer(question, context)
                fin_response = self.finance_agent.answer(question, context)
                
                # Combina as respostas
                response = self.combine_answers(proc_response, fin_response)
            
            # Armazena no cache
            self.response_cache[question] = response
            return response
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"
    
    def combine_answers(self, proc_response: str, fin_response: str) -> str:
        """
        Combina respostas dos agentes de compras e finanças de forma coerente.
        """
        prompt = f"""
        Combine as seguintes respostas em uma única resposta coerente e bem estruturada:

        Resposta do Agente de Compras:
        {proc_response}

        Resposta do Agente Financeiro:
        {fin_response}

        Mantenha todas as informações importantes e organize de forma clara.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente que combina informações de forma clara e organizada."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Em caso de erro, retorna as respostas separadas
            return f"""
            Informações sobre Processo de Compra:
            {proc_response}

            Informações Financeiras:
            {fin_response}
            """ 