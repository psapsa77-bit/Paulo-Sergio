#!/usr/bin/env python3
"""
Exemplos práticos de uso do Robô FGTS Digital

Este arquivo contém diferentes exemplos de como usar o robô
em diferentes cenários.
"""
import sys
from pathlib import Path
import asyncio

# Adicionar diretório atual ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent))

from robo_fgts import RoboFGTS


def exemplo_basico():
    """
    Exemplo 1: Uso básico com configurações padrão do .env
    """
    print("\n" + "="*60)
    print("EXEMPLO 1: Uso Básico")
    print("="*60)

    # Criar instância do robô (usa configurações do .env)
    robo = RoboFGTS()

    # Lista de CNPJs para processar
    cnpjs = [
        '12345678000190',
        '98765432000110'
    ]

    # Processar
    print(f"\nProcessando {len(cnpjs)} empresas...")
    sucesso = robo.processar_clientes(cnpjs)

    if sucesso:
        print("\n✓ Processamento concluído com sucesso!")
    else:
        print("\n✗ Falha no processamento")


def exemplo_customizado():
    """
    Exemplo 2: Uso com configurações personalizadas
    """
    print("\n" + "="*60)
    print("EXEMPLO 2: Configuração Personalizada")
    print("="*60)

    # Criar instância com configurações específicas
    robo = RoboFGTS(
        cert_path='certificados/meu_certificado.pfx',
        cert_password='minha_senha_secreta',
        headless=True  # Modo headless (sem interface gráfica)
    )

    # Processar uma única empresa
    cnpjs = ['12345678000190']

    print(f"\nProcessando 1 empresa em modo headless...")
    sucesso = robo.processar_clientes(cnpjs)

    if sucesso:
        print("\n✓ Processamento concluído com sucesso!")


def exemplo_arquivo_cnpjs():
    """
    Exemplo 3: Ler CNPJs de um arquivo
    """
    print("\n" + "="*60)
    print("EXEMPLO 3: Ler CNPJs de Arquivo")
    print("="*60)

    # Ler CNPJs de um arquivo
    def ler_cnpjs(arquivo):
        with open(arquivo, 'r') as f:
            return [
                linha.strip()
                for linha in f
                if linha.strip() and not linha.strip().startswith('#')
            ]

    try:
        cnpjs = ler_cnpjs('lista_clientes.txt')
        print(f"\n{len(cnpjs)} CNPJs carregados do arquivo")

        # Processar
        robo = RoboFGTS()
        sucesso = robo.processar_clientes(cnpjs)

        if sucesso:
            print("\n✓ Processamento concluído!")

    except FileNotFoundError:
        print("\n✗ Arquivo 'lista_clientes.txt' não encontrado")
        print("Crie o arquivo com um CNPJ por linha")


async def exemplo_assincrono():
    """
    Exemplo 4: Uso assíncrono para melhor performance
    """
    print("\n" + "="*60)
    print("EXEMPLO 4: Processamento Assíncrono")
    print("="*60)

    # Criar instância
    robo = RoboFGTS(headless=True)

    # Lista de CNPJs
    cnpjs = [
        '12345678000190',
        '98765432000110',
        '11122233000144'
    ]

    print(f"\nProcessando {len(cnpjs)} empresas de forma assíncrona...")

    # Processar de forma assíncrona
    sucesso = await robo.processar_clientes_async(cnpjs)

    if sucesso:
        print("\n✓ Processamento assíncrono concluído!")


def exemplo_com_tratamento_erro():
    """
    Exemplo 5: Uso com tratamento completo de erros
    """
    print("\n" + "="*60)
    print("EXEMPLO 5: Com Tratamento de Erros")
    print("="*60)

    try:
        # Criar robô
        robo = RoboFGTS()

        # Validar certificado antes de processar
        if not robo._validar_certificado():
            raise Exception("Certificado inválido")

        # Lista de CNPJs
        cnpjs = ['12345678000190']

        # Processar com tratamento de erro
        print("\nIniciando processamento...")
        sucesso = robo.processar_clientes(cnpjs)

        if sucesso:
            print("\n✓ Processamento bem-sucedido!")
            print(f"✓ Verifique os resultados em: {robo.config.RESULTS_DIR}")
        else:
            print("\n✗ Processamento falhou")
            print(f"✗ Verifique os logs em: {robo.config.LOGS_DIR}")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário")

    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")
        print("Verifique suas configurações e tente novamente")


def exemplo_batch_processing():
    """
    Exemplo 6: Processamento em lote com múltiplas execuções
    """
    print("\n" + "="*60)
    print("EXEMPLO 6: Processamento em Lote")
    print("="*60)

    # Dividir CNPJs em lotes
    todos_cnpjs = [
        '12345678000190',
        '98765432000110',
        '11122233000144',
        '44455566000177',
        '77788899000100'
    ]

    tamanho_lote = 2
    lotes = [
        todos_cnpjs[i:i+tamanho_lote]
        for i in range(0, len(todos_cnpjs), tamanho_lote)
    ]

    print(f"\nProcessando {len(todos_cnpjs)} CNPJs em {len(lotes)} lotes")

    # Processar cada lote
    robo = RoboFGTS()

    for i, lote in enumerate(lotes, 1):
        print(f"\n--- Processando Lote {i}/{len(lotes)} ---")
        print(f"CNPJs: {', '.join(lote)}")

        sucesso = robo.processar_clientes(lote)

        if sucesso:
            print(f"✓ Lote {i} concluído")
        else:
            print(f"✗ Lote {i} falhou")

        # Aguardar entre lotes (opcional)
        import time
        if i < len(lotes):
            print("Aguardando 5 segundos antes do próximo lote...")
            time.sleep(5)


def menu_exemplos():
    """Menu interativo para escolher exemplo"""
    print("\n" + "="*60)
    print("ROBÔ FGTS DIGITAL - EXEMPLOS DE USO")
    print("="*60)

    print("\nEscolha um exemplo:")
    print("1. Uso Básico")
    print("2. Configuração Personalizada")
    print("3. Ler CNPJs de Arquivo")
    print("4. Processamento Assíncrono")
    print("5. Com Tratamento de Erros")
    print("6. Processamento em Lote")
    print("0. Sair")

    escolha = input("\nOpção: ").strip()

    exemplos = {
        '1': exemplo_basico,
        '2': exemplo_customizado,
        '3': exemplo_arquivo_cnpjs,
        '4': lambda: asyncio.run(exemplo_assincrono()),
        '5': exemplo_com_tratamento_erro,
        '6': exemplo_batch_processing
    }

    if escolha in exemplos:
        exemplos[escolha]()
    elif escolha == '0':
        print("\nAté logo!")
    else:
        print("\n✗ Opção inválida")


if __name__ == "__main__":
    # Executar menu interativo
    menu_exemplos()

    # Ou executar um exemplo específico diretamente:
    # exemplo_basico()
    # exemplo_customizado()
    # exemplo_com_tratamento_erro()
