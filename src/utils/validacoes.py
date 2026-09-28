def verificar_id(id_registro: int, mensagem: str = "ID invalido.") -> None:
    if not isinstance(id_registro, int) or isinstance(id_registro, bool):
        raise TypeError("ID tem que ser um numero inteiro.")

    if id_registro <= 0:
        raise ValueError(mensagem)


def verificar_texto_obrigatorio(texto: str | None, mensagem: str) -> None:
    if not texto or not texto.strip():
        raise ValueError(mensagem)
