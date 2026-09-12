from src.database.conexao import Conexao


def test_conexao():
    conexao = Conexao()

    assert conexao.get_connection() is not None

