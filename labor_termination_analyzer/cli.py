"""
Interface de linha de comando (CLI) para análise de rescisões trabalhistas.

Comandos disponíveis:
- exemplo: Gera um arquivo JSON de exemplo
- analisar: Analisa uma rescisão e gera relatórios
- extrair: Extrai dados de um PDF
"""

from pathlib import Path
from typing import Optional
import sys

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("AVISO: Instale typer e rich para melhor experiência: pip install typer rich")

from .parser import RescisaoParser
from .pdf_extractor import PDFExtractor
from .analyzer import RescisaoAnalyzer
from .generators import HTMLGenerator, PDFGenerator


# Cria aplicação CLI
app = typer.Typer(
    name="rescisao",
    help="🔍 Analisador de Rescisões Trabalhistas - Ferramenta CLI",
    add_completion=False
)

console = Console() if RICH_AVAILABLE else None


@app.command()
def exemplo(
    arquivo_saida: str = typer.Argument(
        "exemplo_rescisao.json",
        help="Nome do arquivo JSON de saída"
    )
):
    """
    Gera um arquivo JSON de exemplo para teste.

    Exemplo:
        rescisao exemplo minha_rescisao.json
    """
    try:
        # Gera rescisão de exemplo
        rescisao = RescisaoParser.gerar_exemplo()

        # Salva em arquivo
        caminho = Path(arquivo_saida)
        RescisaoParser.para_arquivo(rescisao, caminho)

        if RICH_AVAILABLE:
            console.print(f"\n✅ [green]Arquivo de exemplo gerado:[/green] {caminho.absolute()}")
            console.print("\n📝 Você pode editar este arquivo e usar o comando [cyan]rescisao analisar[/cyan]\n")
        else:
            print(f"\n✅ Arquivo de exemplo gerado: {caminho.absolute()}")
            print("\n📝 Você pode editar este arquivo e usar o comando 'rescisao analisar'\n")

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n❌ [red]Erro:[/red] {e}\n", style="bold red")
        else:
            print(f"\n❌ Erro: {e}\n")
        raise typer.Exit(1)


@app.command()
def analisar(
    arquivo_entrada: str = typer.Argument(..., help="Arquivo JSON com dados da rescisão"),
    html: Optional[str] = typer.Option(None, "--html", "-h", help="Gerar relatório HTML (caminho do arquivo)"),
    pdf: Optional[str] = typer.Option(None, "--pdf", "-p", help="Gerar relatório PDF (caminho do arquivo)"),
    exibir: bool = typer.Option(True, "--exibir/--no-exibir", "-e/-E", help="Exibir análise no terminal")
):
    """
    Analisa uma rescisão trabalhista e gera relatórios.

    Exemplos:
        rescisao analisar minha_rescisao.json
        rescisao analisar dados.json --html relatorio.html
        rescisao analisar dados.json --html relatorio.html --pdf relatorio.pdf
        rescisao analisar dados.json --pdf relatorio.pdf --no-exibir
    """
    try:
        # Carrega arquivo
        if RICH_AVAILABLE:
            console.print(f"\n🔄 Carregando arquivo: {arquivo_entrada}...")
        else:
            print(f"\n🔄 Carregando arquivo: {arquivo_entrada}...")

        caminho_entrada = Path(arquivo_entrada)
        rescisao = RescisaoParser.de_arquivo(caminho_entrada)

        # Cria analisador
        analyzer = RescisaoAnalyzer(rescisao)
        resumo = analyzer.gerar_resumo_completo()

        # Exibe no terminal
        if exibir:
            exibir_analise_terminal(resumo)

        # Gera HTML
        if html:
            if RICH_AVAILABLE:
                console.print(f"\n📄 Gerando relatório HTML...")
            else:
                print(f"\n📄 Gerando relatório HTML...")

            html_gen = HTMLGenerator()
            caminho_html = html_gen.gerar_arquivo(rescisao, html)

            if RICH_AVAILABLE:
                console.print(f"✅ [green]HTML gerado:[/green] {caminho_html.absolute()}")
            else:
                print(f"✅ HTML gerado: {caminho_html.absolute()}")

        # Gera PDF
        if pdf:
            if not PDFGenerator.esta_disponivel():
                if RICH_AVAILABLE:
                    console.print("\n⚠️ [yellow]AVISO:[/yellow] WeasyPrint não disponível para gerar PDF.")
                    console.print("Gere o HTML e use 'Imprimir > Salvar como PDF' no navegador.\n")
                else:
                    print("\n⚠️ AVISO: WeasyPrint não disponível para gerar PDF.")
                    print("Gere o HTML e use 'Imprimir > Salvar como PDF' no navegador.\n")
            else:
                if RICH_AVAILABLE:
                    console.print(f"\n📑 Gerando relatório PDF...")
                else:
                    print(f"\n📑 Gerando relatório PDF...")

                pdf_gen = PDFGenerator()
                caminho_pdf = pdf_gen.gerar_arquivo(rescisao, pdf)

                if RICH_AVAILABLE:
                    console.print(f"✅ [green]PDF gerado:[/green] {caminho_pdf.absolute()}")
                else:
                    print(f"✅ PDF gerado: {caminho_pdf.absolute()}")

        if RICH_AVAILABLE:
            console.print("\n✨ [green bold]Análise concluída com sucesso![/green bold]\n")
        else:
            print("\n✨ Análise concluída com sucesso!\n")

    except FileNotFoundError as e:
        if RICH_AVAILABLE:
            console.print(f"\n❌ [red]Arquivo não encontrado:[/red] {e}\n")
        else:
            print(f"\n❌ Arquivo não encontrado: {e}\n")
        raise typer.Exit(1)

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n❌ [red]Erro:[/red] {e}\n")
        else:
            print(f"\n❌ Erro: {e}\n")
        raise typer.Exit(1)


