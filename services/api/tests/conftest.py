from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
API_DIR = ROOT / "services" / "api"
for path in (ROOT, API_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
