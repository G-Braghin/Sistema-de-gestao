class UsuarioController:
    def __init__(self, usuario_service, autenticacao_service):
        self.usuario_service = usuario_service
        self.autenticacao_service = autenticacao_service

    def fazer_login(self,id_usuario, senha):
        try:
            usuario = self.autenticacao_service.autenticar(id_usuario,senha)
            print(f"Usuario autenticado: {usuario.nome}")
            return usuario
        except ValueError as e:
            print(f"Erro ao autenticar usuario: {e}")
            return None

    def cadastrar_usuario(self, usuario_logado, nome, senha, papel):
        try:
            usuario_novo=self.usuario_service.cadastrar_usuario(usuario_logado, nome, senha, papel)
            print(f"funcionario cadastrado com sucesso! ID de acesso: {usuario_novo.id_usuario}")
            return usuario_novo
        except PermissionError as e:
            print(f"Erro de permissão: {e}")
            return None

    def promover_gerente(self, usuario_logado,id_usuario_alvo):
        try:
            usuario_promovido=self.usuario_service.promover_a_gerente(usuario_logado,id_usuario_alvo)
            print(f"{usuario_promovido.nome} promovido a Gerente!")
            return usuario_promovido
        except (PermissionError,ValueError) as e:
            print(f"Erro de permissao: {e}")
            return None

    def resetar_senha(self,usuario_logado,id_usuario_alvo,nova_senha):
        try:
            usuario_alvo=self.usuario_service.resetar_senha(usuario_logado,id_usuario_alvo,nova_senha)
            print(f"Nova senha para {usuario_alvo.nome} foi feito com Sucesso!")
            return usuario_alvo
        except (ValueError, PermissionError) as e:
            print(f"Erro ao resetar a senha: {e}")
            return None

    def desativar_usuario(self,usuario_logado,id_usuario_alvo):
        try:
            usuario_alvo=self.usuario_service.desativar_usuario(usuario_logado,id_usuario_alvo)
            print(f"Conta do usuario {usuario_alvo.nome} desativada com Sucesso!")
            return usuario_alvo
        except (ValueError, PermissionError) as e:
            print(f"Erro ao tentar desativar usuario {e}")
            return None

    def atualizar_senha_usuario(self,usuario_logado,senha_atual,senha_nova):
        try:
            self.autenticacao_service.atualizar_senha_usuario(usuario_logado.id_usuario,senha_atual,senha_nova)
            print("Senha atualizada com sucesso.")
            return True
        except ValueError as e:
            print(f"Erro ao atualizar a senha: {e}")
            return False

    def opcoes_cadastro(self,usuario_logado):
        papeis = self.usuario_service.obter_papeis_cadastro(usuario_logado)
        return[(i,papel.value) for i,papel in enumerate(papeis,start=1)]
    
    def papel_da_opcao_cadastro(self, usuario_logado, opcao):
        papeis = self.usuario_service.obter_papeis_cadastro(usuario_logado)
        try:
            return papeis[int(opcao) - 1]
        except (ValueError, IndexError):
            return None    

    def garantir_admin_padrao(self):
        usuario=self.usuario_service.criar_admin_padrao()
        if usuario:
            print(f"Administrador padrao criado! ID de acesso: {usuario.id_usuario}")
        return usuario
            