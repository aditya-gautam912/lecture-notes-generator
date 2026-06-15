import pytest
import os
import tempfile
from fastapi.testclient import TestClient

os.environ["GROQ_API_KEY"] = "test-key"
os.environ["TESTING"] = "1"

from main import app
import database

TEST_DB = "sqlite:///./test_lectures.db"

@pytest.fixture(autouse=True)
def override_db():
    original_engine = database.engine
    from sqlalchemy import create_engine
    database.engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
    database.SessionLocal = database.sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield
    database.Base.metadata.drop_all(bind=database.engine)
    database.engine = original_engine
    database.SessionLocal = database.sessionmaker(autocommit=False, autoflush=False, bind=original_engine)

@pytest.fixture
def client():
    return TestClient(app)
