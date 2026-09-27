import os

from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.usuario import Usuario
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService


class UsuarioService:
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        autenticacao_service: AutenticacaoService,
    ):
        self.usuario_repository = usuario_repository
        self.autenticacao_service = autenticacao_service

    def pode_gerenciar(self, usuario_logado: Usuario, usuario_alvo: Usuario) -> bool:
        if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
            return True

        if usuario_logado.papel == PapelUsuario.GERENTE:
            return usuario_alvo.papel == PapelUsuario.FUNCIONARIO
        return False

    def cadastrar_usuario(
        self,
        usuario_logado: Usuario,
        nome: str,
        senha: str,
        papel: PapelUsuario = PapelUsuario.FUNCIONARIO,
    ) -> Usuario:
        if not nome or not nome.strip():
            raise ValueError("O nome nao pode estar vazio.")

        if not senha or not senha.strip():
            raise ValueError("Senha nao pode estar vazio.")

        papeis_permitidos = self.obter_papeis_cadastro(usuario_logado)

        if papel not in papeis_permitidos:
            raise PermissionError("Você não pode cadastrar esse cargo.")

        senha_hash = self.autenticacao_service.gerar_senha_hash(senha)
        novo_usuario = Usuario(nome=nome, senha_hash=senha_hash, papel=papel)
        return self.usuario_repository.criar(novo_usuario)

    def promover_a_gerente(self, usuario_logado: Usuario, id_usuario: int) -> Usuario:
        if usuario_logado.papel != PapelUsuario.ADMINISTRADOR:
            raise PermissionError(
                "Apenas administradores podem promover funcionários a gerentes."
            )
        self._checar_id(id_usuario)

        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuário com id {id_usuario} não encontrado.")

        if usuario.papel != PapelUsuario.FUNCIONARIO:
            raise ValueError("Apenas funcionários podem ser promovidos a gerentes.")

        usuario.papel = PapelUsuario.GERENTE
        return self.usuario_repository.atualizar(usuario)

    def resetar_senha(
        self, usuario_logado: Usuario, id_usuario_alvo: int, nova_senha: str
    ) -> Usuario:
        self._checar_id(id_usuario_alvo)

        if not nova_senha or not nova_senha.strip():
            raise ValueError("Senha nao pode estar vazio.")

        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f"Usuário com id {id_usuario_alvo} não encontrado.")

        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError(
                "Você não tem permissão para resetar a senha deste usuário."
            )

        nova_senha_hash = self.autenticacao_service.gerar_senha_hash(nova_senha)
        usuario_alvo.senha_hash = nova_senha_hash
        return self.usuario_repository.atualizar(usuario_alvo)

    def atualizar_status(
        self, usuario_logado: Usuario, id_usuario_alvo: int, status_ativo: bool
    ) -> Usuario:
        self._checar_id(id_usuario_alvo)

        if not isinstance(status_ativo, bool):
            raise TypeError("Status deve ser True ou False.")

        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f"Usuário com id {id_usuario_alvo} não encontrado.")

        if usuario_alvo.papel == PapelUsuario.ADMINISTRADOR:
            raise PermissionError(
                "Contas de administradores nao podem ser ativadas ou desativas pelo sistema."
            )

        if not status_ativo and usuario_logado.id_usuario == usuario_alvo.id_usuario:
            raise ValueError("Voce nao pode desativar a propria conta.")

        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError(
                "Voce nao tem permissao para alterar status deste usuario."
            )

        if status_ativo == usuario_alvo.ativo:
            raise ValueError(
                f"Usuario ja esta {'ativo.' if status_ativo else 'desativado.'}"
            )

        usuario_alvo.ativo = status_ativo
        return self.usuario_repository.atualizar(usuario_alvo)

    def obter_papeis_cadastro(self, usuario_logado: Usuario) -> list[PapelUsuario]:
        if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
            return [PapelUsuario.FUNCIONARIO, PapelUsuario.GERENTE]
        elif usuario_logado.papel == PapelUsuario.GERENTE:
            return [PapelUsuario.FUNCIONARIO]
        else:
            raise PermissionError(
                "Funcionarios nao tem permissao para casdastrar usuarios"
            )

    def criar_admin_padrao(self) -> Usuario | None:
        if self.usuario_repository.existe_usuario():
            return None

        senha_do_ambiente = os.getenv("SENHA_PADRAO_FABRICA", "admin123")
        senha_hash = self.autenticacao_service.gerar_senha_hash(senha_do_ambiente)
        admin_padrao = Usuario(
            nome="admin", senha_hash=senha_hash, papel=PapelUsuario.ADMINISTRADOR
        )
        return self.usuario_repository.criar(admin_padrao)

    def _checar_id(self, id_usuario: int):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool):
            raise TypeError("ID tem que ser um numero inteiro.")

        if id_usuario <= 0:
            raise ValueError("ID de usuario invalido.")

    def listar_usuarios(
        self, usuario_logado: Usuario, status_ativo: bool = True
    ) -> list:
        if usuario_logado.papel == PapelUsuario.FUNCIONARIO:
            raise PermissionError(
                "Funcionarios nao tem permissao para listar funcionarios"
            )

        usuarios = self.usuario_repository.listar(status_ativo)

        if usuario_logado.papel == PapelUsuario.GERENTE:
            return [
                usuario
                for usuario in usuarios
                if usuario.papel == PapelUsuario.FUNCIONARIO
            ]

        return usuarios