@app.command()
def extrair(
    arquivo_pdf: str = typer.Argument(..., help="Arquivo PDF para extrair dados"),
    saida: str = typer.Option("dados_extraidos.json", "--saida", "-o", help="Arquivo JSON de saída"),
    ocr: bool = typer.Option(False, "--ocr", help="Usar OCR para PDFs escaneados")
):
    """
    Extrai dados de um PDF de rescisão trabalhista.

    Exemplos:
        rescisao extrair documento.pdf
        rescisao extrair documento.pdf --saida meus_dados.json
        rescisao extrair escaneado.pdf --ocr
    """
    try:
        if RICH_AVAILABLE:
            console.print(f"\n🔄 Extraindo dados do PDF: {arquivo_pdf}...")
            if ocr:
                console.print("   [yellow]OCR ativado (pode demorar mais)[/yellow]")
        else:
            print(f"\n🔄 Extraindo dados do PDF: {arquivo_pdf}...")
            if ocr:
                print("   OCR ativado (pode demorar mais)")

        # Extrai dados
        extractor = PDFExtractor(usar_ocr=ocr)
        dados, campos_faltantes = extractor.extrair_e_validar(arquivo_pdf)

        # Salva JSON
        caminho_saida = Path(saida)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            import json
            json.dump(dados, f, indent=2, ensure_ascii=False, default=str)

        if RICH_AVAILABLE:
            console.print(f"\n✅ [green]Dados extraídos salvos em:[/green] {caminho_saida.absolute()}")
        else:
            print(f"\n✅ Dados extraídos salvos em: {caminho_saida.absolute()}")

        # Mostra campos faltantes
        if campos_faltantes:
            if RICH_AVAILABLE:
                console.print(f"\n⚠️ [yellow]Campos não encontrados (preencha manualmente):[/yellow]")
                for campo in campos_faltantes:
                    console.print(f"   - {campo}")
            else:
                print(f"\n⚠️ Campos não encontrados (preencha manualmente):")
                for campo in campos_faltantes:
                    print(f"   - {campo}")

        if RICH_AVAILABLE:
            console.print(f"\n💡 [cyan]Próximo passo:[/cyan] Edite o arquivo JSON e use:")
            console.print(f"   [bold]rescisao analisar {caminho_saida}[/bold]\n")
        else:
            print(f"\n💡 Próximo passo: Edite o arquivo JSON e use:")
            print(f"   rescisao analisar {caminho_saida}\n")

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n❌ [red]Erro:[/red] {e}\n")
        else:
            print(f"\n❌ Erro: {e}\n")
        raise typer.Exit(1)


