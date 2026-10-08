"""
Test configuration.

Sets DATABASE_URL to an in-memory SQLite database so tests don't
require PostgreSQL and run completely in isolation.

Also ensures tables are created before each test module that needs them.
"""

from __future__ import annotations

import os
import pytest

# Force in-memory SQLite for all tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_cryptomaka.db")
os.environ.setdefault("APP_ENV", "test")


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create database tables once per test session."""
    from cryptomaka.database.session import Base, engine
    # Import models so SQLAlchemy registers them
    import cryptomaka.database.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up test DB file
    Base.metadata.drop_all(bind=engine)
    import pathlib
    db_path = pathlib.Path("test_cryptomaka.db")
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass
