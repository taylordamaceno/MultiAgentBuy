import os
from dotenv import load_dotenv
import time
import json

# Carregar variáveis de ambiente
load_dotenv()

# Carregar regras financeiras do JSON
try:
    with open('finance_rules.json', 'r', encoding='utf-8') as file:
        FINANCE_RULES = json.load(file)
    print("Regras financeiras carregadas com sucesso.")
except Exception as e:
    print(f"Erro ao carregar regras financeiras: {str(e)}")
    FINANCE_RULES = {
        "orcamentos": [],
        "limites_aprovacao": []
    }

# Converter dados de orçamento para o formato usado internamente
BUDGET_DATA = {}
for item in FINANCE_RULES.get("orcamentos", []):
    BUDGET_DATA[item["centro_custo"]] = {
        "total_mensal": item["orcamento_mensal"],
        "gasto_atual": item["orcamento_mensal"] - item["disponivel"],
        "disponivel": item["disponivel"],
        "responsavel": item["responsavel"]
    }

# Respostas pré-programadas para demonstração
FINANCE_RESPONSES = {
    "orçamento ti infra": f"""
Atualmente, o centro de custo "TI – Infraestrutura" possui:
- Orçamento mensal: R$ {BUDGET_DATA.get("TI – Infraestrutura", {}).get("total_mensal", 0):,}
- Valor já utilizado: R$ {BUDGET_DATA.get("TI – Infraestrutura", {}).get("gasto_atual", 0):,}
- Disponível: R$ {BUDGET_DATA.get("TI – Infraestrutura", {}).get("disponivel", 0):,}

O responsável por este orçamento é {BUDGET_DATA.get("TI – Infraestrutura", {}).get("responsavel", "Não informado")}.
""",

    "orçamento ti ferramentas": f"""
Atualmente, o centro de custo "TI – Ferramentas" possui:
- Orçamento mensal: R$ {BUDGET_DATA.get("TI – Ferramentas", {}).get("total_mensal", 0):,}
- Valor já utilizado: R$ {BUDGET_DATA.get("TI – Ferramentas", {}).get("gasto_atual", 0):,}
- Disponível: R$ {BUDGET_DATA.get("TI – Ferramentas", {}).get("disponivel", 0):,}

O responsável por este orçamento é {BUDGET_DATA.get("TI – Ferramentas", {}).get("responsavel", "Não informado")}.
""",

    "orçamento rh": f"""
Atualmente, o centro de custo "RH – Desenvolvimento" possui:
- Orçamento mensal: R$ {BUDGET_DATA.get("RH – Desenvolvimento", {}).get("total_mensal", 0):,}
- Valor já utilizado: R$ {BUDGET_DATA.get("RH – Desenvolvimento", {}).get("gasto_atual", 0):,}
- Disponível: R$ {BUDGET_DATA.get("RH – Desenvolvimento", {}).get("disponivel", 0):,}

O responsável por este orçamento é {BUDGET_DATA.get("RH – Desenvolvimento", {}).get("responsavel", "Não informado")}.
""",

    "orçamento facilities": f"""
Atualmente, o centro de custo "Facilities" possui:
- Orçamento mensal: R$ {BUDGET_DATA.get("Facilities", {}).get("total_mensal", 0):,}
- Valor já utilizado: R$ {BUDGET_DATA.get("Facilities", {}).get("gasto_atual", 0):,}
- Disponível: R$ {BUDGET_DATA.get("Facilities", {}).get("disponivel", 0):,}

O responsável por este orçamento é {BUDGET_DATA.get("Facilities", {}).get("responsavel", "Não informado")}.
""",

    "orçamento home office": f"""
Atualmente, o centro de custo "Facilities - Home Office" possui:
- Orçamento mensal: R$ {BUDGET_DATA.get("Facilities - Home Office", {}).get("total_mensal", 0):,}
- Valor já utilizado: R$ {BUDGET_DATA.get("Facilities - Home Office", {}).get("gasto_atual", 0):,}
- Disponível: R$ {BUDGET_DATA.get("Facilities - Home Office", {}).get("disponivel", 0):,}

O responsável por este orçamento é {BUDGET_DATA.get("Facilities - Home Office", {}).get("responsavel", "Não informado")}.
""",

    "compra monitor 5000": """
Para uma compra de monitor no valor de R$ 5.000:

1. Verificação orçamentária: Esta compra pode ser alocada no centro de custo "TI – Infraestrutura".
2. Status atual: Há orçamento disponível no centro de custo (R$ 12.500).
3. Fluxo de aprovação: Por estar entre R$ 2.001 e R$ 10.000, requer aprovação do gestor da área e do Financeiro.
4. Timeline estimado: 3 dias úteis para aprovação completa.

Recomendação: Proceda com a requisição no sistema, informando o centro de custo correto e anexando a cotação do fornecedor.
""",

    "notebook 15000": """
Para uma compra de notebook no valor de R$ 15.000:

1. Verificação orçamentária: Esta compra seria alocada no centro de custo "TI – Infraestrutura".
2. Status atual: Não há orçamento disponível suficiente (apenas R$ 12.500 disponíveis de R$ 15.000 necessários).
3. Fluxo de aprovação: Por estar acima de R$ 10.000, requer aprovação do gestor da área, Financeiro e Diretoria Executiva.
4. Timeline estimado: 7 dias úteis para aprovação completa.

⚠️ Alerta de orçamento: Esta compra excede o orçamento disponível para o centro de custo.
⚠️ Alerta de restrição: Equipamentos acima de R$ 10.000 requerem cotação de 3 fornecedores e aprovação técnica.

Recomendações alternativas:
- Verificar se há opções mais econômicas que atendam às necessidades técnicas
- Solicitar transferência orçamentária de outro centro de custo (requer aprovação da diretoria)
- Reagendar a compra para o próximo ciclo orçamentário
- Considerar dividir a compra em partes (notebook básico + upgrades separados)
""",

    "treinamento 20000": """
Para um treinamento de equipe no valor de R$ 20.000:

1. Verificação orçamentária: Esta compra seria alocada no centro de custo "RH – Desenvolvimento".
2. Status atual: Orçamento disponível insuficiente (apenas R$ 5.000 disponíveis).
3. Fluxo de aprovação: Por estar acima de R$ 10.000, requereria aprovação do gestor da área, Financeiro e Diretoria Executiva.

⚠️ Alerta de orçamento: Esta compra excede significativamente o orçamento disponível para o centro de custo.

Recomendações alternativas:
- Dividir o treinamento em módulos menores ao longo do ano
- Adiar parte do treinamento para o próximo ciclo orçamentário
- Solicitar transferência orçamentária de outro centro de custo (requer aprovação da diretoria)
- Negociar desconto ou plano de pagamento estendido com o fornecedor
""",

    "quem aprova 6000": """
Para uma compra de R$ 6.000:

O fluxo de aprovação requer:
1. Gestor direto da área requisitante
2. Departamento Financeiro

Como está na faixa entre R$ 2.001 e R$ 10.000, não é necessária aprovação da Diretoria Executiva.

Tempo estimado para aprovação: 3 dias úteis
""",

    "quem aprova 12000": """
Para uma compra de R$ 12.000:

O fluxo de aprovação requer:
1. Gestor direto da área requisitante
2. Departamento Financeiro
3. Diretoria Executiva

Como está acima de R$ 10.000, é necessária a aprovação completa, incluindo a Diretoria.

Tempo estimado para aprovação: 7 dias úteis

Atenção: Acima de R$ 10.000, a solicitação deve incluir:
- Justificativa detalhada da necessidade
- Análise de impacto no orçamento do centro de custo
"""
}

