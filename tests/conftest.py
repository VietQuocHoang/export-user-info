import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from config.app import app  # noqa: E402
from db.engine import get_engine  # noqa: E402
from models import Base, Organization, User  # noqa: E402
from models.users import StatusEnum  # noqa: E402


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(test_engine):
    app.dependency_overrides[get_engine] = lambda: test_engine
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(test_engine):
    with Session(test_engine) as session:
        org_a = Organization(
            name="Org A",
            org_config={
                "id": True,
                "org_id": True,
                "first_name": True,
                "last_name": True,
                "email": True,
                "department": True,
                "location": True,
            },
        )
        org_b = Organization(
            name="Org B",
            org_config={
                "id": True,
                "org_id": True,
                "first_name": True,
                "last_name": True,
                "location": True,
                "email": False,
                "department": False,
            },
        )
        session.add_all([org_a, org_b])
        session.flush()

        session.add_all(
            [
                User(
                    first_name="Alice",
                    last_name="Smith",
                    email="alice@example.com",
                    phone_number="111-111",
                    position="Engineer",
                    department="Engineering",
                    location="USA",
                    status=StatusEnum.ACTIVE,
                    org_id=org_a.id,
                ),
                User(
                    first_name="Bob",
                    last_name="Brown",
                    email="bob@example.com",
                    phone_number="222-222",
                    position="Manager",
                    department="Operations",
                    location="USA",
                    status=StatusEnum.TERMINATED,
                    org_id=org_a.id,
                ),
                User(
                    first_name="Charlie",
                    last_name="Davis",
                    email="charlie@example.com",
                    phone_number="333-333",
                    position="Analyst",
                    department="Finance",
                    location="Canada",
                    status=StatusEnum.ACTIVE,
                    org_id=org_b.id,
                ),
            ]
        )
        session.commit()

        return {"org_a": org_a.id, "org_b": org_b.id}
