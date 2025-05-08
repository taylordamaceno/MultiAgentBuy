# 🧠 Assistente de Compras Internas com Multi-Agent

Um assistente inteligente que utiliza múltiplos agentes especializados para responder perguntas sobre processos de compras e aprovações financeiras.

## 🚀 Guia Rápido

### Instalar e Executar (5 minutos)
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/MultiAgentBuy.git
cd MultiAgentBuy

# 2. Configure o ambiente
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure sua chave OpenAI
echo "OPENAI_API_KEY=sua-chave-da-openai" > .env

# 5. Execute o setup
python setup.py

# 6. Inicie o assistente
python main.py
```

## 💬 Como Usar

1. Após iniciar o programa com `python main.py`, digite suas perguntas no terminal.
2. Para ver exemplos de perguntas, digite `ajuda` quando solicitado.
3. Para encerrar, digite `sair`.

### 💡 Perguntas que o sistema responde:

**Políticas de Compras:**
- "Qual é o processo para comprar um software?"
- "Como solicitar uma compra de equipamento?"
- "Quais documentos preciso para pedir um notebook?"

**Orçamentos e Valores:**
- "Posso comprar um monitor de R$ 5.000?"
- "Qual o orçamento disponível para TI?"
- "Há verba disponível para treinamentos este mês?"

**Aprovações:**
- "Quem precisa aprovar uma compra de R$ 8.500?"
- "Qual o fluxo de aprovação para compras acima de R$ 10.000?"
- "Quanto tempo demora para aprovar uma compra de R$ 15.000?"

## 🔧 Solução de Problemas

| Problema | Solução |
|----------|---------|
| *"Erro: OPENAI_API_KEY não configurada!"* | Crie ou edite o arquivo `.env` e adicione: `OPENAI_API_KEY=sua-chave-aqui` |
| *"Nenhum embedding encontrado..."* | Execute primeiro o script de setup: `python setup.py` |
| *"ModuleNotFoundError"* | Verifique se executou `pip install -r requirements.txt` |
| *"Arquivo não encontrado"* | Certifique-se de estar no diretório correto e de ter executado `git clone` |

## 🔍 Como Funciona

O sistema utiliza três agentes especializados que trabalham juntos:

1. **🔍 RAG Agent:** Busca informações relevantes nos documentos usando RAG (Retrieval Augmented Generation)
2. **📋 Procurement Agent:** Especialista em regras e processos de compras
3. **💰 Finance Agent:** Especialista em orçamentos e aprovações financeiras

Um **Coordenador** central recebe suas perguntas, classifica o tipo (compras, finanças ou ambos), e encaminha para os agentes apropriados.

## 📂 Estrutura Simplificada

```
MultiAgentBuy/
├── main.py                # 👈 Ponto de entrada principal
├── setup.py              # 👈 Configuração inicial (execute primeiro!)
├── coordinator.py        # Controlador central
├── agents/               # Agentes especializados 
├── data/                 # Dados e embeddings
│   ├── raw/              # Documentos originais
│   ├── embeddings/       # Vetores para busca semântica
└── utils/                # Utilitários e processadores
```

## 📚 Para Desenvolvedores

### Fluxo de Dados
1. O usuário faz uma pergunta via `main.py`
2. O `coordinator.py` classifica e encaminha para os agentes
3. O `rag_agent.py` busca informações relevantes na base de conhecimento
4. Agentes especializados (`procurement_agent.py` e `finance_agent.py`) geram respostas
5. O coordenador combina as respostas e retorna ao usuário

### Processamento de Dados
- `setup.py` cria a estrutura inicial e processa os documentos
- Os documentos são divididos em chunks e transformados em embeddings
- Uma busca semântica encontra informações relevantes para cada pergunta

### Adicionando Novos Documentos
Para adicionar novos documentos:
1. Adicione o arquivo em `data/raw/`
2. Atualize os processadores em `utils/`
3. Execute `setup.py` novamente

## 📝 Licença


