from contextlib import contextmanager
from datetime import datetime

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from src.enums import PapelEnum
from src.models import Base
from tests.clientes.conftest import ClienteFatory
from tests.produtos.conftest import ProductFactory
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


@pytest.fixture
def produto():
    product = ProductFactory()
    product.id = 99
    return product


# Definindo Fixture para testes que dependende de algo no banco
@pytest.fixture
def usuario_db(session):
    user_db = UserFactory(papel=PapelEnum.FUNCIONARIO)
    session.add(user_db)
    session.flush()

    return user_db


@pytest.fixture
def produto_db(session):
    product_db = ProductFactory()
    session.add(product_db)
    session.flush()

    return product_db


@pytest.fixture
def cliente_db(session):
    cliente_db = ClienteFatory()
    session.add(cliente_db)

    return cliente_db


# Definindo uma meneira de simular um horario para os testes
@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 10, 10)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
