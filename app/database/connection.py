import os
import sqlite3
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = Path(os.getenv("BANKING_DB_PATH", APP_DIR / "data" / "banking.db"))


class Database:
    """Small SQLite connection/bootstrap boundary.

    Repositories ask this object for connections; services and workflows never
    import sqlite3 directly. A new connection is created per repository call,
    which keeps the local FastAPI demo simple and avoids sharing a SQLite
    connection across worker threads.
    """

    def __init__(self, path: Path | str = DEFAULT_DB_PATH) -> None:
        self.path = Path(path)
        self.schema_path = Path(__file__).with_name("schema.sql")
        self.seed_path = Path(__file__).with_name("seed.sql")

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(self.schema_path.read_text())
            connection.executescript(self.seed_path.read_text())
