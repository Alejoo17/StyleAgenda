from collections.abc import Generator
from sqlalchemy.orm import Session
from app.core.config import settings
from app.infrastructure.sqlite_database import SQLiteDatabase

database = SQLiteDatabase(settings.database_url)


def get_session() -> Generator[Session, None, None]:
    session = database.session()
    try: yield session
    finally: session.close()
