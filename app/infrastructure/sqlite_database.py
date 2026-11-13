from threading import Lock
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker


class SQLiteDatabase:
    """Singleton del motor y sessionmaker; una sesión nueva por unidad de trabajo."""
    _instance: "SQLiteDatabase | None" = None
    _lock = Lock()

    def __new__(cls, database_url: str | None = None):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
        return cls._instance

    def __init__(self, database_url: str | None = None):
        if self._initialized:
            if database_url and database_url != self.database_url:
                raise RuntimeError("SQLiteDatabase ya fue inicializada con otra URL")
            return
        self.database_url = database_url or "sqlite:///./data/styleagenda.db"
        connect_args = {"check_same_thread": False} if self.database_url.startswith("sqlite") else {}
        self.engine = create_engine(self.database_url, connect_args=connect_args, future=True)
        if self.database_url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def _enable_foreign_keys(dbapi_connection, _record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        self.session_factory = sessionmaker(bind=self.engine, class_=Session, expire_on_commit=False)
        self._initialized = True

    def session(self) -> Session:
        return self.session_factory()

    def create_schema(self) -> None:
        from app.infrastructure.orm import Base  # importa todos los modelos
        Base.metadata.create_all(self.engine)

    def dispose(self) -> None:
        self.engine.dispose()

    @classmethod
    def reset_for_tests(cls) -> None:
        """Libera recursos y permite aislar pruebas que usan URLs diferentes."""
        with cls._lock:
            if cls._instance is not None and cls._instance._initialized:
                cls._instance.dispose()
            cls._instance = None
