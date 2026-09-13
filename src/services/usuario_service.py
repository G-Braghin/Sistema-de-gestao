from src.entities.usuario import Usuario
from src.entities.enums.papel_usuario import PapelUsuario

class UsuarioService:
    def __init__(self, usuario_repository, autenticacao_service):
        self.usuario_repository = usuario_repository
        self.autenticacao_service = autenticacao_service

    def pode_gerenciar(self, usuario_logado: Usuario, usuario_alvo: Usuario):
        if usuario_logado.papel == PapelUsuario.ADMINISTRADOR:
            return True
        if usuario_logado.papel == PapelUsuario.GERENTE:
            return usuario_alvo.papel == PapelUsuario.FUNCIONARIO
        return False

    def cadastrar_usuario(self, usuario_logado, nome, senha, papel: PapelUsuario = PapelUsuario.FUNCIONARIO):
        if usuario_logado.papel == PapelUsuario.GERENTE and papel != PapelUsuario.FUNCIONARIO:
            raise PermissionError("Gerentes só podem cadastrar funcionários.")
        if usuario_logado.papel not in (PapelUsuario.ADMINISTRADOR, PapelUsuario.GERENTE):
            raise PermissionError("Você não tem permissão para cadastrar usuários.")
        
        senha_hash = self.autenticacao_service.gerar_senha_hash(senha)
        novo_usuario = Usuario(
            nome=nome, 
            senha_hash=senha_hash, 
            papel=papel
        )
        return self.usuario_repository.criar(novo_usuario)

    def promover_a_gerente(self, usuario_logado, id_usuario):
        if usuario_logado.papel != PapelUsuario.ADMINISTRADOR:
            raise PermissionError("Apenas administradores podem promover funcionários a gerentes.")
        
        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuário com id {id_usuario} não encontrado.")
        
        if usuario.papel != PapelUsuario.FUNCIONARIO:
            raise ValueError("Apenas funcionários podem ser promovidos a gerentes.")
        
        usuario.papel = PapelUsuario.GERENTE
        return self.usuario_repository.atualizar(usuario)

    def resetar_senha(self, usuario_logado, id_usuario_alvo, nova_senha):
        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f"Usuário com id {id_usuario_alvo} não encontrado.")
        
        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError("Você não tem permissão para resetar a senha deste usuário.")
        
        nova_senha_hash = self.autenticacao_service.gerar_senha_hash(nova_senha)
        usuario_alvo.senha_hash = nova_senha_hash
        return self.usuario_repository.atualizar(usuario_alvo)
     
    def desativar_usuario(self, usuario_logado, id_usuario_alvo):
        usuario_alvo = self.usuario_repository.buscar_por_id(id_usuario_alvo)
        if not usuario_alvo:
            raise ValueError(f"Usuário com id {id_usuario_alvo} não encontrado.")
        
        if not self.pode_gerenciar(usuario_logado, usuario_alvo):
            raise PermissionError("Você não tem permissão para desativar este usuário.")
        
        usuario_alvo.ativo = False
        return self.usuario_repository.atualizar(usuario_alvo)   