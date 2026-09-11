from src.entities.enums.papel_usuario import PapelUsuario

class Usuario:
    def __init__(self, nome, senha_hash, papel:PapelUsuario ,id_usuario=None, ativo=True):
        self.id_usuario = id_usuario
        self.nome = nome
        self.senha_hash = senha_hash
        self.papel = papel
        self.ativo = ativo

    def __str__(self):
        return f"Usuario(id_usuario={self.id_usuario}, nome={self.nome}, papel={self.papel}, ativo={self.ativo})"