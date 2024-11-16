"""app models."""

import pkgutil
from pathlib import Path


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="backend.app.db.models.",
    )
    for module in modules:
        print(f"-------{module.name}")
        __import__(module.name)  # noqa: WPS421
