from __future__ import annotations

from unittest import mock

import pytest
from django.db.utils import OperationalError

from dashboard import startup


class DummyApp:
    pass


def test_setup_application_runs_factory_and_migrations(monkeypatch):
    monkeypatch.setenv("AUTO_APPLY_MIGRATIONS", "true")
    monkeypatch.setattr(startup.apps, "ready", True, raising=False)

    called = {}
    monkeypatch.setattr(startup, "ensure_database_ready", lambda: called.setdefault("migrated", True))

    application = startup.setup_application(lambda: DummyApp())

    assert isinstance(application, DummyApp)
    assert called["migrated"] is True


def test_setup_application_respects_disabled_flag(monkeypatch):
    monkeypatch.setenv("AUTO_APPLY_MIGRATIONS", "false")
    monkeypatch.setattr(startup.apps, "ready", True, raising=False)

    spy = mock.Mock()
    monkeypatch.setattr(startup, "ensure_database_ready", spy)

    startup.setup_application(lambda: DummyApp())

    spy.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_ensure_database_ready_runs_migrate_when_plan_exists(monkeypatch):
    executor_mock = mock.MagicMock()
    executor_mock.loader.graph.leaf_nodes.return_value = ["test"]
    executor_mock.migration_plan.return_value = ["plan"]

    monkeypatch.setattr(startup, "MigrationExecutor", mock.Mock(return_value=executor_mock))
    call_command = mock.Mock()
    monkeypatch.setattr(startup, "call_command", call_command)

    startup.ensure_database_ready()

    call_command.assert_called_once_with("migrate", interactive=False, run_syncdb=True, database="default")


@pytest.mark.django_db(transaction=True)
def test_ensure_database_ready_skips_when_no_plan(monkeypatch):
    executor_mock = mock.MagicMock()
    executor_mock.loader.graph.leaf_nodes.return_value = ["test"]
    executor_mock.migration_plan.return_value = []

    monkeypatch.setattr(startup, "MigrationExecutor", mock.Mock(return_value=executor_mock))
    call_command = mock.Mock()
    monkeypatch.setattr(startup, "call_command", call_command)

    startup.ensure_database_ready()

    call_command.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_ensure_database_ready_handles_executor_errors(monkeypatch):
    monkeypatch.setattr(startup, "MigrationExecutor", mock.Mock(side_effect=OperationalError("missing")))
    call_command = mock.Mock()
    monkeypatch.setattr(startup, "call_command", call_command)

    startup.ensure_database_ready()

    call_command.assert_called_once_with("migrate", interactive=False, run_syncdb=True, database="default")
