from pydantic import BaseModel


class AtualizarStatus(BaseModel):
    ativo: bool


class Mensagem(BaseModel):
    mensagem: str
