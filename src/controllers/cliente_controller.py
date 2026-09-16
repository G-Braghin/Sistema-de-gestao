class ClienteController:
    def __init__(self,cliente_service):
        self.cliente_service = cliente_service

    def cadastrar_cliente(self,nome,cpf,telefone,endereco):
        try:
            cliente_novo = self.cliente_service.cadastrar_cliente(nome,cpf,telefone,endereco)
            print("cliente cadastrado com sucesso!")
            return cliente_novo
        except ValueError as e:
            print(f"{e}")
            return None

    def atualizar_telefone(self,cpf_cliente,telefone_novo):
        try:
            cliente=self.cliente_service.atualizar_telefone(cpf_cliente,telefone_novo)
            print(f"Telefone do cliente {cliente.nome} atualizado com sucesso!")
            return cliente
        except ValueError as e:
            print(f"Erro ao atualizar telefone: {e}")
            return None

    def atualizar_endereco(self,cpf_cliente,endereco_novo):
        try:
            cliente=self.cliente_service.atualizar_endereco(cpf_cliente,endereco_novo)
            print(f"Endereco do cliente {cliente.nome} atualizado com sucesso!")
            return cliente
        except ValueError as e:
            print(f"Erro ao atualizar endereco: {e}")
            return None