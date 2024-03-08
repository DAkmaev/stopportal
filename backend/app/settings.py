import enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_file: Path = "../db.sqlite3"
    db_echo: bool = False
    postgres_server: str = "localhost"
    postgres_user: str = "stopportal_user"
    postgres_password: str = "stopportal_password"
    postgres_db: str = "stopportal"

    access_token_expire_minutes: int = 60 * 24 * 8
    api_v1_str: str = "/api"
    algorithm: str = "HS256"
    secret_key: str = "sdsdsdw34fdfwr2efdfwe2"  # secrets.token_urlsafe(32)

    first_superuser: str = "admin"
    first_superuser_password: str = "changethis"

    bot_token: str = ""
    chat_id: str = ""

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        if self.environment not in {"prod", "test"}:
            return URL.build(
                scheme="sqlite+aiosqlite",
                path=f"///{self.db_file}",
            )

        url_scheme = "postgresql+psycopg"
        url_account = f"{self.postgres_user}:{self.postgres_password}"
        url_db = f"{self.postgres_server}/{self.postgres_db}"
        url_path = f"//{url_account}@{url_db}"
        return URL.build(scheme=url_scheme, path=url_path)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_",
        env_file_encoding="utf-8",
    )


settings = Settings()
