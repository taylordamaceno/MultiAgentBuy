"""
Agente especializado em questões de compras.
Responsável por responder perguntas sobre políticas de compras e processos de aquisição.
"""

import os
from dotenv import load_dotenv
import time
import re
from openai import OpenAI
from typing import List, Dict
from .finance_agent import FinanceAgent

# Inicializa o cliente OpenAI
client = OpenAI()

# Carregar variáveis de ambiente
load_dotenv()

# Carregar o conteúdo da política
try:
    with open('data/raw/politica.md', 'r', encoding='utf-8') as file:
        policy_content = file.read()
    print("Política carregada com sucesso.")
except Exception as e:
    print(f"Erro ao carregar a política: {str(e)}")
    policy_content = ""

# Categorias de itens permitidos e proibidos
ITEM_CATEGORIES = {
    "equipamentos_ti": ["notebook", "monitor", "computador", "desktop", "teclado", "mouse", "headset", "webcam", "dock", "docking", "estação", "placa", "hd", "tablet", "impressora"],
    "software": ["software", "licença", "licenca", "aplicativo", "app", "sistema", "programa", "office", "windows", "adobe", "ide", "ferramenta digital"],
    "mobiliario": ["cadeira", "mesa", "móvel", "ergonomico", "ergonômico", "suporte", "apoio", "luminária", "armário", "gaveteiro", "estante"],
    "treinamento": ["curso", "treinamento", "capacitação", "workshop", "certificação", "palestra", "evento", "conferência"],
    "home_office": ["home office", "cadeira ergonomica", "mesa ajustável", "iluminação", "suporte monitor", "apoio de pés"],
    "proibidos": ["presente", "pessoal", "uso particular", "streaming", "netflix", "spotify", "bebida", "alcool", "álcool", "cerveja", "vinho", "camisa", "roupa", "vestuário", "vestuario"]
}

