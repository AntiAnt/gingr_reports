import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytz


@dataclass
class SessionTokens:
    id: int
    refresh_token: str
    access_token: str
    realm_id: int
    created_on: datetime
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime

    def is_access_token_expired(self) -> bool:
        return datetime.now(tz=pytz.utc) >= self.access_token_expires_at

    def is_refresh_token_expired(self) -> bool:
        return datetime.now(tz=pytz.utc) >= self.refresh_token_expires_at


class AuthDBManager(ABC):
    @abstractmethod
    def put_session_tokens(
        self, access_token: str, refresh_token: str, realm_id: int
    ) -> int: ...

    @abstractmethod
    def get_latest_session_tokens(self) -> SessionTokens | None: ...

    @abstractmethod
    def update_session_tokens_access_token(self, id: int, access_token: str) -> int: ...


class SQLiteAuthManager(AuthDBManager):
    auth_table_schema = """
            CREATE TABLE IF NOT EXISTS intuit_auth_session_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                realm_id INTEGER NOT NULL,
                created_on DATETIME NOT NULL,
                access_token_expires_at DATETIME NOT NULL,
                refresh_token_expires_at DATETIME NOT NULL
            )
        """

    def __init__(self) -> None:
        self.database_name = "./intuit_auth.db"
        conn = sqlite3.connect(self.database_name)

        conn.execute(self.auth_table_schema)
        conn.commit()
        conn.close()

    def put_session_tokens(
        self, access_token: str, refresh_token: str, realm_id: int
    ) -> int:
        timestamp = datetime.now(tz=pytz.utc)
        conn = sqlite3.connect(self.database_name)
        _id = conn.execute(
            """INSERT INTO intuit_auth_session_tokens 
                (access_token, refresh_token, realm_id, created_on, access_token_expires_at, refresh_token_expires_at) 
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                access_token,
                refresh_token,
                realm_id,
                timestamp,
                timestamp + timedelta(minutes=60),
                timestamp + timedelta(hours=24),
            ),
        ).lastrowid

        conn.commit()
        conn.close()
        return _id

    def update_session_tokens_access_token(self, id: int, access_token: str) -> int:
        timestamp = datetime.now(tz=pytz.utc)
        conn = sqlite3.connect(self.database_name)
        c = conn.execute(
            """
                UPDATE 
                    intuit_auth_session_tokens
                SET
                    access_token=?,
                    access_token_expires_at=?
                WHERE 
                    id=?
            """,
            (access_token, timestamp + timedelta(minutes=60), id),
        )

        conn.commit()
        conn.close()
        return c.rowcount

    def get_latest_session_tokens(self) -> SessionTokens | None:
        conn = sqlite3.connect(self.database_name)
        row = conn.execute(
            "SELECT * FROM intuit_auth_session_tokens ORDER BY created_on DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row is None:
            return

        return SessionTokens(
            id=row[0],
            access_token=row[1],
            refresh_token=row[2],
            realm_id=row[3],
            created_on=datetime.fromisoformat(row[4]),
            access_token_expires_at=datetime.fromisoformat(row[5]),
            refresh_token_expires_at=datetime.fromisoformat(row[6]),
        )


def get_auth_manager() -> AuthDBManager:
    return SQLiteAuthManager()
