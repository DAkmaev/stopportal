import os

from backend.app.settings import settings


async def create_database() -> None:
    """Create a database."""


async def drop_database() -> None:
    """Drop current database."""
    if settings.db_test_file.exists():
        os.remove(settings.db_test_file)
