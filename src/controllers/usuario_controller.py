from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService

from ..entities.enums.papel_usuario import PapelUsuario
from ..entities.usuario import Usuario


class UsuarioController:
    def __init__(
        self,
        usuario_service: UsuarioService,
        autenticacao_service: AutenticacaoService,
    ):
        self.usuario_service = usuario_service
        self.autenticacao_service = autenticacao_service

    def fazer_login(self, id_usuario: int, senha: str) -> Usuario:
        return self.autenticacao_service.autenticar(id_usuario, senha)

    def cadastrar_usuario(
        self, usuario_logado, nome: str, senha: str, papel
    ) -> Usuario:
        return self.usuario_service.cadastrar_usuario(
            usuario_logado, nome, senha, papel
        )

    def promover_gerente(self, usuario_logado, id_usuario_alvo: int) -> Usuario:
        return self.usuario_service.promover_a_gerente(usuario_logado, id_usuario_alvo)

    def resetar_senha(
        self, usuario_logado, id_usuario_alvo: int, nova_senha: str
    ) -> Usuario:
        return self.usuario_service.resetar_senha(
            usuario_logado, id_usuario_alvo, nova_senha
        )

    def atualizar_status(
        self, usuario_logado: Usuario, id_usuario_alvo: int, status_ativo: bool
    ) -> Usuario:
        return self.usuario_service.atualizar_status(
            usuario_logado, id_usuario_alvo, status_ativo
        )

    def atualizar_senha_usuario(
        self, usuario_logado, senha_atual: str, senha_nova: str
    ) -> Usuario:
        return self.autenticacao_service.atualizar_senha_usuario(
            usuario_logado.id_usuario, senha_atual, senha_nova
        )

    def obter_papeis_cadastro(self, usuario_logado: Usuario) -> list[PapelUsuario]:
        return self.usuario_service.obter_papeis_cadastro(usuario_logado)

    def garantir_admin_padrao(self) -> Usuario | None:
        return self.usuario_service.criar_admin_padrao()

    def listar_usuarios(
        self, usuario_logado: Usuario, status_ativo: bool = True
    ) -> list:
        return self.usuario_service.listar_usuarios(usuario_logado, status_ativo)
