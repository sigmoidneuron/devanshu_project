from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from shared.core.models import Number


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_user(username="admin", password="secretpass")


@pytest.mark.django_db
def test_create_update_delete_number(client, admin_user):
    client.login(username="admin", password="secretpass")
    response = client.post("/numbers/action", {"action": "create", "area_code": "212", "phone_number": "5551234", "cost": 100})
    assert response.status_code == 302
    number = Number.objects.get()
    response = client.post("/numbers/action", {"action": "update", "id": number.id, "area_code": "212", "phone_number": "5559999", "cost": 150})
    assert response.status_code == 302
    number.refresh_from_db()
    assert number.phone_number == "5559999"
    response = client.post("/numbers/action", {"action": "delete", "id": number.id})
    assert response.status_code == 302
    assert Number.objects.count() == 0


@pytest.mark.django_db
def test_numbers_api(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post("/v1/numbers", {"area_code": "305", "phone_number": "1234567", "cost": 200}, format="json")
    assert response.status_code == 201
    number_id = response.json()["id"]
    response = api_client.patch(f"/v1/numbers/{number_id}", {"area_code": "305", "phone_number": "7654321", "cost": 250}, format="json")
    assert response.status_code == 200
    response = api_client.get("/v1/numbers")
    assert response.status_code == 200
    response = api_client.delete(f"/v1/numbers/{number_id}")
    assert response.status_code == 204
