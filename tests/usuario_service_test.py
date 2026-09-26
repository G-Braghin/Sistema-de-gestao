import pytest

from src.entities.usuario import Usuario
from src.entities.enums.papel_usuario import PapelUsuario
from src.services.usuario_service import UsuarioService

class FakeUsuarioRepository:

    def __init__(self):
        self.usuarios = {}
        self.proximo_id = 1

    def criar(self, usuario):
        usuario.id_usuario = self.proximo_id
        self.usuarios[self.proximo_id] = usuario
        self.proximo_id += 1
        return usuario

    def buscar_por_id(self, id_usuario):
        return self.usuarios.get(id_usuario)

    def atualizar(self, usuario):
        self.usuarios[usuario.id_usuario] = usuario
        return usuario

class FakeAutenticacaoService:

    def gerar_senha_hash(self, senha):
        return f"hash_{senha}"

@pytest.fixture
def service():
    repository = FakeUsuarioRepository()
    autenticacao = FakeAutenticacaoService()

    return UsuarioService(
        usuario_repository=repository,
        autenticacao_service=autenticacao
    )

#teste pode_gerenciar
def test_admin_pode_gerenciar(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO
    )

    assert service.pode_gerenciar(admin, funcionario) is True


def test_gerente_pode_gerenciar_funcionario(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO
    )

    assert service.pode_gerenciar(gerente, funcionario) is True

