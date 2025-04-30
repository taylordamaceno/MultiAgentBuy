import os
from dotenv import load_dotenv
import time
import re
from finance_agent import FinanceAssistant

# Carregar variáveis de ambiente
load_dotenv()

# Carregar o conteúdo da política
try:
    with open('politica.md', 'r', encoding='utf-8') as file:
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

# Sistema de resposta aprimorado com análise contextual
class ProcurementAssistant:
    def __init__(self):
        self.policy = policy_content
        self.finance_agent = FinanceAssistant()
        self.conversation_memory = {
            "last_item": None,
            "last_value": None,
            "last_centro_custo": None,
            "history": []
        }
    
    def extract_monetary_value(self, query):
        """Extrai valores monetários da consulta do usuário de forma mais robusta."""
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
            
            # Se for um item de mobiliário e o contexto indica home office, categorizar como home_office
            if is_furniture and is_home_office:
                return {
                    "categoria": "home_office",
                    "item": extracted_item,
                    "proibido": False
                }
            
            # Verificar outras categorias
            for category, keywords in ITEM_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in extracted_item:
                        return {
                            "categoria": category,
                            "item": extracted_item,
                            "proibido": category == "proibidos"
                        }
        
        # Tenta identificar pelo resto da consulta
        for category, keywords in ITEM_CATEGORIES.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return {
                        "categoria": category,
                        "item": keyword,
                        "proibido": category == "proibidos"
                    }
        
        return None
    
    def extract_item_type(self, query):
        """Extrai o tipo de item e o centro de custo correspondente."""
        item_info = self.identify_item_category(query)
        
        if not item_info:
            return None
        
        # Mapeamento de categorias para centros de custo
        category_to_cost_center = {
            "equipamentos_ti": "TI – Infraestrutura",
            "software": "TI – Ferramentas",
            "mobiliario": "Facilities",
            "treinamento": "RH – Desenvolvimento",
            "home_office": "Facilities - Home Office",
            "proibidos": None  # Itens proibidos não têm centro de custo
        }
        
        centro_custo = category_to_cost_center.get(item_info["categoria"])
        
        return {
            "item": item_info["item"],
            "categoria": item_info["categoria"],
            "centro_custo": centro_custo,
            "proibido": item_info["proibido"]
        }
    
    def should_consult_finance(self, query, item_info, monetary_value):
        """Determina se deve consultar o agente financeiro com base na análise da consulta."""
        query_lower = query.lower()
        
        # Palavras-chave que indicam consulta financeira
        finance_keywords = [
            "orçamento", "disponível", "disponivel", "gasto", 
            "verba", "recurso", "financeiro", "recursos",
            "custo", "valor", "aprovar", "aprovação", "quem aprova",
            "alternativa", "dividir compra", "realocar"
        ]
        
        # Se há um valor monetário na consulta acima de 2000
        if monetary_value and monetary_value > 2000:
            return True
        
        # Se há palavras-chave financeiras
        for keyword in finance_keywords:
            if keyword in query_lower:
                return True
        
        # Se o usuário pergunta sobre um item permitido com centro de custo
        if item_info and not item_info["proibido"] and item_info["centro_custo"]:
            return True
                
        return False
    
    def get_approval_info(self, value):
        """Retorna informações sobre o fluxo de aprovação necessário com base no valor."""
        if value <= 2000:
            return {
                "aprovacao": "Aprovação automática pelo sistema",
                "aprovadores": ["Sistema"],
                "dias_uteis": 1
            }
        elif 2001 <= value <= 10000:
            return {
                "aprovacao": "Aprovação do gestor da área + Financeiro",
                "aprovadores": ["Gestor da área", "Financeiro"],
                "dias_uteis": 3
            }
        else:  # value > 10000
            return {
                "aprovacao": "Aprovação do gestor da área + Financeiro + Diretoria Executiva",
                "aprovadores": ["Gestor da área", "Financeiro", "Diretoria Executiva"],
                "dias_uteis": 7
            }
    
    def build_contextual_response(self, query, item_info, monetary_value, finance_data=None):
        """Constrói uma resposta inteligente e contextualizada com base na análise."""
        response = ""
        
        # Se for um item proibido
        if item_info and item_info["proibido"]:
            return f"""
Não é permitida a compra de {item_info['item']} pela empresa.

De acordo com a política de compras (Seção 6 - Itens Proibidos), itens como {item_info['item']} estão explicitamente listados como não autorizados para aquisição corporativa.

Recomendo consultar a lista de itens permitidos na Seção 2 da política para verificar alternativas que atendam à sua necessidade.
"""

        # Compra sem item identificado
        if not item_info:
            if monetary_value:
                # Se tem apenas o valor, falar sobre o fluxo de aprovação
                approval_info = self.get_approval_info(monetary_value)
                response = f"""
Para uma compra no valor de R$ {monetary_value:,.2f}, o fluxo de aprovação necessário é:
- {approval_info['aprovacao']}
- Tempo estimado: {approval_info['dias_uteis']} dias úteis

No entanto, não consegui identificar qual item você deseja comprar. Diferentes itens possuem centros de custo e regras específicas.

Poderia especificar qual item deseja adquirir para que eu forneça informações mais precisas?
"""
            else:
                # Se não tem nem item nem valor
                response = """
Não consegui identificar o item específico ou valor da compra em sua consulta.

A política de compras da empresa permite diversos itens como equipamentos de TI, softwares, mobiliário e cursos, cada um com seu fluxo específico de aprovação e centro de custo.

Poderia reformular sua pergunta mencionando qual item deseja adquirir e possivelmente o valor estimado?
"""
        
        # Compra com item, mas sem valor
        elif not monetary_value:
            response = f"""
Sobre a aquisição de {item_info['item']}:

Este item se enquadra na categoria "{item_info['categoria'].replace('_', ' ').title()}" e deve ser alocado ao centro de custo "{item_info['centro_custo']}".

De acordo com a política de compras (Seção 2), este tipo de item é permitido para aquisição. O processo de requisição envolve:
1. Preencher o formulário no sistema interno
2. Anexar cotação ou link do item
3. Informar o centro de custo "{item_info['centro_custo']}"
4. Enviar para aprovação conforme o valor

Não consegui identificar o valor da compra em sua consulta. O fluxo de aprovação depende do valor:
- Até R$ 2.000: Aprovação automática (1 dia útil)
- R$ 2.001 a R$ 10.000: Gestor + Financeiro (3 dias úteis)
- Acima de R$ 10.000: Gestor + Financeiro + Diretoria (7 dias úteis)
"""

            # Adicionar informações financeiras quando disponíveis
            if finance_data and "Orçamento disponível" in finance_data:
                response += f"""

Informações financeiras adicionais:
- Centro de custo: {item_info['centro_custo']}
- {finance_data.split("Centro de custo:")[1].split("Você pode perguntar sobre")[0].strip()}
"""
            else:
                response += """

Poderia informar o valor estimado para que eu forneça orientações mais específicas sobre viabilidade financeira?
"""
        
        # Compra com item e valor
        else:
            approval_info = self.get_approval_info(monetary_value)
            
            response = f"""
Sobre a aquisição de {item_info['item']} no valor de R$ {monetary_value:,.2f}:

1. Classificação: Este item se enquadra na categoria "{item_info['categoria'].replace('_', ' ').title()}"
2. Centro de custo: "{item_info['centro_custo']}"
3. Fluxo de aprovação: {approval_info['aprovacao']}
4. Prazo estimado: {approval_info['dias_uteis']} dias úteis

De acordo com a política de compras (Seção 2), este tipo de item é permitido para aquisição, desde que siga o processo de requisição:
- Preencher o formulário no sistema interno
- Anexar cotação ou link do item
- Informar o centro de custo adequado
- Enviar para o fluxo de aprovação
"""

            # Adicionar condições específicas com base no valor
            if monetary_value > 5000 and item_info['categoria'] == 'equipamentos_ti':
                response += """
Observação: Para equipamentos de TI acima de R$ 5.000, é necessário incluir uma justificativa técnica detalhada.
"""
            
            if monetary_value > 10000:
                response += """
Importante: Para compras acima de R$ 10.000, é necessário incluir:
- Justificativa detalhada da necessidade
- Análise de impacto no orçamento do centro de custo
- Aprovação da Diretoria Executiva
"""

            # Integrar informações financeiras se disponíveis
            if finance_data and not finance_data.startswith("Baseado nos dados financeiros disponíveis, não tenho informações"):
                # Extrair informações relevantes do finance_data
                if "Orçamento disponível:" in finance_data:
                    # Extrair a parte financeira relevante
                    finance_info = ""
                    
                    if "Há orçamento disponível para esta compra" in finance_data:
                        finance_info += "\n✅ Situação financeira: Compra viável dentro do orçamento disponível."
                    elif "Orçamento insuficiente" in finance_data:
                        finance_info += "\n❌ Situação financeira: Orçamento insuficiente para esta compra."
                        
                        # Adicionar recomendações se existirem
                        if "Recomendações alternativas:" in finance_data:
                            recommendations = finance_data.split("Recomendações alternativas:")[1]
                            if "Restrições específicas" in recommendations:
                                recommendations = recommendations.split("Restrições específicas")[0]
                            finance_info += "\n\nRecomendações financeiras:" + recommendations
                    
                    # Adicionar informação de orçamento disponível
                    if "Orçamento disponível: R$" in finance_data:
                        budget_line = finance_data.split("Orçamento disponível: R$")[1].split("\n")[0]
                        finance_info += f"\nOrçamento disponível: R${budget_line}"
                    
                    response += finance_info
                else:
                    # Caso não haja informações estruturadas como esperado
                    relevant_info = finance_data.replace("Baseado nos dados financeiros disponíveis", "Informações financeiras adicionais")
                    if "Você pode perguntar sobre" in relevant_info:
                        relevant_info = relevant_info.split("Você pode perguntar sobre")[0]
                    response += f"\n\n{relevant_info}"
        
        return response
    
    def answer(self, query):
        """Responde à pergunta com análise contextual inteligente."""
        query_lower = query.lower()
        
        # Simular processamento
        print("Processando consulta usando RAG... ", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        print(" concluído!")
        
        # Verificar se a consulta faz referência a itens anteriores
        if "ele" in query_lower or "isso" in query_lower or "essa compra" in query_lower or "este item" in query_lower:
            # Usar informações do contexto anterior
            if self.conversation_memory["last_item"]:
                query = query.replace("ele", self.conversation_memory["last_item"])
                query = query.replace("isso", self.conversation_memory["last_item"])
                query = query.replace("essa compra", f"compra de {self.conversation_memory['last_item']}")
                query = query.replace("este item", self.conversation_memory["last_item"])
                
                print(f"Detectada referência a item anterior: {self.conversation_memory['last_item']}")
        
        # Extrair entidades-chave da consulta
        monetary_value = self.extract_monetary_value(query)
        item_info = self.extract_item_type(query)
        
        # Se não encontrou valor na consulta atual, verificar se existe na memória
        if not monetary_value and self.conversation_memory["last_value"] and (
            "quanto tempo" in query_lower or 
            "quem aprova" in query_lower or
            "aprovação" in query_lower or
            "custo" in query_lower or
            "orçamento" in query_lower
        ):
            monetary_value = self.conversation_memory["last_value"]
            print(f"Usando valor monetário do contexto anterior: R$ {monetary_value:,.2f}")
        
        # Se não encontrou item na consulta atual, mas está perguntando sobre aprovação ou orçamento
        if not item_info and self.conversation_memory["last_item"] and (
            "quanto tempo" in query_lower or 
            "quem aprova" in query_lower or
            "aprovação" in query_lower or
            "orçamento" in query_lower or
            "centro de custo" in query_lower
        ):
            item_info = self.extract_item_type(f"compra de {self.conversation_memory['last_item']}")
            if item_info:
                print(f"Usando item do contexto anterior: {item_info['item']}")
        
        if monetary_value:
            print(f"Valor monetário identificado: R$ {monetary_value:,.2f}")
            # Salvar na memória
            self.conversation_memory["last_value"] = monetary_value
        
        if item_info:
            print(f"Item identificado: {item_info['item']} (Categoria: {item_info['categoria']})")
            if item_info['centro_custo']:
                print(f"Centro de custo: {item_info['centro_custo']}")
                # Salvar na memória
                self.conversation_memory["last_centro_custo"] = item_info['centro_custo']
            if item_info['proibido']:
                print("Alerta: Item identificado como proibido pela política")
            
            # Salvar item na memória
            self.conversation_memory["last_item"] = item_info['item']
        
        # Verificar se deve consultar o agente financeiro
        finance_response = None
        if self.should_consult_finance(query, item_info, monetary_value):
            print("Detectada necessidade de consulta financeira. Encaminhando para finance_agent...")
            
            # Criar uma consulta mais específica para o finance_agent
            if monetary_value and item_info and item_info['centro_custo']:
                finance_query = f"Verificar orçamento para compra de {item_info['item']} no valor de R$ {monetary_value} no centro de custo {item_info['centro_custo']}"
            elif monetary_value and item_info:
                finance_query = f"Verificar orçamento para compra de {item_info['item']} no valor de R$ {monetary_value}"
            elif monetary_value:
                finance_query = f"Verificar informações para compra no valor de R$ {monetary_value}"
            elif item_info and item_info['centro_custo']:
                finance_query = f"Qual o orçamento disponível para {item_info['centro_custo']}?"
            else:
                finance_query = query
            
            # Obter resposta do finance_agent
            finance_response = self.finance_agent.answer(finance_query)
        
        # Construir resposta inteligente e contextualizada
        response = self.build_contextual_response(query, item_info, monetary_value, finance_response)
        
        # Salvar interação no histórico
        self.conversation_memory["history"].append({
            "query": query,
            "item": item_info['item'] if item_info else None,
            "value": monetary_value,
            "response": response
        })
        
        return response

if __name__ == "__main__":
    # Iniciar assistente
    assistant = ProcurementAssistant()
    
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