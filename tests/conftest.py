import os

import pytest

# Skip heavy index build when running the test suite
os.environ.setdefault("SKIP_INDEX_BUILD", "1")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.main.initialize_vector_index", lambda: None)
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