def exibir_analise_terminal(resumo: dict):
    """Exibe análise formatada no terminal."""
    if not RICH_AVAILABLE:
        # Versão simplificada sem rich
        print("\n" + "="*80)
        print("ANÁLISE DE RESCISÃO TRABALHISTA")
        print("="*80)

        func = resumo['funcionario']
        print(f"\nFuncionário: {func['nome']}")
        print(f"CPF: {func['cpf']}")
        print(f"Cargo: {func['cargo']}")
        print(f"Tempo de serviço: {func['tempo_servico_anos']} anos")

        print(f"\nTipo de Rescisão: {resumo['tipo_rescisao'].upper()}")

        print("\n" + "-"*80)
        print("TOTAIS FINANCEIROS")
        print("-"*80)
        print(f"Total de Verbas:    R$ {float(resumo['totais']['verbas']):>12,.2f}")
        print(f"Total de Descontos: R$ {float(resumo['totais']['descontos']):>12,.2f}")
        print(f"VALOR LÍQUIDO:      R$ {float(resumo['totais']['liquido']):>12,.2f}")

        if resumo['alertas']:
            print("\n" + "-"*80)
            print("ALERTAS")
            print("-"*80)
            for alerta in resumo['alertas']:
                print(f"[{alerta['tipo'].upper()}] {alerta['campo']}: {alerta['mensagem']}")

        print("\n" + "="*80 + "\n")
        return

    # Versão com rich
    console.print()

    # Painel principal
    console.print(Panel.fit(
        "[bold blue]📋 ANÁLISE DE RESCISÃO TRABALHISTA[/bold blue]",
        border_style="blue"
    ))

    # Dados do funcionário
    func = resumo['funcionario']
    func_table = Table(title="👤 Dados do Funcionário", show_header=False, border_style="cyan")
    func_table.add_column("Campo", style="cyan")
    func_table.add_column("Valor", style="white")

    func_table.add_row("Nome", func['nome'])
    func_table.add_row("CPF", func['cpf'])
    func_table.add_row("Cargo", func['cargo'])
    func_table.add_row("Data Admissão", str(func['data_admissao']))
    func_table.add_row("Data Demissão", str(func['data_demissao']))
    func_table.add_row("Tempo de Serviço", f"{func['tempo_servico_anos']} anos ({func['tempo_servico_meses']} meses)")
    func_table.add_row("Salário Bruto", f"R$ {float(func['salario_bruto']):,.2f}")

    console.print(func_table)
    console.print()

    # Tipo de rescisão
    tipo_info = resumo['direitos_tipo_rescisao']
    console.print(Panel(
        f"[bold]{tipo_info['nome']}[/bold]\n{tipo_info['descricao']}",
        title="📋 Tipo de Rescisão",
        border_style="magenta"
    ))
    console.print()

    # Totais
    totais_table = Table(title="💰 Resumo Financeiro", show_header=True, border_style="green")
    totais_table.add_column("Categoria", style="cyan", justify="left")
    totais_table.add_column("Valor (R$)", style="green", justify="right")

    totais_table.add_row(
        "Total de Verbas",
        f"{float(resumo['totais']['verbas']):,.2f}"
    )
    totais_table.add_row(
        "Total de Descontos",
        f"[red]{float(resumo['totais']['descontos']):,.2f}[/red]"
    )
    totais_table.add_row(
        "[bold]VALOR LÍQUIDO[/bold]",
        f"[bold green]{float(resumo['totais']['liquido']):,.2f}[/bold green]"
    )

    console.print(totais_table)
    console.print()

    # Verbas
    if resumo['verbas']:
        verbas_table = Table(title="💵 Verbas Rescisórias", show_header=True, border_style="green")
        verbas_table.add_column("Verba", style="cyan")
        verbas_table.add_column("Valor (R$)", style="green", justify="right")

        for verba in resumo['verbas']:
            verbas_table.add_row(verba['nome'], f"{float(verba['valor']):,.2f}")

        console.print(verbas_table)
        console.print()

    # Descontos
    if resumo['descontos']:
        descontos_table = Table(title="➖ Descontos", show_header=True, border_style="red")
        descontos_table.add_column("Desconto", style="cyan")
        descontos_table.add_column("Valor (R$)", style="red", justify="right")

        for desconto in resumo['descontos']:
            descontos_table.add_row(desconto['nome'], f"{float(desconto['valor']):,.2f}")

        console.print(descontos_table)
        console.print()

    # Alertas
    if resumo['alertas']:
        for alerta in resumo['alertas']:
            estilo_map = {
                'info': 'blue',
                'warning': 'yellow',
                'error': 'red'
            }
            estilo = estilo_map.get(alerta['tipo'], 'blue')

            console.print(Panel(
                f"[bold]{alerta['campo']}[/bold]\n{alerta['mensagem']}",
                border_style=estilo,
                title=f"⚠️ {alerta['tipo'].upper()}"
            ))

        console.print()


def main_cli():
    """Entry point para o CLI."""
    if not RICH_AVAILABLE:
        print("\n⚠️ AVISO: Para melhor experiência visual, instale:")
        print("   pip install typer rich\n")

    app()


if __name__ == "__main__":
    main_cli()
