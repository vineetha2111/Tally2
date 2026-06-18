"""SQLAlchemy engine and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings, get_settings
from app.exceptions.errors import DatabaseError

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine(settings: Settings | None = None) -> Engine:
    """Return a singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        cfg = settings or get_settings()
        _engine = create_engine(
            cfg.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    """Return a singleton session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(settings),
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


@contextmanager
def get_db_session(settings: Settings | None = None) -> Generator[Session, None, None]:
    """Provide a transactional database session."""
    session = get_session_factory(settings)()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        raise DatabaseError(f"Database session error: {exc}") from exc
    finally:
        session.close()


def check_database_connection(settings: Settings | None = None) -> bool:
    """Verify PostgreSQL connectivity."""
    try:
        with get_engine(settings).connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        raise DatabaseError(f"Cannot connect to PostgreSQL: {exc}") from exc
