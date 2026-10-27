import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from src.models import Base


@pytest.fixture(scope='session')
def db_container():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        yield postgres


@pytest.fixture(scope='session')
def engine(db_container):
    engine = create_engine(db_container.get_connection_url())
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    conn = engine.connect()
    transacao = conn.begin()

    session = Session(conn)

    yield session
    session.close()
    transacao.rollback()
    conn.close()
