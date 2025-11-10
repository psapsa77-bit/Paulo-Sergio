"""
Interface de linha de comando para o Labor Termination Analyzer
"""

from pathlib import Path
from typing import Optional
import sys

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .parser import RescisaoParser
from .analyzer import RescisaoAnalyzer
from .generators import HTMLGenerator, PDFGenerator

app = typer.Typer(
    name="rescisao",
    help="Aplicativo para análise de rescisões trabalhistas",
    add_completion=False
)

console = Console()


@app.command("analisar")
def analisar(
    arquivo_json: Path = typer.Argument(
        ...,
        help="Caminho para o arquivo JSON com os dados da rescisão",
        exists=True
    ),
    html: Optional[Path] = typer.Option(
        None,
        "--html",
        "-h",
        help="Gerar relatório HTML no caminho especificado"
    ),
    pdf: Optional[Path] = typer.Option(
        None,
        "--pdf",
        "-p",
        help="Gerar relatório PDF no caminho especificado"
    ),
    mostrar_terminal: bool = typer.Option(
        True,
        "--terminal/--no-terminal",
        "-t/-nt",
        help="Mostrar análise no terminal"
    )
):
    """
    Analisa uma rescisão trabalhista a partir de arquivo JSON

    Exemplo de uso:

        rescisao analisar exemplo.json --html relatorio.html --pdf relatorio.pdf
    """
    try:
        # Parse do arquivo JSON
        console.print(f"\n[cyan]📂 Lendo arquivo:[/cyan] {arquivo_json}")
        rescisao = RescisaoParser.from_json_file(arquivo_json)

        # Análise
        analyzer = RescisaoAnalyzer(rescisao)
        resumo = analyzer.gerar_resumo_completo()

        # Mostrar no terminal
        if mostrar_terminal:
            _exibir_analise_terminal(resumo)

        # Gerar HTML
        if html:
            console.print(f"\n[cyan]📄 Gerando relatório HTML...[/cyan]")
            html_gen = HTMLGenerator()
            html_path = html_gen.gerar(rescisao, html)
            console.print(f"[green]✓ HTML gerado:[/green] {html_path}")

        # Gerar PDF
        if pdf:
            console.print(f"\n[cyan]📑 Gerando relatório PDF...[/cyan]")
            pdf_gen = PDFGenerator()
            pdf_path = pdf_gen.gerar(rescisao, pdf)
            console.print(f"[green]✓ PDF gerado:[/green] {pdf_path}")

        console.print("\n[bold green]✓ Análise concluída com sucesso![/bold green]\n")

    except FileNotFoundError:
        console.print(f"[bold red]✗ Erro:[/bold red] Arquivo não encontrado: {arquivo_json}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Erro:[/bold red] {str(e)}")
        sys.exit(1)


@app.command("exemplo")
def criar_exemplo(
    output: Path = typer.Option(
        "exemplo_rescisao.json",
        "--output",
        "-o",
        help="Caminho para salvar o arquivo de exemplo"
    )
):
    """
    Cria um arquivo JSON de exemplo com dados de rescisão
    """
    import json
    from datetime import date, timedelta

    exemplo = {
        "funcionario": {
            "nome": "Maria da Silva",
            "cpf": "123.456.789-00",
            "cargo": "Analista de Sistemas",
            "data_admissao": "2020-01-15",
            "data_demissao": "2025-11-10",
            "salario_bruto": "5000.00"
        },
        "tipo_rescisao": "sem justa causa",
        "verbas": {
            "saldo_salario": "1666.67",
            "aviso_previo_indenizado": "5416.67",
            "ferias_vencidas": "0.00",
            "ferias_proporcionais": "4583.33",
            "um_terco_ferias": "1527.78",
            "decimo_terceiro_proporcional": "4583.33",
            "multa_fgts_40": "11680.00",
            "saldo_fgts": "29200.00"
        },
        "descontos": {
            "inss": "835.22",
            "irrf": "427.37",
            "aviso_previo_indenizado": "0.00"
        },
        "observacoes": "Rescisão processada conforme legislação trabalhista vigente. O funcionário tem direito a seguro-desemprego."
    }

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(exemplo, f, ensure_ascii=False, indent=2)

    console.print(f"\n[green]✓ Arquivo de exemplo criado:[/green] {output}")
    console.print("\n[cyan]Para analisar este exemplo, execute:[/cyan]")
    console.print(f"  rescisao analisar {output}\n")


