from __future__ import annotations

import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from shared.core.models import Number

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ChangeMeNow!2025"


class Command(BaseCommand):
    help = "Seed the database with an admin user and sample numbers."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")
        with transaction.atomic():
            self._create_admin()
            self._create_numbers()
        self.stdout.write(self.style.SUCCESS("Database seeded."))

    def _create_admin(self):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=ADMIN_USERNAME)
        if created:
            user.set_password(ADMIN_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write("Created default admin user.")
        else:
            self.stdout.write("Admin user already exists; skipping creation.")

    def _create_numbers(self):
        if Number.objects.count() >= 100:
            self.stdout.write("Numbers already seeded; skipping.")
            return

        random.seed(42)
        area_codes = ["212", "305", "415", "646", "702", "713", "818", "917", "972", "206"]
        numbers = []
        existing = set(Number.objects.values_list("area_code", "phone_number"))
        while len(numbers) < 100:
            area = random.choice(area_codes)
            local = f"{random.randint(0, 9999999):07d}"
            if (area, local) in existing:
                continue
            existing.add((area, local))
            cost = random.choice([49, 79, 99, 149, 199, 249, 299, 349, 399, 499])
            numbers.append(Number(area_code=area, phone_number=local, cost=cost))
        Number.objects.bulk_create(numbers, batch_size=50)
        self.stdout.write(f"Inserted {len(numbers)} sample numbers.")
