# 🧠 Assistente de Compras Internas com Multi-Agent

Este projeto é um **assistente inteligente de compras internas**, construído com uma abordagem **Multi-Agent**, que combina um agente de política e um agente financeiro.

## ✅ Objetivo

Permitir que usuários façam perguntas sobre as **regras, processos e viabilidade financeira de compras corporativas**, com respostas automáticas baseadas na política interna da empresa e nos dados orçamentários.

---

## 🧱 Estrutura do Sistema

A solução utiliza um sistema de múltiplos agentes especializados com integração por chamada interna:

### 1️⃣ Agente de Política (`procurement_agent.py`)
- **Ponto de entrada principal** do sistema
- Responde questões sobre as regras e processos de compras
- Baseado no arquivo `politica.md` que contém as diretrizes
- Chama o agente financeiro internamente quando detecta questões financeiras

### 2️⃣ Agente Financeiro (`finance_agent.py`)
- Chamado pelo procurement_agent quando necessário
- Gerencia informações orçamentárias e financeiras
- Verifica disponibilidade de recursos para compras
- Sugere alternativas para compras acima do orçamento
- Baseado nos dados de `finance_rules.json`

### 📝 Arquivos de Dados
- `politica.md` - Documento estruturado em Markdown com as políticas de compras
- `finance_rules.json` - Dados orçamentários e regras financeiras em formato JSON

---

## 🧠 O que é RAG e Como Funciona?

RAG (Retrieval Augmented Generation) é uma técnica que combina busca de informações com geração de texto para criar respostas mais precisas e contextualizadas. Vamos entender como funciona no nosso sistema:

### 1️⃣ O Problema que o RAG Resolve

Imagine que você pergunta: "Posso comprar um notebook de R$ 15.000?"

**Sem RAG:**
- O modelo teria que "adivinhar" a resposta
- Poderia inventar regras que não existem
- Não teria acesso ao contexto específico da sua empresa

**Com RAG:**
1. O sistema busca nos documentos da empresa
2. Encontra as regras relevantes sobre compras de notebooks
3. Localiza informações sobre aprovações acima de R$ 10.000
4. Gera uma resposta precisa baseada nessas informações

### 2️⃣ Como o RAG Funciona em 3 Passos

#### Passo 1: Divisão Inteligente (Chunking)
```
Documento Original:
"Compras acima de R$ 10.000 precisam de aprovação da diretoria..."

↓

Chunks:
- Chunk 1: "Compras acima de R$ 10.000..."
- Chunk 2: "Aprovação da diretoria..."
```

#### Passo 2: Busca Semântica
```
Pergunta: "Posso comprar um notebook de R$ 15.000?"

↓

Sistema busca chunks relevantes:
- Chunk sobre limites de aprovação
- Chunk sobre compras de equipamentos
- Chunk sobre processos de aprovação
```

#### Passo 3: Geração de Resposta
```
Chunks encontrados + Pergunta original
↓
Resposta contextualizada e precisa
```

### 3️⃣ Exemplo Prático

**Pergunta:** "Quero comprar uma cadeira ergonômica de R$ 1.800, há orçamento disponível?"

**Processo RAG:**
1. **Busca:**
   - Encontra chunk sobre mobiliário
   - Localiza regras de orçamento
   - Identifica centro de custo correto

2. **Contexto:**
   ```
   - Regra: "Mobiliário precisa de justificativa ergonômica"
   - Orçamento: "Facilities tem R$ 9.000 disponível"
   - Processo: "Aprovação automática até R$ 2.000"
   ```

3. **Resposta:**
   "Sim, você pode comprar a cadeira. O valor está dentro do limite de aprovação automática (R$ 2.000) e há orçamento disponível em Facilities (R$ 9.000). Lembre-se de incluir a justificativa ergonômica no pedido."

### 4️⃣ Benefícios do RAG

- **Precisão:** Respostas baseadas em documentos reais
- **Contexto:** Considera regras específicas da empresa
- **Atualização:** Fácil atualização de regras e processos
- **Transparência:** Respostas podem ser verificadas nas fontes
- **Consistência:** Mantém o tom e estilo da empresa

### 5️⃣ Exemplos de Perguntas que o RAG Melhora

1. **Pergunta:** "Qual o processo para comprar um software de R$ 8.500?"
   - RAG encontra regras específicas de software
   - Localiza processo de aprovação correto
   - Verifica requisitos de licenciamento

2. **Pergunta:** "Preciso de aprovação para um treinamento de R$ 20.000?"
   - RAG identifica regras de treinamento
   - Encontra limites de orçamento
   - Localiza processo de aprovação especial

