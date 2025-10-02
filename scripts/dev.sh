#!/usr/bin/env bash
set -euo pipefail
trap 'kill 0' EXIT
python services/api/manage.py runserver 0.0.0.0:8000 &
python services/admin/manage.py runserver 0.0.0.0:8001 &
wait
