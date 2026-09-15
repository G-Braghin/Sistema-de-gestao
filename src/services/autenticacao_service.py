import bcrypt

class AutenticacaoService:
    def __init__(self, usuario_repository):
        self.usuario_repository = usuario_repository

    def autenticar(self, id_usuario, senha):
        if id_usuario <=0:
            raise ValueError("ID de usuario invalido.")

        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario or not self.verificar_senha(senha, usuario.senha_hash):
            raise ValueError("ID ou Senha Invalidos.")

        if not usuario.ativo:
            raise ValueError("Usuário inativo.")

        return usuario

    def gerar_senha_hash(self, senha):
        return bcrypt.hashpw(
            senha.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def verificar_senha(self, senha, senha_hash):
        return bcrypt.checkpw(
            senha.encode('utf-8'),
            senha_hash.encode('utf-8')
        )

    def atualizar_senha_usuario(self, id_usuario, senha_atual, nova_senha):
        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        if not self.verificar_senha(senha_atual, usuario.senha_hash):
            raise ValueError("Senha atual incorreta.")

        nova_senha_hash = self.gerar_senha_hash(nova_senha)
        usuario.senha_hash = nova_senha_hash
        self.usuario_repository.atualizar(usuario)

        return usuario