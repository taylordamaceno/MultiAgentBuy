import os
from dotenv import load_dotenv
import time
from demo_agent import DemoAssistant
from finance_agent import FinanceAssistant

# Carregar variáveis de ambiente
load_dotenv()

class MultiAgentSystem:
    def __init__(self):
        self.policy_agent = DemoAssistant()
        self.finance_agent = FinanceAssistant()
        
    def detect_domain(self, query):
        """Detecta qual agente deve responder à consulta."""
        query_lower = query.lower()
        
        # Palavras-chave financeiras
        finance_keywords = [
            "orçamento", "disponível", "disponivel", "gasto", 
            "verba", "recurso", "financeiro", "recursos",
            "custo", "valor", "aprovar", "aprovação", "quem aprova",
            "alternativa", "dividir compra", "realocar", "transferência"
        ]
        
        # Palavras-chave de política
        policy_keywords = [
            "permitido", "proibido", "regra", "política", "politica",
            "centro de custo", "processo", "requisição", "categoria",
            "item", "comprar", "prazo", "etapa", "preencher", "formulário"
        ]
        
        # Contar ocorrências
        finance_count = sum(1 for kw in finance_keywords if kw in query_lower)
        policy_count = sum(1 for kw in policy_keywords if kw in query_lower)
        
        # Se ambos tiverem keywords ou nenhum tiver, usar ambos os agentes
        if finance_count > policy_count:
            return "finance"
        elif policy_count > finance_count:
            return "policy"
        else:
            return "both"
    
    def answer(self, query):
        """Direciona a consulta para o agente adequado ou para ambos."""
        domain = self.detect_domain(query)
        
        if domain == "finance":
            print("Consulta classificada como: Financeira")
            return self.finance_agent.answer(query)
        elif domain == "policy":
            print("Consulta classificada como: Política")
            return self.policy_agent.answer(query)
        else:
            print("Consulta classificada como: Híbrida (consultando ambos os agentes)")
            
            # Obter respostas de ambos os agentes
            policy_response = self.policy_agent.answer(query)
            finance_response = self.finance_agent.answer(query)
            
            # Combinar respostas
            combined_response = f"""
=== INFORMAÇÕES DE POLÍTICA DE COMPRAS ===
{policy_response}

=== INFORMAÇÕES FINANCEIRAS E ORÇAMENTÁRIAS ===
{finance_response}
"""
            return combined_response

if __name__ == "__main__":
    # Iniciar sistema multi-agente
    mas = MultiAgentSystem()
    
    # Interface de demonstração
    print("\n=== SISTEMA MULTI-AGENTE DE COMPRAS CORPORATIVAS ===")
    print("Demonstração de Multi-Agente com RAG (Retrieval Augmented Generation)")
    print("Consulte a política de compras e informações financeiras da empresa")
    print("\nExemplos de perguntas para demonstração:")
    print("1. \"Posso comprar um monitor de R$ 5.000? Tem orçamento disponível?\"")
    print("2. \"Qual é o centro de custo para compra de notebook e quem é o responsável pelo orçamento?\"") 
    print("3. \"Quero fazer um treinamento de R$ 20.000, é permitido e há recursos disponíveis?\"")
    print("4. \"Quais são as etapas para comprar um notebook e quem precisa aprovar?\"")
    print("5. \"Há alguma alternativa para comprar um equipamento acima do orçamento disponível?\"")
    print("\nDigite 'sair' para encerrar\n")
    
    # Loop de conversa
    while True:
        query = input("\nSua pergunta: ")
        if query.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando demonstração. Obrigado!")
            break
        
        response = mas.answer(query)
        print(f"\nSistema Multi-Agente: {response}") 