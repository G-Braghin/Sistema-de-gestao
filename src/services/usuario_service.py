from src.enums import PapelEnum
from src.models import Usuario
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.settings import Settings
from src.utils.validacoes import verificar_id, verificar_texto_obrigatorio


class UsuarioService:
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        autenticacao_service: AutenticacaoService,
    ):
        self.usuario_repository = usuario_repository
        self.autenticacao_service = autenticacao_service

    @staticmethod
    def pode_gerenciar(usuario_logado: Usuario, usuario_alvo: Usuario) -> bool:
        if usuario_logado.papel == PapelEnum.ADMIN:
            return True

        if usuario_logado.papel == PapelEnum.GERENTE:
            return usuario_alvo.papel == PapelEnum.FUNCIONARIO
        return False

    def cadastrar_usuario(
        self,
        usuario_logado: Usuario,
        dados_cadastro: Usuario,
    ) -> Usuario:
        papeis_permitidos = self.obter_papeis_cadastro(usuario_logado)

        if dados_cadastro.papel not in papeis_permitidos:
            raise PermissionError('Você não pode cadastrar esse cargo.')

        novo_user = dados_cadastro
        novo_user.senha = self.autenticacao_service.gerar_senha_hash(
            dados_cadastro.senha
        )
        novo_user = self.usuario_repository.criar(novo_user)
        self.usuario_repository.commit()
        return novo_user

    def promover_a_gerente(self, usuario_logado: Usuario, id_usuario: int) -> Usuario:
        if usuario_logado.papel != PapelEnum.ADMIN:
            raise PermissionError(
                'Apenas administradores podem promover funcionários a gerentes.'
            )
        verificar_id(id_usuario, 'ID de usuário invalido.')

        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError(f'Usuário com id {id_usuario} não encontrado.')

        if usuario.papel != PapelEnum.FUNCIONARIO:
            raise ValueError('Apenas funcionários podem ser promovidos a gerentes.')

        usuario = self.usuario_repository.atualizar(
            usuario.id, {'papel': PapelEnum.GERENTE}
        )

        self.usuario_repository.commit()
        return usuario

    def resetar_senha(
        self, usuario_logado: Usuario, id_usuario_alvo: int, nova_senha: str
    ) -> Usuario:
        verificar_id(id_usuario_alvo, 'ID de usuário invalido.')

        verificar_texto_obrigatorio(nova_senha, 'Senha não pode estar vazio.')

        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f'Usuário com id {id_usuario_alvo} não encontrado.')

        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError(
                'Você não tem permissão para resetar a senha deste usuário.'
            )

        nova_senha_hash = self.autenticacao_service.gerar_senha_hash(nova_senha)
        usuario = self.usuario_repository.atualizar(
            usuario_alvo.id, {'senha': nova_senha_hash}
        )
        self.usuario_repository.commit()
        return usuario

    def atualizar_status(
        self, usuario_logado: Usuario, id_usuario_alvo: int, status_ativo: bool
    ) -> Usuario:
        verificar_id(id_usuario_alvo, 'ID de usuário invalido.')

        if not isinstance(status_ativo, bool):
            raise TypeError('Status deve ser True ou False.')

        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f'Usuário com id {id_usuario_alvo} não encontrado.')

        if usuario_alvo.papel == PapelEnum.ADMIN:
            raise PermissionError(
                'Contas de administradores não podem ser ativadas ou '
                'desativas pelo sistema.'
            )

        if not status_ativo and usuario_logado.id == usuario_alvo.id:
            raise ValueError('Voce não pode desativar a própria conta.')

        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError(
                'Voce não tem permissão para alterar status deste usuário.'
            )

        if status_ativo == usuario_alvo.ativo:
            raise ValueError(
                f'Usuario ja esta {"ativo." if status_ativo else "desativado."}'
            )
        usuario = self.usuario_repository.atualizar(
            usuario_alvo.id, {'ativo': status_ativo}
        )
        self.usuario_repository.commit()

        return usuario

    @staticmethod
    def obter_papeis_cadastro(usuario_logado: Usuario) -> list[PapelEnum]:
        if usuario_logado.papel == PapelEnum.ADMIN:
            return [PapelEnum.FUNCIONARIO, PapelEnum.GERENTE]
        elif usuario_logado.papel == PapelEnum.GERENTE:
            return [PapelEnum.FUNCIONARIO]
        else:
            raise PermissionError(
                'funcionários não tem permissão para cadastrar usuários'
            )

    def criar_admin_padrao(self) -> Usuario | None:
        if self.usuario_repository.existe_usuario():
            return None

        senha_do_ambiente = Settings().SENHA_PADRAO_FABRICA
        senha_hash = self.autenticacao_service.gerar_senha_hash(senha_do_ambiente)
        admin_padrao = Usuario(nome='admin', senha=senha_hash, papel=PapelEnum.ADMIN)
        admin = self.usuario_repository.criar(admin_padrao)

        self.usuario_repository.commit()

        return admin

    def listar_usuarios(
        self, usuario_logado: Usuario, status_ativo: bool = True
    ) -> list:
        if usuario_logado.papel == PapelEnum.FUNCIONARIO:
            raise PermissionError(
                'Funcionarios não tem permissão para listar funcionarios'
            )

        usuarios = self.usuario_repository.listar(status_ativo)

        if usuario_logado.papel == PapelEnum.GERENTE:
            return [
                usuario
                for usuario in usuarios
                if usuario.papel == PapelEnum.FUNCIONARIO
            ]

        return usuarios
