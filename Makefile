PYTHON ?= python
DJANGO_MANAGE_API = $(PYTHON) services/api/manage.py
DJANGO_MANAGE_ADMIN = $(PYTHON) services/admin/manage.py

.PHONY: dev migrate seed test build up

dev:
	./scripts/dev.sh

migrate:
	$(DJANGO_MANAGE_API) migrate

seed:
	$(DJANGO_MANAGE_API) seed

test:
	PYTHONPATH=. pytest --ds=api.settings services/api/tests
	PYTHONPATH=. pytest --ds=dashboard.settings services/admin/tests

build:
	docker compose build

up:
	docker compose up -d
