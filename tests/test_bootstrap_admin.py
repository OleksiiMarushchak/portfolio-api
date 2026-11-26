from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import settings
from app.db.base import get_db
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        settings,
        "BOOTSTRAP_ADMIN_SECRET",
        SecretStr("x" * 32),
    )
    db = AsyncMock()
    db.scalar.return_value = None

    def add_user(user):
        user.id = 1

    db.add = Mock(side_effect=add_user)

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, db
    app.dependency_overrides.pop(get_db, None)


def test_bootstrap_creates_first_admin(client):
    test_client, db = client

    response = test_client.post(
        "/auth/bootstrap",
        headers={"X-Bootstrap-Secret": "x" * 32},
        json={"login": "first_admin", "password": "a-secure-password"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "admin"
    assert "password_hash" not in response.json()
    db.commit.assert_awaited_once()


def test_bootstrap_rejects_wrong_secret(client):
    test_client, db = client

    response = test_client.post(
        "/auth/bootstrap",
        headers={"X-Bootstrap-Secret": "wrong"},
        json={"login": "first_admin", "password": "a-secure-password"},
    )

    assert response.status_code == 403
    db.execute.assert_not_awaited()


def test_bootstrap_is_disabled_after_a_user_exists(client):
    test_client, db = client
    db.scalar.return_value = 1

    response = test_client.post(
        "/auth/bootstrap",
        headers={"X-Bootstrap-Secret": "x" * 32},
        json={"login": "second_admin", "password": "a-secure-password"},
    )

    assert response.status_code == 409
    db.commit.assert_not_awaited()
