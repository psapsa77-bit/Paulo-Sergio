"""
Modelos de dados para o DET Robot
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class StatusMensagem(str, Enum):
    """Status da mensagem no DET"""
    NAO_LIDA = "nao_lida"
    LIDA = "lida"
    ARQUIVADA = "arquivada"


class TipoMensagem(str, Enum):
    """Tipos de mensagens do DET"""
    NOTIFICACAO = "notificacao"
    INTIMACAO = "intimacao"
    AUTO_INFRACAO = "auto_infracao"
    COMUNICADO = "comunicado"
    OUTRO = "outro"


class MensagemDET(BaseModel):
    """Modelo de uma mensagem do DET"""

    id_mensagem: str = Field(description="ID único da mensagem")
    numero: Optional[str] = Field(default=None, description="Número da mensagem/documento")
    assunto: str = Field(description="Assunto da mensagem")
    tipo: TipoMensagem = Field(default=TipoMensagem.OUTRO, description="Tipo da mensagem")
    data_envio: datetime = Field(description="Data de envio da mensagem")
    data_ciencia: Optional[datetime] = Field(default=None, description="Data de ciência/leitura")
    prazo_resposta: Optional[datetime] = Field(default=None, description="Prazo para resposta/ação")
    dias_restantes: Optional[int] = Field(default=None, description="Dias restantes para prazo")
    remetente: str = Field(description="Remetente da mensagem")
    status: StatusMensagem = Field(default=StatusMensagem.NAO_LIDA, description="Status da mensagem")
    resumo: Optional[str] = Field(default=None, description="Resumo/preview do conteúdo")
    url_mensagem: Optional[str] = Field(default=None, description="URL para acessar a mensagem completa")
    anexos: List[str] = Field(default_factory=list, description="Lista de anexos")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmpregadorDET(BaseModel):
    """Dados do empregador no DET"""

    cnpj_cpf: str = Field(description="CNPJ ou CPF do empregador")
    razao_social: Optional[str] = Field(default=None, description="Razão social ou nome")
    nome_fantasia: Optional[str] = Field(default=None, description="Nome fantasia")
    email_cadastrado: Optional[str] = Field(default=None, description="Email cadastrado no DET")
    telefone: Optional[str] = Field(default=None, description="Telefone cadastrado")
    endereco: Optional[str] = Field(default=None, description="Endereço cadastrado")
    ultimo_acesso: Optional[datetime] = Field(default=None, description="Data do último acesso")
    total_mensagens: int = Field(default=0, description="Total de mensagens na caixa")
    mensagens_nao_lidas: int = Field(default=0, description="Quantidade de mensagens não lidas")


class ResultadoExtracao(BaseModel):
    """Resultado completo da extração do DET"""

    data_extracao: datetime = Field(default_factory=datetime.now, description="Data/hora da extração")
    empregador: Optional[EmpregadorDET] = Field(default=None, description="Dados do empregador")
    mensagens: List[MensagemDET] = Field(default_factory=list, description="Lista de mensagens extraídas")
    total_extraido: int = Field(default=0, description="Total de mensagens extraídas")
    apenas_nao_lidas: bool = Field(default=True, description="Se extraiu apenas não lidas")
    erros: List[str] = Field(default_factory=list, description="Erros durante extração")
    sucesso: bool = Field(default=True, description="Se a extração foi bem sucedida")
    tempo_execucao: Optional[float] = Field(default=None, description="Tempo de execução em segundos")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def resumo(self) -> str:
        """Gera um resumo da extração"""
        if not self.sucesso:
            return f"Extração falhou com {len(self.erros)} erro(s)"

        return (
            f"Extração realizada em {self.data_extracao.strftime('%d/%m/%Y %H:%M')}\n"
            f"Total de mensagens: {self.total_extraido}\n"
            f"Mensagens não lidas: {sum(1 for m in self.mensagens if m.status == StatusMensagem.NAO_LIDA)}\n"
            f"Tempo de execução: {self.tempo_execucao:.2f}s" if self.tempo_execucao else ""
        )


class ConfiguracaoDET(BaseModel):
    """Configurações do robô DET"""

    # Navegador
    navegador: str = Field(default="auto", description="Navegador a usar: auto, chrome, firefox, chromium")
    headless: bool = Field(default=False, description="Executar sem interface gráfica")
    timeout: int = Field(default=30, description="Timeout padrão em segundos")

    # Autenticação
    metodo_auth: str = Field(default="govbr", description="Método: govbr ou certificado")
    cpf_cnpj: Optional[str] = Field(default=None, description="CPF ou CNPJ para login")
    senha: Optional[str] = Field(default=None, description="Senha (apenas para Gov.br)")
    caminho_certificado: Optional[str] = Field(default=None, description="Caminho do certificado digital")

    # Extração
    apenas_nao_lidas: bool = Field(default=True, description="Extrair apenas mensagens não lidas")
    limite_mensagens: int = Field(default=100, description="Limite de mensagens a extrair")
    baixar_anexos: bool = Field(default=False, description="Baixar anexos das mensagens")
    pasta_anexos: str = Field(default="./anexos_det", description="Pasta para salvar anexos")

    # Armazenamento
    formato_saida: str = Field(default="json", description="Formato: json, csv, excel")
    pasta_saida: str = Field(default="./dados_det", description="Pasta para salvar dados")

    # Segurança
    salvar_credenciais: bool = Field(default=False, description="Salvar credenciais localmente")
    log_detalhado: bool = Field(default=True, description="Ativar log detalhado")
