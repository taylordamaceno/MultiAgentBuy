"""
Agente especializado em questões financeiras.
Responsável por responder perguntas sobre orçamentos e aprovações financeiras.
"""

import json
import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import time

# Inicializa o cliente OpenAI
client = OpenAI()

# Carregar variáveis de ambiente
load_dotenv()

# Carregar regras financeiras do JSON
try:
    with open('data/raw/finance_rules.json', 'r', encoding='utf-8') as file:
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

class FinanceAgent:
    """Agente especializado em questões financeiras."""
    
    def __init__(self):
        """Inicializa o agente financeiro."""
        self.system_prompt = """Você é um especialista em finanças corporativas.
        Sua função é responder perguntas sobre orçamentos, aprovações e regras financeiras.
        Seja claro, conciso e profissional em suas respostas.
        Sempre mencione a fonte das informações quando disponível."""
        
        # Carrega regras financeiras
        self.finance_rules = self._load_finance_rules()
    
    def _load_finance_rules(self) -> Dict:
        """Carrega regras financeiras do arquivo JSON."""
        try:
            with open('data/raw/finance_rules.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar regras financeiras: {e}")
            return {
                "orcamentos": [],
                "limites_aprovacao": []
            }
    
    def _extract_amount(self, text: str) -> float:
        """Extrai valor monetário do texto usando OpenAI."""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extraia apenas o valor monetário do texto. Retorne apenas o número."},
                    {"role": "user", "content": text}
                ]
            )
            amount = float(response.choices[0].message.content.strip())
            return amount
        except:
            return 0.0
    
    def _get_budget_info(self, amount: float, department: str = None) -> str:
        """Verifica informações de orçamento com base no valor e departamento."""
        # Verifica se o valor excede o orçamento total disponível
        total_budget = sum(budget["disponivel"] for budget in BUDGET_DATA.values())
        if amount > total_budget:
            return f"⚠️ Alerta: O valor de R$ {amount:,.2f} excede o orçamento total disponível (R$ {total_budget:,.2f})."
        
        # Se for especificado um departamento, verifica o orçamento específico
        if department and department in BUDGET_DATA:
            available = BUDGET_DATA[department]["disponivel"]
            if amount > available:
                return f"⚠️ Alerta: O valor de R$ {amount:,.2f} excede o orçamento disponível para {department} (R$ {available:,.2f})."
            else:
                return f"✅ O departamento {department} possui orçamento disponível (R$ {available:,.2f}) para esta compra de R$ {amount:,.2f}."
        
        # Sugere departamentos com orçamento suficiente
        suitable_depts = [dept for dept, data in BUDGET_DATA.items() if data["disponivel"] >= amount]
        if suitable_depts:
            return f"💡 Os seguintes departamentos possuem orçamento disponível para esta compra de R$ {amount:,.2f}: {', '.join(suitable_depts)}."
        else:
            return f"⚠️ Nenhum departamento possui orçamento disponível para o valor solicitado (R$ {amount:,.2f})."
    
    def answer(self, question: str, context: List[Dict]) -> str:
        """
        Gera uma resposta para a pergunta usando o contexto fornecido.
        
        Args:
            question: A pergunta do usuário
            context: Lista de chunks relevantes encontrados pelo RAG
            
        Returns:
            str: Resposta gerada
        """
        # Checa respostas pré-definidas para demonstração
        for key, response in FINANCE_RESPONSES.items():
            if key.lower() in question.lower():
                return response
        
        # Extrai valor monetário se presente na pergunta
        amount = self._extract_amount(question)
        
        if not context:
            # Se não tiver contexto mas tiver valor monetário, tenta gerar uma resposta básica
            if amount > 0:
                budget_info = self._get_budget_info(amount)
                approval_info = ""
                
                for threshold in self.finance_rules.get("limites_aprovacao", []):
                    min_val = threshold.get("valor_minimo", 0)
                    max_val = threshold.get("valor_maximo", float("inf"))
                    
                    if min_val <= amount <= max_val:
                        approval_info = f"""
                        Para uma compra de R$ {amount:,.2f}:
                        
                        Fluxo de aprovação:
                        {', '.join(threshold.get("aprovadores", []))}
                        
                        Tempo estimado: {threshold.get("tempo_estimado", "Não especificado")}
                        """
                        break
                
                if approval_info:
                    return budget_info + "\n\n" + approval_info
                else:
                    return budget_info
                    
            return "Desculpe, não encontrei informações financeiras relevantes para responder sua pergunta."
        
        # Prepara o contexto
        context_text = "\n\n".join([
            f"Conteúdo: {chunk['content']}\n"
            f"Fonte: {chunk['metadata']['source']}\n"
            f"Seção: {chunk['metadata']['section'] if 'section' in chunk['metadata'] else ''}"
            for chunk in context
        ])
        
        # Adiciona informação de orçamento se tiver um valor monetário
        if amount > 0:
            budget_info = self._get_budget_info(amount)
            context_text += f"\n\nInformação de Orçamento:\n{budget_info}"
        
        # Cria o prompt
        prompt = f"""Com base nas seguintes informações financeiras, responda à pergunta do usuário.
        Seja objetivo e direto, apresentando valores e regras claramente.
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
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta sobre finanças."

if __name__ == "__main__":
    # Iniciar assistente
    assistant = FinanceAgent()
    
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
        
        response = assistant.answer(query, [])
        print(f"\nAssistente Financeiro: {response}") 