"""
Módulo de autenticação no FGTS Digital
======================================

Gerencia a autenticação usando certificado digital A1 (.pfx/.p12)
e integração com Playwright para automação do navegador.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, date

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12

from .models import CertificadoDigital

logger = logging.getLogger(__name__)


class FGTSAuthenticator:
    """
    Gerencia autenticação no portal FGTS Digital usando certificado digital.
    """

    # URLs do FGTS Digital
    URL_FGTS_DIGITAL = "https://fgtsdigital.caixa.gov.br"
    URL_LOGIN = f"{URL_FGTS_DIGITAL}/login"
    URL_PORTAL = f"{URL_FGTS_DIGITAL}/empregador"

    def __init__(self, certificado: CertificadoDigital):
        """
        Inicializa o autenticador com um certificado digital.

        Args:
            certificado: Objeto CertificadoDigital com caminho e senha
        """
        self.certificado = certificado
        self._info_certificado: Optional[Dict[str, Any]] = None
        self.autenticado = False

    def validar_certificado(self) -> Dict[str, Any]:
        """
        Valida e extrai informações do certificado digital.

        Returns:
            Dicionário com informações do certificado

        Raises:
            ValueError: Se o certificado for inválido ou estiver vencido
        """
        try:
            # Ler arquivo do certificado
            with open(self.certificado.caminho, 'rb') as f:
                pfx_data = f.read()

            # Decodificar PKCS12
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data,
                self.certificado.senha.encode(),
                backend=default_backend()
            )

            if certificate is None:
                raise ValueError("Certificado não encontrado no arquivo PFX")

            # Extrair informações do certificado
            subject = certificate.subject
            issuer = certificate.issuer

            # Extrair CN (Common Name) - geralmente contém nome e CPF/CNPJ
            cn = None
            for attribute in subject:
                if attribute.oid == x509.oid.NameOID.COMMON_NAME:
                    cn = attribute.value
                    break

            # Extrair CPF/CNPJ do subject alternative names ou do CN
            cpf_cnpj = self._extrair_cpf_cnpj(certificate)

            # Validar data de validade
            valido_ate = certificate.not_valid_after_utc.date()
            hoje = date.today()

            if valido_ate < hoje:
                raise ValueError(f"Certificado vencido em {valido_ate}")

            info = {
                "nome_titular": cn,
                "cpf_cnpj": cpf_cnpj,
                "emissor": issuer.rfc4514_string(),
                "valido_de": certificate.not_valid_before_utc.date().isoformat(),
                "valido_ate": valido_ate.isoformat(),
                "numero_serie": certificate.serial_number,
                "dias_para_vencer": (valido_ate - hoje).days,
                "certificados_adicionais": len(additional_certs) if additional_certs else 0
            }

            # Atualizar modelo
            self.certificado.valido_ate = valido_ate
            self.certificado.cpf_cnpj = cpf_cnpj
            self.certificado.nome_titular = cn

            self._info_certificado = info
            logger.info(f"Certificado validado: {cn} - Válido até {valido_ate}")

            return info

        except Exception as e:
            logger.error(f"Erro ao validar certificado: {e}")
            raise ValueError(f"Certificado inválido: {e}")

    def _extrair_cpf_cnpj(self, certificate: x509.Certificate) -> Optional[str]:
        """
        Extrai CPF ou CNPJ do certificado.

        Args:
            certificate: Certificado X.509

        Returns:
            CPF ou CNPJ extraído, ou None se não encontrado
        """
        # Tentar extrair do Subject Alternative Names
        try:
            san_ext = certificate.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            for name in san_ext.value:
                if isinstance(name, x509.RFC822Name):
                    # Pode conter CPF/CNPJ no email
                    email = name.value
                    cpf_cnpj = ''.join(filter(str.isdigit, email))
                    if len(cpf_cnpj) in [11, 14]:  # CPF ou CNPJ
                        return cpf_cnpj
        except x509.ExtensionNotFound:
            pass

        # Tentar extrair do Common Name
        subject = certificate.subject
        for attribute in subject:
            if attribute.oid == x509.oid.NameOID.COMMON_NAME:
                cn = attribute.value
                # Extrair números do CN
                cpf_cnpj = ''.join(filter(str.isdigit, cn))
                if len(cpf_cnpj) in [11, 14]:
                    return cpf_cnpj

        return None

    def obter_configuracao_playwright(self) -> Dict[str, Any]:
        """
        Retorna a configuração do certificado para uso com Playwright.

        Returns:
            Dicionário com configuração de client_certificates para Playwright

        Example:
            config = auth.obter_configuracao_playwright()
            context = browser.new_context(client_certificates=[config])
        """
        return {
            "origin": self.URL_FGTS_DIGITAL,
            "pfxPath": str(self.certificado.caminho.absolute()),
            "passphrase": self.certificado.senha
        }

    def obter_info_certificado(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações do certificado (deve chamar validar_certificado primeiro).

        Returns:
            Dicionário com informações do certificado ou None
        """
        return self._info_certificado

    def verificar_autenticacao(self, url_atual: str) -> bool:
        """
        Verifica se está autenticado baseado na URL atual.

        Args:
            url_atual: URL atual do navegador

        Returns:
            True se autenticado, False caso contrário
        """
        self.autenticado = self.URL_PORTAL in url_atual or "/empregador" in url_atual
        return self.autenticado

    def get_headers_autenticacao(self) -> Dict[str, str]:
        """
        Retorna headers customizados para requisições autenticadas.

        Returns:
            Dicionário com headers HTTP
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def limpar_sessao(self) -> None:
        """Limpa informações de sessão e marca como não autenticado."""
        self.autenticado = False
        logger.info("Sessão limpa")

    def __repr__(self) -> str:
        """Representação string do autenticador"""
        if self._info_certificado:
            return (
                f"FGTSAuthenticator("
                f"titular={self._info_certificado.get('nome_titular')}, "
                f"cpf_cnpj={self._info_certificado.get('cpf_cnpj')}, "
                f"valido_ate={self._info_certificado.get('valido_ate')}, "
                f"autenticado={self.autenticado})"
            )
        return f"FGTSAuthenticator(certificado={self.certificado.caminho.name}, autenticado={self.autenticado})"
