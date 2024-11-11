import enum
from pathlib import Path

from pydantic_settings import BaseSettings


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_file: Path = "database.db"
    db_test_file: Path = "database_test.db"
    db_server: str = "localhost"
    db_user: str = "stopportal_user"
    db_password: str = "stopportal_password"
    db_name: str = "stopportal"
    db_port: int = 5433

    access_token_expire_minutes: int = 60 * 24 * 8
    api_v1_str: str = "/api"
    algorithm: str = "HS256"
    secret_key: str = "sdsdsdw34fdfwr2efdfwe2"  # secrets.token_urlsafe(32)

    broker_url: str = "redis://localhost:6379/0"

    @property
    def db_url(self) -> str:
        return self.generate_url()

    @property
    def db_test_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_test_file}"

    def generate_url(self):
        if self.environment not in {"prod", "test"}:
            return f"sqlite+aiosqlite:///{self.db_file}"

        url_scheme = "postgresql+psycopg"
        url_account = f"{self.db_user}:{self.db_password}"
        url_db = f"{self.db_server}:{self.db_port}/{self.db_name}"
        return f"{url_scheme}://{url_account}@{url_db}"


settings = Settings()