3. **Pergunta:** "Como solicitar um monitor ultrawide?"
   - RAG encontra regras de equipamentos
   - Identifica centro de custo correto
   - Localiza processo de aprovação

---

## 🧠 Implementação RAG (Retrieval Augmented Generation)

O sistema implementa RAG para melhorar a precisão e relevância das respostas:

### 1️⃣ Processamento de Dados
- **Chunking Inteligente**:
  - Divisão do `politica.md` em seções e parágrafos
  - Divisão estruturada do `finance_rules.json`
  - Tamanho de chunk configurável (1000 caracteres com overlap de 200)

- **Embeddings**:
  - Geração via OpenAI ada-002
  - Armazenamento otimizado
  - Sistema de cache

- **Metadata**:
  - Seção e categoria
  - Nível de importância
  - Fonte e data
  - Keywords automáticas

### 2️⃣ Busca Semântica
- Índice FAISS para busca rápida
- Similaridade coseno
- Top-3 chunks mais relevantes
- Filtragem por metadata

### 3️⃣ Geração de Respostas
- Contexto enriquecido com chunks relevantes
- Sistema de prompt engineering
- Respostas baseadas em evidências
- Prevenção de alucinações

### 4️⃣ Arquivos de Implementação
- `rag_config.json` - Configurações do sistema RAG
- `process_policy.py` - Processamento do arquivo de política
- `process_finance.py` - Processamento do arquivo financeiro
- `generate_embeddings.py` - Geração de embeddings
- `rag_agent.py` - Agente principal com RAG

### 5️⃣ Diretórios de Dados
- `data/chunks/` - Chunks processados
- `data/embeddings/` - Embeddings gerados
- `data/metadata/` - Índices e metadata

---

## 🧠 Como os Agentes se Integram

O `procurement_agent` funciona como entrypoint principal. Quando ele identifica uma necessidade de avaliação financeira (ex: menção a valor, orçamento, etc.), ele chama internamente o `finance_agent` com os parâmetros relevantes.

### Fluxo de Processamento:
1. O usuário faz uma pergunta ao sistema
2. O `procurement_agent` analisa a consulta para responder sobre política
3. Se detectar um valor monetário ou palavras-chave financeiras:
   - Extrai o valor da compra e tipo de item da consulta
   - Chama o `finance_agent` com esses parâmetros
   - Recebe a análise financeira
   - Combina ambas as respostas em uma análise unificada

Assim, o usuário recebe uma resposta completa que considera tanto aspectos de política quanto de viabilidade financeira.

---

## 🚀 Como Usar

### Pré-requisitos
- Python 3.8+
- Dependências no arquivo `requirements.txt`

### Instalação
```bash
# Clonar o repositório
git clone <url-do-repositorio>

# Navegar até o diretório
cd multi_AI_agent_langchain

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais da OpenAI
```

### Execução

Para executar o sistema completo:
```bash
python procurement_agent.py
```

Para testar apenas o agente financeiro isoladamente:
```bash
python finance_agent.py
```

---

## 📊 Exemplos de Consultas

O sistema pode responder a perguntas como:

1. "Posso comprar um monitor ultrawide de 34 polegadas por R$ 5.000?"
2. "Qual é o centro de custo para a compra de um notebook de R$ 12.000?"
3. "Quais são as etapas para solicitar um treinamento de R$ 20.000?"
4. "Quero comprar uma cadeira ergonômica de R$ 1.800, há orçamento disponível?"
5. "Quem precisa aprovar uma compra de software de R$ 8.500?"

---

## 🔄 Evolução Futura

Planos para expansão do sistema:

- Integração com sistemas ERP para dados orçamentários em tempo real
- Adição de um agente de fornecedores para sugerir vendedores homologados
- Implementação de um agente de aprovação para acompanhar status de solicitações
- Interface web para acesso mais amigável

---

## 💼 Potencial em Ambiente Produtivo

Este projeto demonstra o conceito de multi-agentes cooperativos, mas em um ambiente produtivo real, o potencial é muito maior:

- **Integração com Sistemas Corporativos**: Os agentes poderiam consultar APIs e bases de dados reais da empresa (ERP, CRM, sistemas financeiros), mantendo a mesma lógica de cooperação e delegação.

- **Frameworks de Orquestração**: Com ferramentas como LangChain e similares, podemos orquestrar fluxos mais complexos, percorrendo diferentes ferramentas e fontes de dados conforme necessário.

