import os
import importlib

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path}"
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    os.environ["LOG_FILE"] = str(tmp_path / "audit_trail.log")

    import src.main as main
    importlib.reload(main)

    with TestClient(main.app) as test_client:
        yield test_client
