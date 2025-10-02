"""Utilities used during Django application startup."""

from __future__ import annotations

import logging
import os
from typing import Callable

import django
from django.apps import apps
from django.core.management import call_command
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.db.utils import OperationalError, ProgrammingError


logger = logging.getLogger(__name__)


def _should_auto_apply_migrations() -> bool:
    """Return ``True`` when automatic migrations are enabled."""

    return os.getenv("AUTO_APPLY_MIGRATIONS", "true").lower() in {"1", "true", "yes"}


def _run_migrate(database: str) -> None:
    """Execute ``migrate`` for the provided database alias."""

    logger.info("Applying database migrations for alias '%s'.", database)
    call_command("migrate", interactive=False, run_syncdb=True, database=database)


def ensure_database_ready(database: str = "default") -> None:
    """Ensure that all migrations have been applied for the selected database."""

    connection = connections[database]
    try:
        executor = MigrationExecutor(connection)
    except (OperationalError, ProgrammingError):
        _run_migrate(database)
        return

    targets = executor.loader.graph.leaf_nodes()
    try:
        plan = executor.migration_plan(targets)
    except (OperationalError, ProgrammingError):
        _run_migrate(database)
        return

    if plan:
        _run_migrate(database)
    else:
        logger.debug("No pending migrations for alias '%s'.", database)


def setup_application(factory: Callable[[], object]) -> object:
    """Prepare Django and return the application created by ``factory``."""

    if not apps.ready:
        django.setup()

    if _should_auto_apply_migrations():
        ensure_database_ready()
    else:
        logger.info("AUTO_APPLY_MIGRATIONS disabled; skipping migration check.")

    return factory()


__all__ = ["ensure_database_ready", "setup_application"]

