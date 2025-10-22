import os
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine


def _build_engine():
    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, connect_args=connect_args)


engine = _build_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_context():
    with Session(engine) as session:
        yield session


def get_session():
    with Session(engine) as session:
        yield session
