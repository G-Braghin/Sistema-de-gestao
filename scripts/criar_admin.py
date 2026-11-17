from src.database.database import get_session
from src.repositories.usuario_repository import UsuarioRepository
from src.services.autenticacao_service import AutenticacaoService
from src.services.usuario_service import UsuarioService


def main():
    with get_session() as session:
        usuario_repository = UsuarioRepository(session)
        autenticacao_service = AutenticacaoService(usuario_repository)

        usuario_service = UsuarioService(
            usuario_repository,
            autenticacao_service,
        )

        admin = usuario_service.criar_admin_padrao()

        if admin:
            print('Administrador padrão criado com sucesso!')
        else:
            print('Já existem usuários cadastrados. Nenhuma alteração realizada.')


if __name__ == '__main__':
    main()