class FinanceAssistant:
    def __init__(self):
        self.finance_rules = FINANCE_RULES
        self.budget_data = BUDGET_DATA
    
    def get_approval_info(self, value):
        """Retorna informações de aprovação com base no valor."""
        for limit in self.finance_rules.get("limites_aprovacao", []):
            if "Até R$ 2.000" in limit["faixa"] and value <= 2000:
                return limit
            elif "R$ 2.001 a R$ 10.000" in limit["faixa"] and 2001 <= value <= 10000:
                return limit
            elif "Acima de R$ 10.000" in limit["faixa"] and value > 10000:
                return limit
        return None
    
    def check_budget(self, centro_custo, valor):
        """Verifica se há orçamento disponível para a compra."""
        if centro_custo in self.budget_data:
            disponivel = self.budget_data[centro_custo]["disponivel"]
            return {
                "centro_custo": centro_custo,
                "disponivel": disponivel,
                "valor_solicitado": valor,
                "suficiente": disponivel >= valor,
                "diferenca": disponivel - valor,
                "percentual_consumo": (valor / disponivel) * 100 if disponivel > 0 else float('inf')
            }
        return None
    
    def get_restrictions(self, item_type, valor):
        """Retorna restrições específicas baseadas no tipo de item e valor."""
        restrictions = []
        
        # Verificar restrições específicas para o valor
        if valor > 10000:
            for restriction in self.finance_rules.get("restricoes_especificas", []):
                if "Equipamentos acima de R$ 10.000" in restriction["tipo"]:
                    restrictions.extend(restriction["restricoes"])
        
        # Outras verificações específicas podem ser adicionadas aqui
        
        return restrictions
    
    def get_alternative_recommendations(self, budget_check):
        """Gera recomendações alternativas baseadas no status orçamentário."""
        recommendations = []
        
        if not budget_check["suficiente"]:
            # Verificar valor pendente
            faltante = abs(budget_check["diferenca"])
            
            # Recomendações para quando não há orçamento suficiente
            recommendations.append("Reagendar a compra para o próximo ciclo orçamentário")
            recommendations.append("Solicitar transferência orçamentária de outro centro de custo (requer aprovação da diretoria)")
            
            # Se o valor faltante for pequeno em relação ao solicitado
            if faltante <= budget_check["valor_solicitado"] * 0.3:  # Se falta menos de 30%
                recommendations.append("Verificar se há opções mais econômicas que atendam às necessidades")
            
            # Se o valor for muito grande
            if budget_check["valor_solicitado"] > 5000:
                recommendations.append("Considerar dividir a compra em partes menores distribuídas ao longo do tempo")
                recommendations.append("Negociar desconto ou plano de pagamento estendido com o fornecedor")
        
        return recommendations
    
    def answer(self, query):
        """Responde à pergunta com base em palavras-chave financeiras e regras de negócio."""
        query_lower = query.lower()
        
        # Simular processamento
        print("Consultando dados financeiros... ", end="", flush=True)
        for _ in range(3):
            time.sleep(0.5)
            print(".", end="", flush=True)
        print(" concluído!")
        
        # Verificar por palavras-chave nas respostas pré-programadas
        for keyword, response in FINANCE_RESPONSES.items():
            if keyword.lower() in query_lower:
                return response
        
        # Verificar se está perguntando sobre orçamento de algum centro de custo
        if "orçamento" in query_lower or "disponível" in query_lower or "disponivel" in query_lower:
            for centro, dados in self.budget_data.items():
                centro_lower = centro.lower()
                if centro_lower in query_lower:
                    return f"""
Atualmente, o centro de custo "{centro}" possui:
- Orçamento mensal: R$ {dados["total_mensal"]:,}
- Valor já utilizado: R$ {dados["gasto_atual"]:,}
- Disponível: R$ {dados["disponivel"]:,}

O responsável por este orçamento é {dados["responsavel"]}.
"""
        
        # Extrair possível valor monetário da consulta
        import re
        valores = re.findall(r'r\$\s*(\d+[\.,]?\d*)|(\d+)[.,]?(\d*)\s*mil', query_lower)
        valor = None
        
        if valores:
            try:
                if "mil" in query_lower:
                    # Tratar expressões como "5 mil"
                    for match in valores:
                        if match[1]:  # Se capturou o número antes de "mil"
                            valor = float(match[1]) * 1000
                            break
                elif valores[0][0]:  # Formato R$ X
                    valor = float(valores[0][0].replace('.', '').replace(',', '.'))
                else:  # Outros formatos
                    valor_str = ''.join(filter(None, valores[0][1:]))
                    if valor_str:
                        valor = float(valor_str)
            except:
                pass
        
        # Se conseguiu identificar um valor
        if valor:
            # Buscar aprovações necessárias para este valor
            approval_info = self.get_approval_info(valor)
            
            # Tentar identificar o centro de custo
            centro_custo = None
            for keyword, centro in {
                "ti": "TI – Infraestrutura",
                "infraestrutura": "TI – Infraestrutura",
                "monitor": "TI – Infraestrutura",
                "notebook": "TI – Infraestrutura",
                "computador": "TI – Infraestrutura",
                "software": "TI – Ferramentas",
                "ferramentas": "TI – Ferramentas",
                "licença": "TI – Ferramentas",
                "rh": "RH – Desenvolvimento",
                "treinamento": "RH – Desenvolvimento",
                "curso": "RH – Desenvolvimento",
                "facilities": "Facilities",
                "escritório": "Facilities",
                "mobiliário": "Facilities",
                "home office": "Facilities - Home Office",
                "home-office": "Facilities - Home Office"
            }.items():
                if keyword in query_lower:
                    centro_custo = centro
                    break
            
            # Verificar orçamento disponível
            budget_check = None
            if centro_custo:
                budget_check = self.check_budget(centro_custo, valor)
            
            # Construir resposta
            response = f"Para uma compra no valor de R$ {valor:,.2f}:\n\n"
            
            if approval_info:
                response += f"Fluxo de aprovação: {approval_info['aprovacao']}\n"
                response += f"Tempo estimado para aprovação: {approval_info['dias_uteis']} dias úteis\n\n"
            
            if budget_check:
                response += f"Centro de custo: {budget_check['centro_custo']}\n"
                response += f"Orçamento disponível: R$ {budget_check['disponivel']:,.2f}\n"
                
                if budget_check['suficiente']:
                    response += "✅ Há orçamento disponível para esta compra.\n"
                    
                    # Verificar se consome grande parte do orçamento
                    if budget_check['percentual_consumo'] > 80:
                        response += f"⚠️ Alerta: Esta compra consumirá {budget_check['percentual_consumo']:.1f}% do orçamento disponível.\n"
                else:
                    response += f"❌ Orçamento insuficiente. Faltam R$ {abs(budget_check['diferenca']):,.2f}.\n"
                    
                    # Obter recomendações alternativas
                    recommendations = self.get_alternative_recommendations(budget_check)
                    if recommendations:
                        response += "\nRecomendações alternativas:\n"
                        for rec in recommendations:
                            response += f"- {rec}\n"
            
            # Verificar restrições específicas
            restrictions = self.get_restrictions("genérico", valor)
            if restrictions:
                response += "\nRestrições específicas para esta compra:\n"
                for restriction in restrictions:
                    response += f"- {restriction}\n"
            
            return response
        
        # Resposta genérica para outras perguntas
        return """
Baseado nos dados financeiros disponíveis, não tenho informações específicas sobre essa consulta.

Você pode perguntar sobre:
- Orçamento disponível por centro de custo
- Verificação de viabilidade financeira de uma compra
- Quem deve aprovar uma compra de determinado valor
- Alternativas para compras acima do orçamento disponível
- Previsão de tempo para aprovação financeira
"""

if __name__ == "__main__":
    # Iniciar assistente
    assistant = FinanceAssistant()
    
    # Interface de demonstração
    print("\n=== ASSISTENTE FINANCEIRO DE COMPRAS ===")
    print("Demonstração de Agente Financeiro")
    print("Consulte informações orçamentárias e financeiras de compras")
    print("\nExemplos de perguntas para demonstração:")
    print("1. \"Qual o orçamento disponível para TI Infraestrutura?\"")
    print("2. \"Posso comprar um monitor de R$ 5.000 para minha equipe?\"") 
    print("3. \"Quem precisa aprovar uma compra de R$ 12.000?\"")
    print("4. \"Quero fazer um treinamento para equipe que custa R$ 20.000, é possível?\"")
    print("5. \"Qual o orçamento disponível para compras de home office?\"")
    print("\nDigite 'sair' para encerrar\n")
    
    # Loop de conversa
    while True:
        query = input("\nSua pergunta: ")
        if query.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando demonstração. Obrigado!")
            break
        
        response = assistant.answer(query)
        print(f"\nAssistente Financeiro: {response}") 