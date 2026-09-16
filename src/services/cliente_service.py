import re

from src.entities.cliente import Cliente

class ClienteService:
    def __init__(self,cliente_repository):
        self.cliente_repository = cliente_repository

    def validar_cpf(self,cpf):
        if len(cpf) != 11: 
            return False

        if cpf == cpf[0] * 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        digito1 = 0 if resto == 10 else resto
    
        if digito1 != int(cpf[9]):
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        digito2 = 0 if resto == 10 else resto
    
        if digito2 != int(cpf[10]):
            return False
        
        return True

    def validar_telefone(self,telefone):
        padrao = r'^[1-9]{2}9[\d]{8}$'
        if re.match(padrao, telefone):
            return True
        return False

    def cadastrar_cliente(self, nome,cpf,telefone,endereco):
        cpf = re.sub(r'\D', '', cpf)
        telefone = re.sub(r'\D', '', telefone)

        if not nome.strip():
            raise ValueError ("O nome nao pode estar vazio.")

        if not cpf:
            raise ValueError ("O CPF nao pode estar vazio.")

        if not self.validar_cpf(cpf):
            raise ValueError ("O CPF e invalido!")

        cliente_existente = self.cliente_repository.buscar_por_cpf(cpf)
        if cliente_existente:
            raise ValueError("O CPF já está cadastrado.")
        
        if not telefone:
            raise ValueError ("O telefone nao pode estar vazio.")
        
        if not self.validar_telefone(telefone):
            raise ValueError ("O telefone e invalido!")

        novo_cliente = Cliente(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco
        )
        return self.cliente_repository.criar(novo_cliente)

    def atualizar_cliente(self,cliente):
        if not cliente.nome.strip():
            raise ValueError ("Nome nao pode estar vazio.")

        cpf = re.sub(r'\D', '', cliente.cpf)
        if not self.validar_cpf(cpf):
            raise ValueError ("O CPF e invalido!")

        telefone = re.sub(r'\D', '', cliente.telefone)
        if not self.validar_telefone(telefone):
            raise ValueError ("O telefone e invalido!")

        cliente.nome = cliente.nome.strip()
        cliente.cpf = cpf 
        cliente.telefone = telefone
        cliente.endereco = cliente.endereco.strip()

        return self.cliente_repository.atualizar(cliente)
