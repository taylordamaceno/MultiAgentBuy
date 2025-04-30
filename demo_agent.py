import os
from dotenv import load_dotenv
import time

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

# Respostas pré-programadas para demonstração
DEMO_RESPONSES = {
    "monitor ultrawide": """
Com base na política de compras, monitores ultrawide não são aprovados para compra direta.

De acordo com a seção 2 (Tipos de Itens Permitidos para Compra), embora monitores estejam na categoria "Equipamentos de TI", monitores ultrawide específicos requerem aprovação especial da diretoria por estarem fora do padrão.

A política permite monitores de até 27 polegadas para designers, mas modelos ultrawide precisam de justificativa especial.
""",

    "monitor 34": """
Com base na política de compras, monitores de 34 polegadas não são aprovados para compra direta.

De acordo com a seção 2 (Tipos de Itens Permitidos para Compra), embora monitores estejam na categoria "Equipamentos de TI", monitores de 34 polegadas requerem aprovação especial da diretoria por estarem fora do padrão.

A política permite monitores de até 27 polegadas para designers, mas modelos maiores precisam de justificativa especial.
""",

    "cadeira ergonômica": """
Sim, você pode comprar uma cadeira ergonômica para seu home office.

Conforme a seção 2 da política de compras, itens de "Home Office" incluem cadeiras ergonômicas com uma restrição de valor de até R$ 2.000 por colaborador/ano, com aprovação do gestor.

Esta compra deve ser alocada ao centro de custo "Facilities – Home Office" conforme indicado na seção 3 da política.
""",

    "softwares de produtividade": """
De acordo com a seção 3 da política de compras, o centro de custo correto para a compra de softwares de produtividade é "TI - Ferramentas".

Esta informação está claramente definida na tabela de Centro de Custo da política.
""",
    
    "centro de custo software": """
De acordo com a seção 3 da política de compras, o centro de custo correto para a compra de softwares de produtividade é "TI - Ferramentas".

Esta informação está claramente definida na tabela de Centro de Custo da política.
""",

    "centro de custo monitor": """
De acordo com a seção 3 da política de compras, o centro de custo correto para a compra de um monitor para um colaborador de TI é "TI - Infraestrutura".

Os monitores são classificados como "Hardware de TI" na tabela de Centro de Custo da política.
""",

    "r$ 8.500": """
Para uma compra de R$ 8.500, o tempo de aprovação é de 3 dias úteis.

Conforme a seção 4 da política (Fluxo de Aprovação), compras entre R$ 2.001 e R$ 10.000 têm um prazo médio de aprovação de 3 dias úteis e requerem aprovação do gestor da área e do Financeiro.
""",

    "r$ 4.800": """
Para uma compra de R$ 4.800, o tempo de aprovação é de 3 dias úteis.

Conforme a seção 4 da política (Fluxo de Aprovação), compras entre R$ 2.001 e R$ 10.000 têm um prazo médio de aprovação de 3 dias úteis e requerem aprovação do gestor da área e do Financeiro.
""",

    "requisitar a compra de um notebook": """
Para requisitar a compra de um notebook, você deve seguir estas etapas segundo a seção 5 da política:

1. Preencher o formulário de requisição no sistema interno
2. Anexar cotação ou link do item
3. Informar centro de custo (TI - Infraestrutura para notebooks)
4. Enviar para aprovação via sistema
5. Aguardar validação e liberação pelo time de Compras

Adicionalmente, para equipamentos de TI como notebooks, você deve:
- Adicionar justificativa técnica
- Informar cargo e departamento do solicitante
""",

    "requisição de compras": """
O processo de requisição de compras, segundo a seção 5 da política, envolve as seguintes etapas:

1. Preencher o formulário de requisição no sistema interno
2. Anexar cotação ou link do item
3. Informar centro de custo apropriado
4. Enviar para aprovação via sistema
5. Aguardar validação e liberação pelo time de Compras

Para itens específicos como equipamentos de TI, há requisitos adicionais como justificativa técnica.
""",

    "monitor gamer": """
Não, você não pode comprar um monitor gamer pessoal e pedir reembolso pela empresa.

De acordo com a seção 6 da política (Itens Proibidos), equipamentos para uso fora do escopo corporativo não são permitidos. Um monitor gamer pessoal seria classificado como equipamento para uso pessoal, não corporativo.

Além disso, a seção 2 estabelece que apenas monitores para uso profissional são permitidos, com limites específicos de tamanho.
""",

    "camisa": """
Não, você não pode comprar uma camisa através da empresa.

Conforme a seção 6 da política (Itens Proibidos), itens de vestuário não relacionados a uniformes corporativos e presentes pessoais estão explicitamente listados como proibidos para compra.
""",

    "netflix": """
Não, você não pode comprar uma assinatura da Netflix.

De acordo com a seção 6 da política (Itens Proibidos), assinaturas de streaming estão explicitamente listadas como itens proibidos para compra pela empresa.
"""
}

class DemoAssistant:
    def __init__(self):
        self.policy = policy_content
    
    def answer(self, query):
        """Responde à pergunta com base em palavras-chave."""
        query_lower = query.lower()
        
        # Simular processamento
        print("Processando consulta usando RAG... ", end="", flush=True)
        for _ in range(3):
            time.sleep(0.5)
            print(".", end="", flush=True)
        print(" concluído!")
        
        # Verificar por palavras-chave nas respostas pré-programadas
        for keyword, response in DEMO_RESPONSES.items():
            if keyword.lower() in query_lower:
                return response
        
        # Resposta genérica para outras perguntas
        return """
Baseado na política de compras da empresa, não tenho informações específicas sobre essa consulta.

Por favor, reformule sua pergunta ou consulte diretamente o departamento de compras para obter orientações mais precisas sobre este caso específico.

Você pode perguntar sobre:
- Aprovação de compras de equipamentos (monitores, notebooks, cadeiras)
- Centros de custo para diferentes tipos de compra
- Prazos de aprovação baseados no valor
- Processo de requisição
- Itens proibidos
"""

if __name__ == "__main__":
    # Iniciar assistente
    assistant = DemoAssistant()
    
    # Interface de demonstração
    print("\n=== ASSISTENTE DE COMPRAS CORPORATIVAS ===")
    print("Demonstração de RAG (Retrieval Augmented Generation)")
    print("Consulte a política de compras da empresa")
    print("\nExemplos de perguntas para demonstração:")
    print("1. \"Posso comprar um monitor ultrawide de 34 polegadas para o meu time de desenvolvimento?\"")
    print("2. \"Qual é o centro de custo correto para a compra de um monitor para um novo colaborador de TI?\"") 
    print("3. \"Se o monitor custa R$ 4.800, em quanto tempo ele deve ser aprovado pelo fluxo de compras?\"")
    print("4. \"Quais são as etapas que preciso seguir para solicitar a compra de um notebook?\"")
    print("5. \"Posso comprar um monitor gamer pessoal e pedir reembolso pela empresa?\"")
    print("\nDigite 'sair' para encerrar\n")
    
    # Loop de conversa
    while True:
        query = input("\nSua pergunta: ")
        if query.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando demonstração. Obrigado!")
            break
        
        response = assistant.answer(query)
        print(f"\nAssistente: {response}") 