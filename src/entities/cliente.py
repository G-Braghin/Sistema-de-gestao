class Cliente:
    def __init__(
        self,
        nome: str,
        cpf: str,
        telefone: str,
        endereco: str,
        id_cliente: int | None = None,
    ):
        self.id_cliente = id_cliente
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco

    def __str__(self):
        return f"Cliente(id_cliente={self.id_cliente}, nome={self.nome}, cpf={self.cpf}, telefone={self.telefone}, endereco={self.endereco})"
