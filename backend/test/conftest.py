"""
conftest.py — ensures the DB schema is fresh before any test runs.
"""
import os
import sys

# Ensure backend/src is importable when running tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.database.session import engine
from app.models import Base


@pytest.fixture(autouse=True, scope="session")
def reset_schema():
    """Drop and recreate all tables once per test session to use latest schema."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
