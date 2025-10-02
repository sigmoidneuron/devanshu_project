from __future__ import annotations

from django.conf import settings
from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    table_name = getattr(settings, "RATELIMIT_CACHE_TABLE", "ratelimit_cache")
    call_command("createcachetable", table_name)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_cache_table, migrations.RunPython.noop),
    ]
