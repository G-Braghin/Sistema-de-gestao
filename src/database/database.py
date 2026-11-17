from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


@contextmanager
def get_session():
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    with get_session() as session:
        yield session
