import bcrypt
from src.repositories.usuario_repository import UsuarioRepository


class AutenticacaoService:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def autenticar(self, id_usuario: int, senha: str):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool):
            raise TypeError("ID tem que ser um numero inteiro.")

        if id_usuario <= 0:
            raise ValueError("ID de usuario invalido.")

        if not senha or not senha.strip():
            raise ValueError("Senha nao pode estar vazio.")
        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario or not self.verificar_senha(senha, usuario.senha_hash):
            raise ValueError("ID ou Senha Invalidos.")

        if not usuario.ativo:
            raise ValueError("Usuário inativo.")

        return usuario

    def gerar_senha_hash(self, senha: str):
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verificar_senha(self, senha: str, senha_hash: str):
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))

    def atualizar_senha_usuario(
        self, id_usuario: int, senha_atual: str, nova_senha: str
    ):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool):
            raise TypeError("ID tem que ser um numero inteiro.")

        if id_usuario <= 0:
            raise ValueError("ID de usuario invalido.")

        if not senha_atual or not senha_atual.strip():
            raise ValueError("A senha atual nao pode estar vazio.")

        if not nova_senha or not nova_senha.strip():
            raise ValueError("A nova senha nao pode estar vazio.")

        if senha_atual == nova_senha:
            raise ValueError("A nova senha nao pode ser igual a atual.")

        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        if not self.verificar_senha(senha_atual, usuario.senha_hash):
            raise ValueError("Senha atual incorreta.")

        nova_senha_hash = self.gerar_senha_hash(nova_senha)
        usuario.senha_hash = nova_senha_hash
        self.usuario_repository.atualizar(usuario)

        return usuario
