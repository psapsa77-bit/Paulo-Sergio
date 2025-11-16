"""
Interface de linha de comando para o DET Robot
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from typing import Optional
from pathlib import Path
import getpass

from .browser import BrowserManager
from .auth import DETAuthenticator
from .scraper import DETScraper
from .storage import DETStorage
from .models import ConfiguracaoDET

app = typer.Typer(
    name="det-robot",
    help="Robô para extração de mensagens do DET (Domicílio Eletrônico Trabalhista)",
    add_completion=False,
)

console = Console()


def log_rich(mensagem: str):
    """Função de log com formatação rich"""
    console.log(mensagem)


@app.command()
def extrair(
    cpf: Optional[str] = typer.Option(
        None,
        "--cpf",
        "-c",
        help="CPF para login no Gov.br (apenas números)",
    ),
    senha: Optional[str] = typer.Option(
        None,
        "--senha",
        "-s",
        help="Senha do Gov.br (se não informada, será solicitada)",
    ),
    navegador: str = typer.Option(
        "auto",
        "--navegador",
        "-n",
        help="Navegador: auto, chrome, firefox, chromium",
    ),
    headless: bool = typer.Option(
        False,
        "--headless",
        "-h",
        help="Executar sem interface gráfica",
    ),
    manual: bool = typer.Option(
        False,
        "--manual",
        "-m",
        help="Login manual (abre navegador para você fazer login)",
    ),
    apenas_nao_lidas: bool = typer.Option(
        True,
        "--nao-lidas/--todas",
        help="Extrair apenas mensagens não lidas",
    ),
    limite: int = typer.Option(
        100,
        "--limite",
        "-l",
        help="Limite de mensagens a extrair",
    ),
    formato: str = typer.Option(
        "json",
        "--formato",
        "-f",
        help="Formato de saída: json, csv, excel, txt",
    ),
    pasta_saida: str = typer.Option(
        "./dados_det",
        "--pasta",
        "-p",
        help="Pasta para salvar os dados",
    ),
):
    """
    Extrai mensagens do DET (Domicílio Eletrônico Trabalhista)
    """
    console.print(Panel.fit(
        "[bold blue]DET Robot[/bold blue]\n"
        "Extrator de mensagens do Domicílio Eletrônico Trabalhista",
        border_style="blue"
    ))

    # Validar parâmetros
    if not manual and not cpf:
        cpf = typer.prompt("CPF (apenas números)")

    if not manual and not senha and cpf:
        senha = getpass.getpass("Senha do Gov.br: ")

    # Inicializar componentes
    storage = DETStorage(pasta_saida, log_callback=log_rich)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Iniciar navegador
            task = progress.add_task("Iniciando navegador...", total=None)
            browser = BrowserManager(
                navegador=navegador,
                headless=headless,
                log_callback=log_rich
            )
            browser.iniciar()
            progress.update(task, completed=True)

            # Autenticação
            auth = DETAuthenticator(browser, log_callback=log_rich)

            task = progress.add_task("Acessando DET...", total=None)
            auth.acessar_pagina_login()
            progress.update(task, completed=True)

            if manual:
                console.print("\n[yellow]Modo de login manual ativado[/yellow]")
                console.print("Por favor, faça login no navegador que foi aberto.")
                console.print("O sistema aguardará até 5 minutos.\n")

                task = progress.add_task("Aguardando login manual...", total=None)
                sucesso = auth.login_manual(timeout_minutos=5)
                progress.update(task, completed=True)
            else:
                task = progress.add_task("Realizando login...", total=None)
                sucesso = auth.login_govbr(cpf, senha)
                progress.update(task, completed=True)

            if not sucesso:
                console.print("[red]Falha na autenticação[/red]")
                browser.capturar_screenshot("falha_login.png")
                raise typer.Exit(code=1)

            console.print("[green]Login realizado com sucesso![/green]\n")

            # Extração
            scraper = DETScraper(browser, auth, log_callback=log_rich)

            task = progress.add_task("Extraindo mensagens...", total=None)
            resultado = scraper.executar_extracao_completa(
                apenas_nao_lidas=apenas_nao_lidas,
                limite=limite
            )
            progress.update(task, completed=True)

        # Exibir resultados
        if resultado.sucesso:
            console.print(f"\n[green]Extração concluída![/green]")
            console.print(f"Total de mensagens: [bold]{resultado.total_extraido}[/bold]")

            if resultado.mensagens:
                # Criar tabela de mensagens
                tabela = Table(title="Mensagens Extraídas")
                tabela.add_column("Nº", style="cyan", no_wrap=True)
                tabela.add_column("Assunto", style="white")
                tabela.add_column("Data", style="yellow")
                tabela.add_column("Status", style="green")
                tabela.add_column("Prazo", style="red")

                for i, msg in enumerate(resultado.mensagens[:20], 1):  # Mostrar primeiras 20
                    prazo = ""
                    if msg.dias_restantes is not None:
                        if msg.dias_restantes < 5:
                            prazo = f"[red bold]{msg.dias_restantes} dias[/red bold]"
                        else:
                            prazo = f"{msg.dias_restantes} dias"

                    tabela.add_row(
                        str(i),
                        msg.assunto[:50] + "..." if len(msg.assunto) > 50 else msg.assunto,
                        msg.data_envio.strftime("%d/%m/%Y"),
                        msg.status.value,
                        prazo
                    )

                console.print(tabela)

                if len(resultado.mensagens) > 20:
                    console.print(f"\n[dim]... e mais {len(resultado.mensagens) - 20} mensagens[/dim]")

            # Salvar dados
            task = progress.add_task("Salvando dados...", total=None)

            arquivos_salvos = []

            if formato in ["json", "todos"]:
                arquivo = storage.salvar_json(resultado)
                arquivos_salvos.append(arquivo)

            if formato in ["csv", "todos"]:
                arquivo = storage.salvar_csv(resultado)
                arquivos_salvos.append(arquivo)

            if formato in ["excel", "xlsx", "todos"]:
                arquivo = storage.salvar_excel(resultado)
                arquivos_salvos.append(arquivo)

            if formato in ["txt", "texto", "todos"]:
                arquivo = storage.salvar_relatorio_texto(resultado)
                arquivos_salvos.append(arquivo)

            console.print("\n[green]Arquivos salvos:[/green]")
            for arq in arquivos_salvos:
                console.print(f"  - {arq}")

        else:
            console.print(f"\n[red]Extração falhou[/red]")
            for erro in resultado.erros:
                console.print(f"  - {erro}")

        # Fechar navegador
        browser.fechar()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n[red]Erro: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def listar(
    pasta: str = typer.Option(
        "./dados_det",
        "--pasta",
        "-p",
        help="Pasta com dados salvos",
    ),
):
    """
    Lista extrações anteriores salvas
    """
    storage = DETStorage(pasta)
    extracoes = storage.listar_extracoes()

    if not extracoes:
        console.print("[yellow]Nenhuma extração encontrada[/yellow]")
        return

    tabela = Table(title="Extrações Salvas")
    tabela.add_column("Nome", style="cyan")
    tabela.add_column("Data", style="yellow")
    tabela.add_column("Tamanho", style="green")

    for ext in extracoes:
        tabela.add_row(
            ext["nome"],
            ext["data_modificacao"].strftime("%d/%m/%Y %H:%M"),
            f"{ext['tamanho'] / 1024:.1f} KB"
        )

    console.print(tabela)


@app.command()
def visualizar(
    arquivo: str = typer.Argument(help="Caminho do arquivo JSON a visualizar"),
):
    """
    Visualiza detalhes de uma extração salva
    """
    storage = DETStorage()

    try:
        resultado = storage.carregar_json(arquivo)
        relatorio = storage.gerar_relatorio_texto(resultado)
        console.print(relatorio)
    except Exception as e:
        console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def testar_navegador(
    navegador: str = typer.Option(
        "auto",
        "--navegador",
        "-n",
        help="Navegador: auto, chrome, firefox, chromium",
    ),
):
    """
    Testa se o navegador está funcionando corretamente
    """
    console.print("[blue]Testando navegador...[/blue]")

    try:
        browser = BrowserManager(
            navegador=navegador,
            headless=False,
            log_callback=log_rich
        )

        browser.iniciar()
        console.print(f"[green]Navegador {browser.navegador_usado} iniciado com sucesso![/green]")

        browser.acessar_det()
        console.print("[green]Site do DET acessado com sucesso![/green]")

        console.print("\nNavegador ficará aberto por 10 segundos...")
        import time
        time.sleep(10)

        browser.fechar()
        console.print("[green]Teste concluído com sucesso![/green]")

    except Exception as e:
        console.print(f"[red]Erro no teste: {e}[/red]")
        raise typer.Exit(code=1)


def main():
    """Entry point para CLI"""
    app()


if __name__ == "__main__":
    main()
