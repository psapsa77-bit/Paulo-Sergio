"""
Autenticação com certificado digital A1 para o portal FGTS Digital.
Lida com leitura, validação e configuração do certificado .pfx/.p12.
"""

from __future__ import annotations

import logging
import os
import ssl
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Tuple

from .models import CertificadoDigital

logger = logging.getLogger(__name__)


class CertificadoError(Exception):
    """Erro relacionado ao certificado digital."""
    pass


class FGTSAuthenticator:
    """
    Gerencia autenticação com certificado digital A1.

    Valida, carrega e prepara o certificado para uso com Playwright.
    """

    def __init__(self, caminho: str | Path, senha: str):
        self.caminho = Path(caminho)
        self.senha = senha
        self._certificado: Optional[CertificadoDigital] = None
        self._cert_pem_path: Optional[Path] = None
        self._key_pem_path: Optional[Path] = None

    def validar(self) -> CertificadoDigital:
        """
        Valida o certificado e retorna informações sobre ele.
        Raises CertificadoError se inválido.
        """
        if not self.caminho.exists():
            raise CertificadoError(f"Arquivo de certificado não encontrado: {self.caminho}")

        sufixo = self.caminho.suffix.lower()
        if sufixo not in (".pfx", ".p12"):
            raise CertificadoError(f"Formato de certificado não suportado: {sufixo}. Use .pfx ou .p12")

        try:
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.x509 import NameOID
        except ImportError:
            # Sem a lib cryptography, só verifica se o arquivo é legível
            logger.warning("cryptography não instalada; validação detalhada do certificado ignorada.")
            self._certificado = CertificadoDigital(
                caminho=self.caminho,
                senha=self.senha,
            )
            return self._certificado

        try:
            dados = self.caminho.read_bytes()
            chave_privada, certificado, _chain = pkcs12.load_key_and_certificates(
                dados, self.senha.encode()
            )
        except Exception as exc:
            raise CertificadoError(
                f"Falha ao abrir certificado. Verifique se a senha está correta. Detalhe: {exc}"
            ) from exc

        # Extrair informações
        valido_ate: Optional[date] = None
        cpf_cnpj: Optional[str] = None
        nome_titular: Optional[str] = None

        if certificado is not None:
            valido_ate = certificado.not_valid_after_utc.date() if hasattr(
                certificado, "not_valid_after_utc"
            ) else certificado.not_valid_after.date()

            try:
                nome_titular = certificado.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            except (IndexError, Exception):
                pass

            # CPF/CNPJ costuma estar no subject serialNumber ou em OIDs específicos
            try:
                serial_attr = certificado.subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
                if serial_attr:
                    cpf_cnpj = serial_attr[0].value
            except Exception:
                pass

        self._certificado = CertificadoDigital(
            caminho=self.caminho,
            senha=self.senha,
            valido_ate=valido_ate,
            cpf_cnpj=cpf_cnpj,
            nome_titular=nome_titular,
        )

        if not self._certificado.esta_valido:
            raise CertificadoError(
                f"Certificado vencido em {valido_ate}. Por favor, renove seu certificado digital."
            )

        logger.info("Certificado validado: %s | Válido até %s", nome_titular, valido_ate)
        return self._certificado

    def extrair_pem(self) -> Tuple[Path, Path]:
        """
        Extrai o certificado e a chave privada em formato PEM
        para arquivos temporários.

        Returns:
            Tuple[Path, Path]: (caminho_cert_pem, caminho_chave_pem)
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.serialization import pkcs12
        except ImportError as exc:
            raise CertificadoError(
                "A biblioteca 'cryptography' é necessária para extrair PEM. "
                "Instale com: pip install cryptography"
            ) from exc

        dados = self.caminho.read_bytes()
        chave_privada, certificado, chain = pkcs12.load_key_and_certificates(
            dados, self.senha.encode()
        )

        # Serializar certificado em PEM
        cert_pem = certificado.public_bytes(serialization.Encoding.PEM)

        # Serializar chave privada em PEM (sem senha para facilitar uso com Playwright)
        key_pem = chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Salvar em arquivos temporários
        cert_file = tempfile.NamedTemporaryFile(suffix="_cert.pem", delete=False)
        cert_file.write(cert_pem)
        cert_file.close()

        key_file = tempfile.NamedTemporaryFile(suffix="_key.pem", delete=False)
        key_file.write(key_pem)
        key_file.close()

        self._cert_pem_path = Path(cert_file.name)
        self._key_pem_path = Path(key_file.name)

        logger.debug("PEM extraídos: cert=%s  key=%s", self._cert_pem_path, self._key_pem_path)
        return self._cert_pem_path, self._key_pem_path

    def limpar_arquivos_temporarios(self) -> None:
        """Remove arquivos PEM temporários do disco."""
        for path in (self._cert_pem_path, self._key_pem_path):
            if path and path.exists():
                try:
                    path.unlink()
                    logger.debug("Arquivo temporário removido: %s", path)
                except Exception:
                    pass
        self._cert_pem_path = None
        self._key_pem_path = None

    @property
    def certificado(self) -> Optional[CertificadoDigital]:
        return self._certificado

    @property
    def cert_pem_path(self) -> Optional[Path]:
        return self._cert_pem_path

    @property
    def key_pem_path(self) -> Optional[Path]:
        return self._key_pem_path

    def __del__(self):
        self.limpar_arquivos_temporarios()
