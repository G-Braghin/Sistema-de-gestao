from jwt import decode

from src.api.security import criar_token


def test_jwt(user_funcionario, settings):
    token = criar_token(user_funcionario.id)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['sub'] == str(user_funcionario.id)
    assert 'exp' in decoded
