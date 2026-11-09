from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    with Session(engine, expire_on_commit=False) as session, session.begin():
        yield session
