#!/usr/bin/env python3
"""
Script para testar conexão com o Portal FGTS Digital

Este script verifica se o robô consegue acessar o portal e identifica problemas.
"""
import sys
import asyncio
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

import config
from playwright.async_api import async_playwright


async def testar_acesso_portal():
    """Testa acesso ao portal FGTS"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║      🔍 TESTE DE CONEXÃO - PORTAL FGTS DIGITAL 🔍           ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    browser = None
    context = None

    try:
        print("📌 Teste 1: Verificando configurações...")
        print(f"   URL configurada: {config.FGTS_URL_LOGIN}")
        print(f"   Timeout: {config.BROWSER_TIMEOUT}ms")
        print(f"   Modo headless: {config.HEADLESS}")
        print("   ✓ Configurações OK")
        print()

        print("📌 Teste 2: Iniciando navegador...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Sempre visual para teste
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )
        print("   ✓ Navegador iniciado")
        print()

        print("📌 Teste 3: Criando contexto do navegador...")
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )
        page = await context.new_page()
        print("   ✓ Contexto criado")
        print()

        print("📌 Teste 4: Acessando portal FGTS...")
        print(f"   Tentando acessar: {config.FGTS_URL_LOGIN}")

        try:
            response = await page.goto(
                config.FGTS_URL_LOGIN,
                wait_until="networkidle",
                timeout=60000
            )

            if response:
                status = response.status
                print(f"   Status HTTP: {status}")

                if status == 200:
                    print("   ✓ Portal acessado com sucesso!")
                    print()
                    print("📌 Teste 5: Verificando conteúdo da página...")

                    # Pegar título da página
                    title = await page.title()
                    print(f"   Título da página: {title}")

                    # URL atual
                    url_atual = page.url
                    print(f"   URL atual: {url_atual}")

                    # Screenshot
                    screenshot_path = config.LOGS_DIR / "teste_acesso_portal.png"
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"   Screenshot salvo em: {screenshot_path}")
                    print()

                    print("📌 Teste 6: Procurando elementos na página...")

                    # Verificar se tem botões/links de login
                    botoes = await page.query_selector_all("button")
                    links = await page.query_selector_all("a")

                    print(f"   Botões encontrados: {len(botoes)}")
                    print(f"   Links encontrados: {len(links)}")

                    # Listar primeiros 5 botões
                    if botoes:
                        print("   Primeiros botões:")
                        for i, botao in enumerate(botoes[:5]):
                            texto = await botao.inner_text()
                            if texto.strip():
                                print(f"      {i+1}. {texto.strip()}")

                    print()
                    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
                    print()
                    print("O portal está acessível. Se você ainda tem problemas:")
                    print("  1. Verifique se seu certificado digital está instalado")
                    print("  2. Verifique a senha do certificado no arquivo .env")
                    print("  3. Tente executar o robô em modo visual (HEADLESS=False)")
                    print()

                    input("Pressione ENTER para fechar o navegador...")

                elif status == 404:
                    print("   ❌ Erro 404: Página não encontrada")
                    print("   A URL configurada está incorreta!")
                    print(f"   URL atual: {config.FGTS_URL_LOGIN}")
                    print()
                    print("   Possíveis soluções:")
                    print("   - Verifique se a URL do portal mudou")
                    print("   - Acesse manualmente pelo navegador e confirme a URL")

                elif status >= 500:
                    print(f"   ❌ Erro {status}: Servidor com problemas")
                    print("   O portal FGTS pode estar fora do ar ou em manutenção")

                else:
                    print(f"   ⚠️  Status inesperado: {status}")

            else:
                print("   ❌ Sem resposta do servidor")

        except Exception as e:
            print(f"   ❌ Erro ao acessar portal: {str(e)}")
            print()
            print("   Possíveis causas:")
            print("   1. Portal FGTS está fora do ar")
            print("   2. Problema de conexão com a internet")
            print("   3. Firewall bloqueando acesso")
            print("   4. URL do portal mudou")
            print()

            # Tentar screenshot mesmo com erro
            try:
                screenshot_path = config.LOGS_DIR / "teste_acesso_erro.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"   Screenshot do erro salvo em: {screenshot_path}")
            except:
                pass

    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")

    finally:
        print()
        print("🔧 Fechando navegador...")
        if context:
            await context.close()
        if browser:
            await browser.close()
        print("   ✓ Navegador fechado")


def main():
    """Função principal"""
    try:
        asyncio.run(testar_acesso_portal())
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
