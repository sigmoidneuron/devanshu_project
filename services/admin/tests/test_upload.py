from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from shared.core.models import Number


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_user(username="admin", password="secretpass")


@pytest.mark.django_db
def test_bulk_upload_csv(client, admin_user):
    client.login(username="admin", password="secretpass")
    csv_content = "area_code,phone_number,cost\n212,5551234,100\n213,5552222,150\n"
    upload = SimpleUploadedFile("numbers.csv", csv_content.encode("utf-8"), content_type="text/csv")
    response = client.post(
        "/upload",
        {"dry_run": False, "upsert": False, "file": upload},
        follow=True,
    )
    assert response.status_code == 200
    assert Number.objects.count() == 2


@pytest.mark.django_db
def test_bulk_upload_api(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    csv_content = "area_code,phone_number,cost\n212,5553333,120\n"
    upload = SimpleUploadedFile("numbers.csv", csv_content.encode("utf-8"), content_type="text/csv")
    response = api_client.post(
        "/v1/numbers/bulk-upload",
        {"dry_run": True, "upsert": True, "file": upload},
        format="multipart",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 1
