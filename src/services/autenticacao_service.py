import bcrypt

from src.repositories.usuario_repository import UsuarioRepository
from src.utils.validacoes import verificar_id, verificar_texto_obrigatorio


class AutenticacaoService:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    @staticmethod
    def gerar_senha_hash(senha: str):
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str):
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))

    def autenticar(self, id_usuario: int, senha: str):
        verificar_id(id_usuario, 'ID de usuario invalido.')

        verificar_texto_obrigatorio(senha, 'Senha nao pode estar vazio.')
        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario or not self.verificar_senha(senha, usuario.senha):
            raise ValueError('ID ou Senha Invalidos.')

        if not usuario.ativo:
            raise ValueError('Usuário inativo.')

        return usuario

    def atualizar_senha_usuario(
        self, id_usuario: int, senha_atual: str, nova_senha: str
    ):
        verificar_id(id_usuario, 'ID de usuario invalido.')

        verificar_texto_obrigatorio(senha_atual, 'A senha atual nao pode estar vazio.')

        verificar_texto_obrigatorio(nova_senha, 'A nova senha nao pode estar vazio.')

        if senha_atual == nova_senha:
            raise ValueError('A nova senha nao pode ser igual a atual.')

        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError('Usuário não encontrado.')

        if not self.verificar_senha(senha_atual, usuario.senha):
            raise ValueError('Senha atual incorreta.')

        nova_senha_hash = self.gerar_senha_hash(nova_senha)
        return self.usuario_repository.atualizar(usuario.id, {'senha': nova_senha_hash})