def test_gerente_nao_pode_gerenciar_gerente(service):
    gerente1 = Usuario(
        nome="Gerente 1",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    gerente2 = Usuario(
        nome="Gerente 2",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    assert service.pode_gerenciar(gerente1, gerente2) is False

def test_gerente_nao_pode_gerenciar_admin(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR
    )

    assert service.pode_gerenciar(gerente, admin) is False

def test_funcionario_nao_pode_gerenciar(service):
    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO
    )

    outro_funcionario = Usuario(
        nome="Outro",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO
    )

    assert service.pode_gerenciar(funcionario, outro_funcionario) is False

#testar cadastrar_usuario
def test_gerente_pode_cadastrar_funcionario(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    usuario = service.cadastrar_usuario(
        gerente,
        "Joao",
        "123456"
    )

    assert usuario.id_usuario is not None
    assert usuario.nome == "Joao"
    assert usuario.papel == PapelUsuario.FUNCIONARIO
    assert usuario.senha_hash == "hash_123456"

def test_gerente_nao_pode_cadastrar_gerente(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    with pytest.raises(PermissionError):
        service.cadastrar_usuario(
            gerente,
            "Joao",
            "123456",
            PapelUsuario.GERENTE
        )

def test_funcionario_nao_pode_cadastrar_usuario(service):
    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO
    )

    with pytest.raises(PermissionError):
        service.cadastrar_usuario(
            funcionario,
            "Joao",
            "123456"
        )

#testar promover_a_gerente
def test_admin_pode_promover_funcionario(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1
    )

    service.usuario_repository.usuarios[1] = funcionario

    resultado = service.promover_a_gerente(
        admin,
        1
    )

    assert resultado.papel == PapelUsuario.GERENTE

def test_gerente_nao_pode_promover(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1
    )

    service.usuario_repository.usuarios[1] = funcionario

    with pytest.raises(PermissionError):
        service.promover_a_gerente(
            gerente,
            1
        )

#testar resetar_senha
def test_gerente_pode_resetar_senha_de_funcionario(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE,
        id_usuario=1
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2
    )

    service.usuario_repository.usuarios[2] = funcionario

    resultado = service.resetar_senha(
        gerente,
        2,
        "nova_senha"
    )

    assert resultado.senha_hash == "hash_nova_senha"

def test_gerente_nao_pode_resetar_senha_de_gerente(service):
    gerente_logado = Usuario(
        nome="Gerente 1",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    gerente_alvo = Usuario(
        nome="Gerente 2",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE,
        id_usuario=2
    )

    service.usuario_repository.usuarios[2] = gerente_alvo

    with pytest.raises(PermissionError):
        service.resetar_senha(
            gerente_logado,
            2,
            "nova_senha"
        )

#testar desativar_usuario
def test_gerente_pode_desativar_funcionario(service):
    gerente = Usuario(
        nome="Gerente",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2,
        ativo=True
    )

    service.usuario_repository.usuarios[2] = funcionario

    resultado = service.desativar_usuario(
        gerente,
        2
    )

    assert resultado.ativo is False

def test_gerente_nao_pode_desativar_gerente(service):
    gerente1 = Usuario(
        nome="Gerente 1",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE
    )

    gerente2 = Usuario(
        nome="Gerente 2",
        senha_hash="hash",
        papel=PapelUsuario.GERENTE,
        id_usuario=2
    )

    service.usuario_repository.usuarios[2] = gerente2

    with pytest.raises(PermissionError):
        service.desativar_usuario(
            gerente1,
            2
        )


def test_cadastrar_usuario_com_nome_vazio(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='O nome nao pode estar vazio.'):
        service.cadastrar_usuario(admin, "", "123456")

    assert service.usuario_repository.usuarios == {}


def test_cadastrar_usuario_com_nome_com_espacos(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='O nome nao pode estar vazio.'):
        service.cadastrar_usuario(admin, "   ", "123456")

    assert service.usuario_repository.usuarios == {}


def test_cadastrar_usuario_com_nome_none(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='O nome nao pode estar vazio.'):
        service.cadastrar_usuario(admin, None, "123456")

    assert service.usuario_repository.usuarios == {}


def test_cadastrar_usuario_com_senha_vazio(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='Senha nao pode estar vazio.'):
        service.cadastrar_usuario(admin, "Joao", "")

    assert service.usuario_repository.usuarios == {}


def test_cadastrar_usuario_com_senha_com_espacos(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='Senha nao pode estar vazio.'):
        service.cadastrar_usuario(admin, "Joao", "   ")

    assert service.usuario_repository.usuarios == {}


def test_cadastrar_usuario_com_senha_none(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(ValueError, match='Senha nao pode estar vazio.'):
        service.cadastrar_usuario(admin, "Joao", None)

    assert service.usuario_repository.usuarios == {}


def test_admin_nao_pode_cadastrar_administrador(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    with pytest.raises(PermissionError, match="Você não pode cadastrar esse cargo"):
        service.cadastrar_usuario(
            admin, "Outro Admin", "123456", PapelUsuario.ADMINISTRADOR
        )

    assert service.usuario_repository.usuarios == {}


def test_promover_a_gerente_com_id_zero(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.promover_a_gerente(admin, 0)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_promover_a_gerente_com_id_negativo(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.promover_a_gerente(admin, -1)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_promover_a_gerente_com_id_texto(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.promover_a_gerente(admin, "abc")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_promover_a_gerente_com_id_bool(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.promover_a_gerente(admin, True)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_resetar_senha_com_id_zero(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.resetar_senha(admin, 0, "nova_senha")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_resetar_senha_com_id_negativo(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.resetar_senha(admin, -1, "nova_senha")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_resetar_senha_com_id_texto(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.resetar_senha(admin, "abc", "nova_senha")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_resetar_senha_com_id_bool(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.resetar_senha(admin, True, "nova_senha")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_desativar_usuario_com_id_zero(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.desativar_usuario(admin, 0)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_desativar_usuario_com_id_negativo(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(ValueError, match='ID de usuario invalido.'):
        service.desativar_usuario(admin, -1)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_desativar_usuario_com_id_texto(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.desativar_usuario(admin, "abc")

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_desativar_usuario_com_id_bool(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    alvo = Usuario(
        nome="Alvo",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=1,
        ativo=True
    )
    admin.id_usuario = 10
    service.usuario_repository.usuarios[1] = alvo

    with pytest.raises(TypeError, match='ID tem que ser um numero inteiro.'):
        service.desativar_usuario(admin, True)

    assert alvo.papel == PapelUsuario.FUNCIONARIO
    assert alvo.senha_hash == "hash_antigo"
    assert alvo.ativo is True


def test_resetar_senha_com_nova_senha_vazia(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2,
        ativo=True
    )
    service.usuario_repository.usuarios[2] = funcionario

    with pytest.raises(ValueError, match="Senha nao pode estar vazio"):
        service.resetar_senha(admin, 2, "")

    assert funcionario.senha_hash == "hash_antigo"


def test_resetar_senha_com_nova_senha_com_espacos(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2,
        ativo=True
    )
    service.usuario_repository.usuarios[2] = funcionario

    with pytest.raises(ValueError, match="Senha nao pode estar vazio"):
        service.resetar_senha(admin, 2, "   ")

    assert funcionario.senha_hash == "hash_antigo"


def test_resetar_senha_com_nova_senha_none(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2,
        ativo=True
    )
    service.usuario_repository.usuarios[2] = funcionario

    with pytest.raises(ValueError, match="Senha nao pode estar vazio"):
        service.resetar_senha(admin, 2, None)

    assert funcionario.senha_hash == "hash_antigo"


def test_admin_nao_pode_desativar_propria_conta(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    service.usuario_repository.usuarios[1] = admin

    with pytest.raises(ValueError, match="Voce nao pode desativar a propria conta"):
        service.desativar_usuario(admin, 1)

    assert admin.ativo is True


def test_desativar_usuario_ja_desativado(service):
    admin = Usuario(
        nome="Admin",
        senha_hash="hash",
        papel=PapelUsuario.ADMINISTRADOR,
        id_usuario=1
    )

    funcionario = Usuario(
        nome="Funcionario",
        senha_hash="hash_antigo",
        papel=PapelUsuario.FUNCIONARIO,
        id_usuario=2,
        ativo=True
    )
    service.usuario_repository.usuarios[2] = funcionario

    funcionario.ativo = False

    with pytest.raises(ValueError, match="Usuario ja esta desativado"):
        service.desativar_usuario(admin, 2)

    assert funcionario.ativo is False
