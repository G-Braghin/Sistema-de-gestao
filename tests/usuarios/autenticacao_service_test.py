from src.services.autenticacao_service import AutenticacaoService
import bcrypt

def test_gerar_e_verificar_senha():
    service = AutenticacaoService(None)

    senha_hash = service.gerar_senha_hash("123456")

    assert senha_hash != "123456"
    assert service.verificar_senha("123456", senha_hash)
    assert not service.verificar_senha("654321", senha_hash)

def test_autenticar_usuario_inativo():
    senha_hash_valida = bcrypt.hashpw("senha".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    class MockUsuarioRepository:
        def buscar_por_id(self, id_usuario):
            return type('Usuario', (object,), {
                'id_usuario': 1,
                'senha_hash': senha_hash_valida,
                'ativo': False
            })()

    mock_repo = MockUsuarioRepository()
    service = AutenticacaoService(mock_repo)

    try:
        service.autenticar(1, "senha")
        assert False, "Deveria ter lançado ValueError para usuário inativo"
    except ValueError as e:
        assert str(e) == "Usuário inativo."

def _criar_mock_com_senha(senha):
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return type('Usuario', (object,), {
        'id_usuario': 1,
        'senha_hash': senha_hash,
        'ativo': True
    })()


def test_atualizar_senha_usuario_sucesso():
    usuario_mock = _criar_mock_com_senha("senha_antiga")

    class MockUsuarioRepository:
        def buscar_por_id(self, id_usuario):
            return usuario_mock
        def atualizar(self, usuario):
            return usuario

    service = AutenticacaoService(MockUsuarioRepository())
    resultado = service.atualizar_senha_usuario(1, "senha_antiga", "senha_nova")

    assert service.verificar_senha("senha_nova", resultado.senha_hash)
    assert not service.verificar_senha("senha_antiga", resultado.senha_hash)


def test_atualizar_senha_usuario_com_senha_atual_errada():
    usuario_mock = _criar_mock_com_senha("senha_antiga")

    class MockUsuarioRepository:
        def buscar_por_id(self, id_usuario):
            return usuario_mock

    service = AutenticacaoService(MockUsuarioRepository())

    try:
        service.atualizar_senha_usuario(1, "senha_errada", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == "Senha atual incorreta."


def test_atualizar_senha_usuario_nao_encontrado():
    class MockUsuarioRepository:
        def buscar_por_id(self, id_usuario):
            return None

    service = AutenticacaoService(MockUsuarioRepository())

    try:
        service.atualizar_senha_usuario(999, "qualquer", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == "Usuário não encontrado."


def test_autenticar_com_id_zero():
    service = AutenticacaoService(None)

    try:
        service.autenticar(0, "senha")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'ID de usuario invalido.'


def test_autenticar_com_id_negativo():
    service = AutenticacaoService(None)

    try:
        service.autenticar(-1, "senha")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'ID de usuario invalido.'


def test_autenticar_com_id_texto():
    service = AutenticacaoService(None)

    try:
        service.autenticar("abc", "senha")
        assert False, "Deveria ter lançado TypeError"
    except TypeError as e:
        assert str(e) == 'ID tem que ser um numero inteiro.'


def test_autenticar_com_id_bool():
    service = AutenticacaoService(None)

    try:
        service.autenticar(True, "senha")
        assert False, "Deveria ter lançado TypeError"
    except TypeError as e:
        assert str(e) == 'ID tem que ser um numero inteiro.'


def test_atualizar_senha_usuario_com_id_zero():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(0, "senha_antiga", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'ID de usuario invalido.'


def test_atualizar_senha_usuario_com_id_negativo():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(-1, "senha_antiga", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'ID de usuario invalido.'


def test_atualizar_senha_usuario_com_id_texto():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario("abc", "senha_antiga", "senha_nova")
        assert False, "Deveria ter lançado TypeError"
    except TypeError as e:
        assert str(e) == 'ID tem que ser um numero inteiro.'


def test_atualizar_senha_usuario_com_id_bool():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(True, "senha_antiga", "senha_nova")
        assert False, "Deveria ter lançado TypeError"
    except TypeError as e:
        assert str(e) == 'ID tem que ser um numero inteiro.'


def test_autenticar_com_senha_vazia():
    service = AutenticacaoService(None)

    try:
        service.autenticar(1, "")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'Senha nao pode estar vazio.'


def test_autenticar_com_senha_com_espacos():
    service = AutenticacaoService(None)

    try:
        service.autenticar(1, "   ")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'Senha nao pode estar vazio.'


def test_autenticar_com_senha_none():
    service = AutenticacaoService(None)

    try:
        service.autenticar(1, None)
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'Senha nao pode estar vazio.'


def test_atualizar_senha_usuario_com_senha_atual_vazia():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, "", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A senha atual nao pode estar vazio.'


def test_atualizar_senha_usuario_com_senha_atual_com_espacos():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, "   ", "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A senha atual nao pode estar vazio.'


def test_atualizar_senha_usuario_com_senha_atual_none():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, None, "senha_nova")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A senha atual nao pode estar vazio.'


def test_atualizar_senha_usuario_com_nova_senha_vazia():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, "senha_antiga", "")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A nova senha nao pode estar vazio.'


def test_atualizar_senha_usuario_com_nova_senha_com_espacos():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, "senha_antiga", "   ")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A nova senha nao pode estar vazio.'


def test_atualizar_senha_usuario_com_nova_senha_none():
    service = AutenticacaoService(None)

    try:
        service.atualizar_senha_usuario(1, "senha_antiga", None)
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == 'A nova senha nao pode estar vazio.'


def test_atualizar_senha_usuario_com_nova_senha_igual_a_atual():
    usuario_mock = _criar_mock_com_senha("senha_atual")
    senha_hash_anterior = usuario_mock.senha_hash

    class MockUsuarioRepository:
        def buscar_por_id(self, id_usuario):
            return usuario_mock

        def atualizar(self, usuario):
            assert False, "Nao deveria atualizar a senha"

    service = AutenticacaoService(MockUsuarioRepository())

    try:
        service.atualizar_senha_usuario(1, "senha_atual", "senha_atual")
        assert False, "Deveria ter lançado ValueError"
    except ValueError as e:
        assert str(e) == "A nova senha nao pode ser igual a atual."

    assert usuario_mock.senha_hash == senha_hash_anterior
