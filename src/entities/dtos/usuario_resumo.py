from src.entities.enums.papel_usuario import PapelUsuario


class UsuarioResumo:
    def __init__(self, id_usuario: int, nome: str, papel: PapelUsuario, ativo: bool):
        self.id_usuario = id_usuario
        self.nome = nome
        self.papel = papel
        self.ativo = ativo
