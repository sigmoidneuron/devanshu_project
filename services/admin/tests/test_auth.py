from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_login_flow(client):
    user = get_user_model().objects.create_user(username="admin", password="secretpass")
    response = client.post("/login/", {"username": "admin", "password": "secretpass"}, secure=True)
    assert response.status_code == 302
    response = client.get("/numbers", secure=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_api(api_client):
    user = get_user_model().objects.create_user(username="admin", password="secretpass")
    response = api_client.post("/v1/auth/login", {"username": "admin", "password": "secretpass"}, format="json", secure=True)
    assert response.status_code == 200
    response = api_client.get("/v1/auth/me", secure=True)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