class ProcurementAgent:
    """Agente especializado em questões de compras."""
    
    def __init__(self):
        """Inicializa o agente de compras."""
        self.finance_agent = FinanceAgent()
        self.policy = policy_content
        self.conversation_memory = {
            "last_item": None,
            "last_value": None,
            "last_centro_custo": None,
            "history": []
        }
    
    def extract_monetary_value(self, query):
        """Extrai valores monetários da consulta do usuário."""
        query_lower = query.lower()
        
        # Padrão para encontrar valores em diversos formatos
        patterns = [
            r'r\$\s*(\d+[\.,]?\d*)', # R$ 5.000 ou R$5000
            r'(\d+)[\.,]?(\d*)\s*reais', # 5.000 reais ou 5000 reais
            r'(\d+)[\.,]?(\d*)\s*mil', # 5 mil ou 5.5 mil
            r'valor\s*de\s*(\d+)[\.,]?(\d*)', # valor de 5.000
            r'custa\s*(\d+)[\.,]?(\d*)', # custa 5.000
            r'(\d+)[\.,]?(\d*)\s*k', # 5k ou 5.5k
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                # Se encontrou algo, tenta converter para um número
                try:
                    if "mil" in pattern or "k" in pattern:
                        # Para valores como "5 mil" ou "5k"
                        if isinstance(matches[0], tuple):
                            value = matches[0][0]
                            decimal = matches[0][1] if len(matches[0]) > 1 and matches[0][1] else "0"
                            if decimal:
                                return float(f"{value}.{decimal}") * 1000
                            else:
                                return float(value) * 1000
                        else:
                            return float(matches[0]) * 1000
                    
                    elif isinstance(matches[0], tuple):
                        # Se o padrão tem grupos separados por vírgula ou ponto
                        if len(matches[0]) > 1 and matches[0][1]:  # Se tem casas decimais
                            number = f"{matches[0][0]}.{matches[0][1]}"
                        else:
                            number = matches[0][0]
                    else:
                        # Se o valor está em um único grupo
                        number = matches[0].replace('.', '').replace(',', '.')
                    
                    return float(number)
                except:
                    pass
        
        return None
    
    def identify_item_category(self, query):
        """Identifica a categoria do item mencionado na consulta."""
        query_lower = query.lower()
        
        # Extrai o que parece ser o nome do item
        item_patterns = [
            r'(?:comprar|adquirir|requisitar)\s+(?:um|uma|uns|umas|o|a|os|as)?\s+([a-záàâãéèêíïóôõöúçñ\s]+?)(?:\s+(?:de|para|com|por|no valor|que custa))',
            r'(?:sobre|para)\s+(?:um|uma|uns|umas|o|a|os|as)?\s+([a-záàâãéèêíïóôõöúçñ\s]+?)(?:\s+(?:de|para|com|por|no valor|que custa))',
            r'(?:compra|aquisição)\s+(?:de|da|do)?\s+(?:um|uma|uns|umas|o|a|os|as)?\s+([a-záàâãéèêíïóôõöúçñ\s]+?)(?:\s+(?:de|para|com|por|no valor|que custa))'
        ]
        
        extracted_item = None
        
        # Tenta extrair o nome do item usando os padrões acima
        for pattern in item_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                extracted_item = matches[0].strip()
                break
        
        # Se não conseguiu extrair, procura por palavras-chave
        if not extracted_item:
            for category, keywords in ITEM_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        extracted_item = keyword
                        break
                if extracted_item:
                    break
        
        # Verificar se o contexto indica home office
        is_home_office = "home office" in query_lower or "casa" in query_lower or "remoto" in query_lower or "remota" in query_lower or "residência" in query_lower
        
        # Verifica em qual categoria o item se encaixa
        if extracted_item:
            # Verificar se é um item que pode ser tanto de escritório quanto de home office
            is_furniture = False
            for keyword in ITEM_CATEGORIES["mobiliario"]:
                if keyword in extracted_item:
                    is_furniture = True
                    break
            
            is_home_office_item = False
            for keyword in ITEM_CATEGORIES["home_office"]:
                if keyword in extracted_item:
                    is_home_office_item = True
                    break
            
            # Define a categoria do item
            item_category = None
            for category, keywords in ITEM_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in extracted_item:
                        item_category = category
                        break
                if item_category:
                    break
            
            # Ajusta a categoria para home office se necessário
            if is_furniture and is_home_office:
                item_category = "home_office"
            
            # Se é um item proibido, retorna imediatamente
            if item_category == "proibidos":
                return {
                    "item": extracted_item,
                    "category": "proibidos",
                    "allowed": False,
                    "message": f"O item '{extracted_item}' aparenta ser de uso pessoal, o que não é permitido pela política de compras."
                }
            
            # Retorna informações sobre o item
            centro_custo = None
            if item_category == "equipamentos_ti" or item_category == "software":
                centro_custo = "TI – Infraestrutura"
            elif item_category == "treinamento":
                centro_custo = "RH – Desenvolvimento"
            elif item_category == "home_office":
                centro_custo = "Facilities - Home Office"
            elif item_category == "mobiliario":
                centro_custo = "Facilities"
            
            # Atualiza a memória da conversa
            self.conversation_memory["last_item"] = extracted_item
            self.conversation_memory["last_centro_custo"] = centro_custo
            
            return {
                "item": extracted_item,
                "category": item_category,
                "allowed": True,
                "centro_custo": centro_custo,
                "message": f"O item '{extracted_item}' é uma aquisição válida para o centro de custo '{centro_custo}'."
            }
        
        return None
    
    def answer(self, question: str, context: List[Dict]) -> str:
        """
        Gera uma resposta para a pergunta usando o contexto fornecido.
        
        Args:
            question: A pergunta do usuário
            context: Lista de chunks relevantes encontrados pelo RAG
            
        Returns:
            str: Resposta gerada
        """
        # Se a pergunta envolve aspectos financeiros, delega para o agente financeiro
        if any(keyword in question.lower() for keyword in ['orçamento', 'valor', 'custo', 'preço', 'financeiro']):
            return self.finance_agent.answer(question, context)
        
        # Tenta extrair informações sobre item e valor
        item_info = self.identify_item_category(question)
        monetary_value = self.extract_monetary_value(question)
        
        # Atualiza a memória de conversação
        if monetary_value:
            self.conversation_memory["last_value"] = monetary_value
        
        # Consulta o agente financeiro se a pergunta envolver valores financeiros
        finance_info = None
        if monetary_value and item_info and item_info["centro_custo"]:
            finance_context = []  # Contexto vazio para uma resposta mais concisa
            finance_query = f"Posso fazer uma compra de {monetary_value} reais para o centro de custo {item_info['centro_custo']}?"
            finance_info = self.finance_agent.answer(finance_query, finance_context)
        
        # Se identificou um item ou valor, gera uma resposta enriquecida
        if item_info or monetary_value:
            # Adiciona informações do contexto
            enriched_context = ""
            if context:
                relevant_context = [chunk for chunk in context 
                                   if item_info and item_info["item"] in chunk["content"].lower()]
                if relevant_context:
                    enriched_context = "\n\n".join([chunk["content"] for chunk in relevant_context[:2]])
            
            # Constrói uma resposta com base nas informações extraídas
            response_parts = []
            
            if item_info:
                if item_info["allowed"]:
                    response_parts.append(f"✅ {item_info['message']}")
                    
                    # Adiciona detalhes de aprovação se tiver valor
                    if monetary_value:
                        if finance_info:
                            response_parts.append(finance_info)
                        
                        # Adiciona informações sobre o processo de compra
                        approval_info = ""
                        if monetary_value <= 2000:
                            approval_info = f"Para compras até R$ {monetary_value:.2f}, você precisa apenas da aprovação do seu gestor direto. O processo geralmente leva 1 dia útil."
                        elif monetary_value <= 10000:
                            approval_info = f"Para compras de R$ {monetary_value:.2f}, você precisa da aprovação do gestor e do departamento financeiro. O processo geralmente leva 3 dias úteis."
                        else:
                            approval_info = f"Para compras acima de R$ 10.000 como esta (R$ {monetary_value:.2f}), você precisa da aprovação do gestor, departamento financeiro e diretoria executiva. O processo pode levar até 7 dias úteis."
                        
                        response_parts.append(approval_info)
                else:
                    response_parts.append(f"❌ {item_info['message']}")
                    response_parts.append("Por favor, consulte a política de compras para mais detalhes sobre itens permitidos.")
            elif monetary_value:
                # Se tem apenas o valor mas não identificou o item
                response_parts.append(f"Para uma compra no valor de R$ {monetary_value:.2f}, é necessário especificar o item para que eu possa fornecer informações mais precisas.")
                if finance_info:
                    response_parts.append(finance_info)
            
            # Adiciona contexto relevante da política, se disponível
            if enriched_context:
                response_parts.append("\nInformações adicionais da política de compras:")
                response_parts.append(enriched_context)
            
            return "\n\n".join(response_parts)
        
        # Se não conseguiu extrair informações específicas, usa o método padrão
        if not context:
            return "Desculpe, não encontrei informações relevantes para responder sua pergunta."
        
        # Prepara o contexto
        context_text = "\n\n".join([
            f"Conteúdo: {chunk['content']}\n"
            f"Fonte: {chunk['metadata']['source']}\n"
            f"Seção: {chunk['metadata']['section'] if 'section' in chunk['metadata'] else ''}"
            for chunk in context
        ])
        
        # Cria o prompt
        prompt = f"""Com base nas seguintes informações sobre políticas de compras, responda à pergunta do usuário.
        Se a informação não estiver disponível no contexto, diga que não tem informação suficiente.

        Contexto:
        {context_text}

        Pergunta: {question}

        Resposta:"""
        
        try:
            # Gera resposta usando OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em processos de compras corporativas."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta sobre compras."

if __name__ == "__main__":
    # Iniciar assistente
    assistant = ProcurementAgent()
    
    # Interface de demonstração
    print("\n=== ASSISTENTE INTELIGENTE DE COMPRAS CORPORATIVAS ===")
    print("Demonstração de RAG com Agentes Especializados")
    print("Consulte a política de compras e viabilidade financeira")
    print("\nExemplos de perguntas para demonstração:")
    print("1. \"Posso comprar um monitor ultrawide de 34 polegadas por R$ 5.000?\"")
    print("2. \"Qual é o centro de custo para a compra de um notebook de R$ 12.000?\"") 
    print("3. \"Quais são as etapas para solicitar um treinamento de R$ 20.000?\"")
    print("4. \"Quero comprar uma cadeira ergonômica de R$ 1.800, há orçamento disponível?\"")
    print("5. \"Quem precisa aprovar uma compra de software de R$ 8.500?\"")
    print("\nDigite 'sair' para encerrar\n")
    
    # Loop de conversa
    while True:
        query = input("\nSua pergunta: ")
        if query.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando demonstração. Obrigado!")
            break
        
        response = assistant.answer(query)
        print(f"\nAssistente: {response}") 