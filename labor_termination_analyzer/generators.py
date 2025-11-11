"""
Geradores de relatórios em HTML e PDF.

Este módulo cria relatórios visuais profissionais a partir
das análises de rescisões trabalhistas.
"""

from pathlib import Path
from typing import Union, Any
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)

from .analyzer import RescisaoAnalyzer
from .models import Rescisao


logger = logging.getLogger(__name__)


class HTMLGenerator:
    """
    Gerador de relatórios em HTML.

    Usa templates Jinja2 para criar relatórios visuais profissionais.
    """

    def __init__(self, template_dir: Union[str, Path, None] = None):
        """
        Inicializa o gerador HTML.

        Args:
            template_dir: Diretório dos templates. Se None, usa o diretório padrão.
        """
        if template_dir is None:
            # Usa diretório templates dentro do pacote
            template_dir = Path(__file__).parent / 'templates'

        self.template_dir = Path(template_dir)

        # Configura Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Adiciona filtros personalizados
        self.env.filters['currency'] = self._filtro_moeda
        self.env.filters['percentage'] = self._filtro_porcentagem
        self.env.filters['date_br'] = self._filtro_data_br

    @staticmethod
    def _filtro_moeda(valor: Any) -> str:
        """Formata valor como moeda brasileira."""
        try:
            from decimal import Decimal
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor))
            return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        except:
            return str(valor)

    @staticmethod
    def _filtro_porcentagem(valor: Any) -> str:
        """Formata valor como porcentagem."""
        try:
            from decimal import Decimal
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor))
            return f"{valor:.2f}%".replace('.', ',')
        except:
            return str(valor)

    @staticmethod
    def _filtro_data_br(valor: Any) -> str:
        """Formata data no padrão brasileiro."""
        try:
            from datetime import date
            if isinstance(valor, date):
                return valor.strftime('%d/%m/%Y')
            return str(valor)
        except:
            return str(valor)

    def gerar(self, rescisao: Rescisao, template_name: str = 'rescisao.html') -> str:
        """
        Gera HTML a partir de uma rescisão.

        Args:
            rescisao: Objeto Rescisao
            template_name: Nome do template a usar

        Returns:
            String HTML gerada

        Raises:
            FileNotFoundError: Se o template não existir
        """
        # Cria analisador
        analyzer = RescisaoAnalyzer(rescisao)

        # Gera resumo completo
        resumo = analyzer.gerar_resumo_completo()

        # Carrega template
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(f'Template não encontrado: {template_name}. Erro: {e}')

        # Renderiza
        html = template.render(
            rescisao=rescisao,
            resumo=resumo,
            analyzer=analyzer,
        )

        return html

    def gerar_arquivo(
        self,
        rescisao: Rescisao,
        caminho_saida: Union[str, Path],
        template_name: str = 'rescisao.html'
    ) -> Path:
        """
        Gera arquivo HTML.

        Args:
            rescisao: Objeto Rescisao
            caminho_saida: Caminho para salvar o HTML
            template_name: Nome do template

        Returns:
            Path do arquivo gerado
        """
        html = self.gerar(rescisao, template_name)

        caminho_path = Path(caminho_saida)
        caminho_path.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f'HTML gerado: {caminho_path}')
        return caminho_path


class PDFGenerator:
    """
    Gerador de relatórios em PDF.

    Converte HTML para PDF usando WeasyPrint.
    """

    def __init__(self, html_generator: HTMLGenerator = None):
        """
        Inicializa o gerador PDF.

        Args:
            html_generator: Gerador HTML a usar. Se None, cria um novo.

        Raises:
            RuntimeError: Se WeasyPrint não estiver disponível
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                f'WeasyPrint não está disponível: {WEASYPRINT_ERROR}\n\n'
                'SOLUÇÃO:\n'
                '1. Windows: Gere o HTML e use "Imprimir > Salvar como PDF" no navegador\n'
                '2. Linux: sudo apt-get install python3-weasyprint\n'
                '3. Mac: brew install python-weasyprint\n\n'
                'Ou instale as bibliotecas GTK conforme documentação do WeasyPrint.'
            )

        self.html_generator = html_generator or HTMLGenerator()

    def gerar(self, rescisao: Rescisao, template_name: str = 'rescisao.html') -> bytes:
        """
        Gera PDF a partir de uma rescisão.

        Args:
            rescisao: Objeto Rescisao
            template_name: Nome do template HTML a usar

        Returns:
            Bytes do PDF gerado
        """
        # Gera HTML
        html_content = self.html_generator.gerar(rescisao, template_name)

        # Converte para PDF
        pdf_bytes = HTML(string=html_content).write_pdf()

        return pdf_bytes

    def gerar_arquivo(
        self,
        rescisao: Rescisao,
        caminho_saida: Union[str, Path],
        template_name: str = 'rescisao.html'
    ) -> Path:
        """
        Gera arquivo PDF.

        Args:
            rescisao: Objeto Rescisao
            caminho_saida: Caminho para salvar o PDF
            template_name: Nome do template

        Returns:
            Path do arquivo gerado
        """
        pdf_bytes = self.gerar(rescisao, template_name)

        caminho_path = Path(caminho_saida)
        caminho_path.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho_path, 'wb') as f:
            f.write(pdf_bytes)

        logger.info(f'PDF gerado: {caminho_path}')
        return caminho_path

    @staticmethod
    def esta_disponivel() -> bool:
        """
        Verifica se o gerador PDF está disponível.

        Returns:
            True se WeasyPrint está disponível
        """
        return WEASYPRINT_AVAILABLE

    @staticmethod
    def obter_mensagem_erro() -> str:
        """
        Retorna mensagem de erro se PDF não estiver disponível.

        Returns:
            Mensagem de erro ou string vazia
        """
        if WEASYPRINT_AVAILABLE:
            return ""

        return (
            '⚠️ GERAÇÃO DE PDF NÃO DISPONÍVEL\n\n'
            'WeasyPrint não está instalado corretamente.\n\n'
            'SOLUÇÕES ALTERNATIVAS:\n'
            '1. 📄 Gere o relatório em HTML\n'
            '2. 🖨️  Abra o HTML no navegador\n'
            '3. 💾 Use "Imprimir > Salvar como PDF"\n\n'
            'INSTALAÇÃO DO WEASYPRINT:\n'
            '• Windows: Consulte SOLUCAO_PDF_WINDOWS.md\n'
            '• Linux: sudo apt-get install python3-weasyprint\n'
            '• Mac: brew install python-weasyprint\n\n'
            f'Erro técnico: {WEASYPRINT_ERROR}'
        )