- **Interfaces Amigáveis**: A integração com frontends como Slack, Microsoft Teams ou interfaces web personalizadas torna-se simples, permitindo que os colaboradores interajam com os agentes de forma natural em seus ambientes de trabalho.

- **Tomada de Decisão Assistida**: Os LLMs como base destes agentes permitem automação de análises complexas com esforço médio de implementação, liberando tempo de especialistas para tarefas que realmente exigem intervenção humana.

- **Escalabilidade**: Novos agentes especializados podem ser adicionados para expandir as capacidades do sistema (jurídico, RH, logística, compliance) sem redesenhar a arquitetura central.

Esta abordagem multi-agente representa um equilíbrio entre sistemas monolíticos simples e arquiteturas complexas, oferecendo uma via prática para implementar IA generativa em processos corporativos.

---

## 🌟 Explicação para Leigos: Multi-Agent em Ação

Imagine que você fez uma pergunta sobre comprar algo para empresa, como "Posso comprar um notebook de R$ 15.000?"

Em um assistente normal, você receberia apenas uma resposta básica sobre regras ou talvez um "não sei". Mas nosso sistema é mais esperto que isso!

### O que criamos?

Desenvolvemos um assistente inteligente que funciona como dois especialistas trabalhando juntos:

🧑‍⚖️ **Especialista em Regras (Agente de Política)**  
Este é o atendente principal que conhece todas as regras de compras da empresa:
- O que você pode ou não comprar
- Quem precisa aprovar
- Para qual departamento vai a cobrança
- Quais documentos são necessários

💰 **Especialista Financeiro (Agente Financeiro)**  
Este é o consultor financeiro que sabe:
- Se há dinheiro disponível no orçamento
- Quem é responsável pela verba
- Alternativas quando o valor excede o orçamento
- Sugestões para dividir compras grandes

### Como funciona na prática?

1. **Você faz uma pergunta única** ao sistema (ex: "Posso comprar um notebook de R$ 15.000?")

2. **O sistema identifica automaticamente** que você está perguntando sobre:
   - Um notebook (item de TI)
   - No valor de R$ 15.000 (valor alto)

3. **O especialista em regras analisa** sua solicitação:
   - "Sim, notebooks são permitidos"
   - "Precisa ser aprovado pela diretoria pois custa mais de R$ 10.000"
   - "Deve ser lançado no centro de custo de TI"

4. **Automaticamente, sem você perceber**, o sistema também consulta o especialista financeiro:
   - "Há orçamento disponível em TI?"
   - "R$ 15.000 excede algum limite?"
   - "Que alternativas existem?"

5. **Você recebe uma resposta completa** que combina os dois conhecimentos:
   - Parte sobre regras (se é permitido, quem aprova)
   - Parte sobre finanças (se há verba, alternativas)

O mais legal é que tudo isso acontece em segundos, com uma única pergunta sua, como se você tivesse consultado dois especialistas ao mesmo tempo!

### Benefício principal

Antes, você teria que:
1. Perguntar ao departamento de compras se pode comprar
2. Depois perguntar ao financeiro se há verba
3. Então voltar ao time de compras com a resposta

Agora, uma única pergunta ao assistente já traz todas as informações necessárias, economizando seu tempo e garantindo uma decisão mais informada.

---

## 📄 Licença

## 📂 Estrutura de Arquivos

O projeto contém os seguintes arquivos principais:

- **demo_agent.py**: Agente de demonstração simples que responde perguntas sobre política de compras usando respostas pré-programadas. Simula um sistema RAG básico para demonstrações.

- **procurement_agent.py**: Agente avançado para consultas sobre política de compras. Analisa detalhadamente as consultas do usuário para entender o tipo de item, valor monetário e outros contextos relevantes.

- **finance_agent.py**: Gerencia consultas relacionadas a orçamentos e finanças. Verifica disponibilidade orçamentária e fornece informações sobre fluxos de aprovação baseados no valor.

- **multi_agent.py**: Sistema coordenador que decide qual agente deve responder com base no tipo de pergunta, podendo combinar respostas quando necessário.

- **politica.md**: Documento contendo a política de compras da empresa em formato Markdown.

- **finance_rules.json**: Arquivo JSON com dados financeiros, incluindo informações sobre orçamentos, limites de aprovação e restrições.

Para executar o sistema, você pode escolher:

```bash
# Para o agente de demonstração simples:
python demo_agent.py

# Para o sistema multi-agente (combina política e finanças):
python multi_agent.py

# Para o agente de compras avançado:
python procurement_agent.py
```