def _exibir_analise_terminal(resumo: dict):
    """Exibe a análise no terminal de forma formatada"""

    # Cabeçalho
    console.print(Panel.fit(
        f"[bold cyan]📋 Análise de Rescisão Trabalhista[/bold cyan]\n"
        f"[white]{resumo['funcionario']['nome']}[/white]",
        border_style="cyan"
    ))

    # Dados do funcionário
    console.print("\n[bold yellow]👤 Dados do Funcionário[/bold yellow]")
    func = resumo['funcionario']

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="white")

    table.add_row("Nome", func['nome'])
    table.add_row("CPF", func['cpf'])
    table.add_row("Cargo", func['cargo'])
    table.add_row("Admissão", func['data_admissao'])
    table.add_row("Demissão", func['data_demissao'])
    table.add_row("Tempo de Serviço", func['tempo_servico'])
    table.add_row("Salário Bruto", func['salario_bruto'])

    console.print(table)

    # Tipo de rescisão
    console.print(f"\n[bold yellow]📑 Tipo de Rescisão[/bold yellow]")
    tipo = resumo['tipo_rescisao']
    console.print(Panel(
        f"[bold white]{tipo['nome']}[/bold white]\n\n{tipo['descricao']}",
        border_style="blue"
    ))

    # Verbas
    if resumo['verbas']:
        console.print(f"\n[bold yellow]💰 Verbas Rescisórias[/bold yellow]")
        table_verbas = Table(show_header=True, box=box.ROUNDED)
        table_verbas.add_column("Verba", style="cyan", width=40)
        table_verbas.add_column("Valor", style="green", justify="right")

        for verba in resumo['verbas']:
            table_verbas.add_row(verba['titulo'], verba['valor_formatado'])

        console.print(table_verbas)

    # Descontos
    if resumo['descontos']:
        console.print(f"\n[bold yellow]➖ Descontos[/bold yellow]")
        table_descontos = Table(show_header=True, box=box.ROUNDED)
        table_descontos.add_column("Desconto", style="cyan", width=40)
        table_descontos.add_column("Valor", style="red", justify="right")

        for desconto in resumo['descontos']:
            table_descontos.add_row(desconto['titulo'], desconto['valor_formatado'])

        console.print(table_descontos)

    # Totais
    console.print(f"\n[bold yellow]💵 Resumo Financeiro[/bold yellow]")
    totais = resumo['totais']

    console.print(Panel(
        f"[white]Total de Verbas:[/white] [green]{totais['total_verbas_formatado']}[/green]\n"
        f"[white]Total de Descontos:[/white] [red]{totais['total_descontos_formatado']}[/red]\n\n"
        f"[bold white]Valor Líquido a Receber:[/bold white] [bold green]{totais['valor_liquido_formatado']}[/bold green]",
        border_style="green",
        title="💰 Resumo"
    ))

    # Observações
    if resumo['observacoes']:
        console.print(f"\n[bold yellow]⚠️  Observações[/bold yellow]")
        console.print(Panel(resumo['observacoes'], border_style="yellow"))


@app.command("versao")
def versao():
    """Mostra a versão do aplicativo"""
    from . import __version__
    console.print(f"\n[cyan]Labor Termination Analyzer[/cyan] v{__version__}\n")


def main():
    """Função principal"""
    app()


if __name__ == "__main__":
    main()
