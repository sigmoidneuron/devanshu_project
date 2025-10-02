from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ADMIN_DIR = ROOT / "services" / "admin"
for path in (ROOT, ADMIN_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def client():
    from django.test import Client

    return Client()


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
