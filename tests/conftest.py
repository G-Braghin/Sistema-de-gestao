import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from src.enums import PapelEnum
from src.models import Base
from tests.usuarios.conftest import UserFactory


@pytest.fixture(scope='session')
def db_container():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        yield postgres


@pytest.fixture(scope='session')
def engine(db_container):
    engine = create_engine(db_container.get_connection_url())
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def session(engine):
    conn = engine.connect()
    try:
        transacao = conn.begin()
        session = Session(conn)
        try:
            yield session
        finally:
            session.close()
            transacao.rollback()
    finally:
        conn.close()


# Definindo fixture de usuario logado
@pytest.fixture
def user_funcionario():
    user = UserFactory(papel=PapelEnum.FUNCIONARIO)
    user.id = 99
    return user


@pytest.fixture
def user_gerente():
    user = UserFactory(papel=PapelEnum.GERENTE)
    user.id = 99
    return user
