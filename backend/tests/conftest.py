import os
import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Settings
from app.models import Base
from app.main import create_app

@pytest.fixture
def setup(tmp_path):
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    settings = Settings(database_url=url, secret_key="test-secret-" * 5,
        admin_password_hash=PasswordHasher().hash("test-password-long"),
        public_origin="http://testserver", secure_cookies=False,
        leads_enabled=True, privacy_version="test-v1", lead_limit=3)
    app = create_app(settings, engine)
    with TestClient(app) as client:
        yield client, sessionmaker(engine), settings
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def payload():
    return {"name": "Степан", "contact": "client@example.com", "service": "rail",
            "message": "Нужна разгрузка вагона", "consent": True}
