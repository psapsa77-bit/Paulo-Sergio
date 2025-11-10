"""
Geradores de relatórios em HTML e PDF
"""

from pathlib import Path
from typing import Union
import tempfile

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from .models import RescisaoTrabalhista
from .analyzer import RescisaoAnalyzer


class HTMLGenerator:
    """Gerador de relatórios HTML"""

    def __init__(self):
        """Inicializa o gerador HTML"""
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def gerar(self, rescisao: RescisaoTrabalhista, output_path: Union[str, Path]) -> Path:
        """
        Gera relatório HTML

        Args:
            rescisao: Objeto RescisaoTrabalhista
            output_path: Caminho para salvar o arquivo HTML

        Returns:
            Path: Caminho do arquivo gerado
        """
        analyzer = RescisaoAnalyzer(rescisao)
        dados = analyzer.gerar_resumo_completo()

        template = self.env.get_template('rescisao.html')
        html_content = template.render(**dados)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path


class PDFGenerator:
    """Gerador de relatórios PDF"""

    def __init__(self):
        """Inicializa o gerador PDF"""
        self.html_generator = HTMLGenerator()

    def gerar(self, rescisao: RescisaoTrabalhista, output_path: Union[str, Path]) -> Path:
        """
        Gera relatório PDF

        Args:
            rescisao: Objeto RescisaoTrabalhista
            output_path: Caminho para salvar o arquivo PDF

        Returns:
            Path: Caminho do arquivo gerado
        """
        # Gera HTML temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            analyzer = RescisaoAnalyzer(rescisao)
            dados = analyzer.gerar_resumo_completo()

            template = self.html_generator.env.get_template('rescisao.html')
            html_content = template.render(**dados)
            tmp.write(html_content)
            tmp_path = tmp.name

        # Converte HTML para PDF
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        HTML(tmp_path).write_pdf(output_path)

        # Remove arquivo temporário
        Path(tmp_path).unlink()

        return output_path

    def gerar_from_html(self, html_path: Union[str, Path], output_path: Union[str, Path]) -> Path:
        """
        Gera PDF a partir de arquivo HTML existente

        Args:
            html_path: Caminho do arquivo HTML
            output_path: Caminho para salvar o arquivo PDF

        Returns:
            Path: Caminho do arquivo gerado
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        HTML(str(html_path)).write_pdf(output_path)

        return output_path
