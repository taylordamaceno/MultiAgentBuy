#!/usr/bin/env python3
"""
Ponto de entrada principal do Assistente de Compras Internas.
Este arquivo fornece uma interface simples para interagir com o sistema.
"""

from coordinator import Coordinator
import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Inicializa colorama para cores no terminal
init()

def check_setup_done():
    """Verifica se o setup foi executado corretamente."""
    if not os.path.exists('data/embeddings') or not os.listdir('data/embeddings'):
        print(f"{Fore.YELLOW}⚠️  Aviso: Não foram encontrados embeddings!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Parece que o setup inicial não foi executado. Execute primeiro:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}    python setup.py{Style.RESET_ALL}")
        response = input("\nDeseja continuar mesmo assim? (s/N): ").strip().lower()
        if response != 's':
            print(f"{Fore.CYAN}Encerrando. Execute 'python setup.py' e tente novamente.{Style.RESET_ALL}")
            sys.exit(0)

def show_examples():
    """Mostra exemplos de perguntas que o usuário pode fazer."""
    print(f"\n{Fore.GREEN}📚 Exemplos de perguntas:{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Políticas de Compras:{Style.RESET_ALL}")
    print("- Qual é o processo para comprar um software?")
    print("- Quais documentos preciso para solicitar um notebook?")
    print("- Posso comprar equipamentos para home office?")
    
    print(f"\n{Fore.CYAN}Orçamentos e Valores:{Style.RESET_ALL}")
    print("- Posso comprar um monitor de R$ 5.000?")
    print("- Qual o orçamento disponível para o departamento de TI?")
    print("- Há verba disponível para treinamentos este mês?")
    
    print(f"\n{Fore.CYAN}Aprovações:{Style.RESET_ALL}")
    print("- Quem precisa aprovar uma compra de R$ 8.500?")
    print("- Qual o fluxo de aprovação para compras acima de R$ 10.000?")
    print("- Quanto tempo demora para aprovar uma compra de R$ 15.000?")

def show_help():
    """Mostra ajuda sobre os comandos disponíveis."""
    print(f"\n{Fore.GREEN}🔍 Comandos disponíveis:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}ajuda{Style.RESET_ALL}: Mostra esta mensagem de ajuda")
    print(f"{Fore.CYAN}exemplos{Style.RESET_ALL}: Mostra exemplos de perguntas")
    print(f"{Fore.CYAN}sair{Style.RESET_ALL}: Encerra o programa")

def main():
    # Carrega variáveis de ambiente
    load_dotenv()
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🤖 Assistente de Compras Internas com Multi-Agent{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Verifica API key
    if not os.getenv('OPENAI_API_KEY'):
        print(f"\n{Fore.RED}❌ Erro: OPENAI_API_KEY não configurada!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Por favor, configure sua chave da OpenAI:{Style.RESET_ALL}")
        print("1. Crie um arquivo .env na raiz do projeto")
        print("2. Adicione: OPENAI_API_KEY=sua-chave-api")
        return
    
    # Verifica se o setup foi executado
    check_setup_done()
    
    try:
        print(f"\n{Fore.YELLOW}Inicializando agentes...{Style.RESET_ALL}")
        # Inicializa o coordenador
        coordinator = Coordinator()
        print(f"{Fore.GREEN}✅ Sistema pronto!{Style.RESET_ALL}")
        
        # Interface do usuário
        print(f"\n{Fore.YELLOW}💬 Faça suas perguntas sobre políticas de compras e orçamentos.{Style.RESET_ALL}")
        print(f"Digite '{Fore.CYAN}ajuda{Style.RESET_ALL}' para ver os comandos disponíveis.")
        print(f"Digite '{Fore.CYAN}exemplos{Style.RESET_ALL}' para ver exemplos de perguntas.")
        print(f"Digite '{Fore.CYAN}sair{Style.RESET_ALL}' para encerrar.")
        
        while True:
            pergunta = input(f"\n{Fore.GREEN}📝 Sua pergunta: {Style.RESET_ALL}").strip()
            
            if not pergunta:
                continue
                
            comando = pergunta.lower()
            
            if comando == 'sair':
                print(f"\n{Fore.CYAN}👋 Até logo!{Style.RESET_ALL}")
                break
                
            if comando == 'ajuda':
                show_help()
                continue
                
            if comando == 'exemplos':
                show_examples()
                continue
            
            try:
                # Processando...
                print(f"{Fore.YELLOW}⏳ Processando sua pergunta...{Style.RESET_ALL}")
                
                # Processa a pergunta
                resposta = coordinator.process_question(pergunta)
                
                # Exibe a resposta com formatação
                print(f"\n{Fore.CYAN}💡 Resposta:{Style.RESET_ALL}")
                print(f"{resposta}")
                
            except Exception as e:
                print(f"\n{Fore.RED}❌ Erro ao processar pergunta: {str(e)}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Por favor, verifique se todas as dependências estão instaladas:{Style.RESET_ALL}")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main() 