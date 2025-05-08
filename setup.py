#!/usr/bin/env python3
"""
Script de inicialização do sistema.
Cria diretórios necessários, processa políticas e regras financeiras,
e gera embeddings para busca semântica.
"""

import os
import sys
import time
import json
from pathlib import Path
from utils.process_policy import process_policy
from utils.process_finance import process_finance
from colorama import init, Fore, Style

# Inicializa colorama para cores no terminal
init()

def verify_requirements():
    """Verifica se as dependências necessárias estão instaladas."""
    try:
        import numpy
        import faiss
        import openai
        from dotenv import load_dotenv
        import tqdm
        return True
    except ImportError as e:
        print(f"{Fore.RED}❌ Erro: Dependência faltando - {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Por favor, instale todas as dependências com:{Style.RESET_ALL}")
        print("pip install -r requirements.txt")
        return False

def verify_openai_key():
    """Verifica se a chave da API OpenAI está configurada."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print(f"{Fore.RED}❌ Erro: OPENAI_API_KEY não configurada!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Por favor, configure sua chave da OpenAI:{Style.RESET_ALL}")
        print("1. Crie um arquivo .env na raiz do projeto")
        print("2. Adicione: OPENAI_API_KEY=sua-chave-api")
        return False
    return True

def verify_source_files():
    """Verifica se os arquivos fonte necessários existem."""
    required_files = [
        Path('data/raw/politica.md'),
        Path('data/raw/finance_rules.json'),
        Path('config/rag_config.json')
    ]
    
    all_exist = True
    for file_path in required_files:
        if not file_path.exists():
            print(f"{Fore.RED}❌ Erro: Arquivo não encontrado - {file_path}{Style.RESET_ALL}")
            all_exist = False
    
    if not all_exist:
        print(f"{Fore.YELLOW}Verifique se a estrutura de diretórios está correta:{Style.RESET_ALL}")
        print("- data/raw/ deve conter politica.md e finance_rules.json")
        print("- config/ deve conter rag_config.json")
        return False
    
    return True

def create_directories():
    """Cria os diretórios necessários para o sistema."""
    dirs = ['data/chunks', 'data/embeddings', 'data/metadata']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"{Fore.GREEN}✅ Diretório criado: {dir_path}{Style.RESET_ALL}")

def run_with_progress(func, message):
    """Executa uma função com indicador de progresso."""
    print(f"{Fore.YELLOW}{message}...{Style.RESET_ALL}")
    start_time = time.time()
    result = func()
    elapsed = time.time() - start_time
    print(f"{Fore.GREEN}✅ Concluído em {elapsed:.2f} segundos!{Style.RESET_ALL}")
    return result

def setup():
    """Inicializa o sistema."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🔧 Inicialização do Assistente de Compras Internas{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Verificações iniciais
    print(f"\n{Fore.CYAN}🔍 Verificando dependências e arquivos...{Style.RESET_ALL}")
    
    if not verify_requirements():
        return False
    
    if not verify_openai_key():
        return False
    
    if not verify_source_files():
        return False
    
    try:
        # Criação de diretórios
        print(f"\n{Fore.CYAN}📁 Criando estrutura de diretórios...{Style.RESET_ALL}")
        create_directories()
        
        # Processamento de arquivos
        run_with_progress(process_policy, "📝 Processando política de compras")
        run_with_progress(process_finance, "💰 Processando regras financeiras")
        
        # Verificação final
        if len(os.listdir('data/embeddings')) > 0:
            print(f"\n{Fore.GREEN}🎉 Setup concluído com sucesso!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Para iniciar o assistente, execute:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}python main.py{Style.RESET_ALL}")
            return True
        else:
            print(f"\n{Fore.RED}⚠️ Aviso: Nenhum embedding foi gerado!{Style.RESET_ALL}")
            print(f"Verifique os logs acima para possíveis erros.")
            return False
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro durante o setup: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Dicas de solução:{Style.RESET_ALL}")
        print("1. Verifique se os arquivos em data/raw/ estão no formato correto")
        print("2. Confirme que sua chave da API OpenAI está correta e tem saldo")
        print("3. Verifique se o arquivo config/rag_config.json está correto")
        print("4. Execute com DEBUG=1 para mais detalhes: DEBUG=1 python setup.py")
        return False

if __name__ == "__main__":
    success = setup()
    if not success:
        sys.exit(1) 