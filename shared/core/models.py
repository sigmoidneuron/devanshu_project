"""Database models shared between services."""

import uuid
from django.db import models
from django.utils import timezone

from .validators import area_code_validator, phone_number_validator


class TimestampedModel(models.Model):
    """Abstract base class with created/updated timestamps."""

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NumberQuerySet(models.QuerySet):
    def with_area_code(self, area_code: str) -> "NumberQuerySet":
        return self.filter(area_code=area_code)

    def with_last_four(self, last_four: str) -> "NumberQuerySet":
        return self.filter(phone_number__endswith=last_four)


class Number(TimestampedModel):
    """Represents a purchasable phone number."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area_code = models.CharField(
        max_length=3,
        validators=[area_code_validator],
        help_text="Exactly three digits representing the area code.",
        db_index=True,
    )
    phone_number = models.CharField(
        max_length=7,
        validators=[phone_number_validator],
        help_text="Exactly seven digits for the local number.",
        db_index=True,
    )
    cost = models.PositiveIntegerField(help_text="Cost in USD cents or dollars as configured.")

    objects = NumberQuerySet.as_manager()

    class Meta:
        unique_together = ("area_code", "phone_number")
        indexes = [
            models.Index(fields=["area_code"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["area_code", "phone_number"]),
        ]
        ordering = ["area_code", "phone_number"]

    def __str__(self) -> str:  # pragma: no cover - human readable
        return f"({self.area_code}) {self.phone_number}"

    @property
    def full_number(self) -> str:
        return f"{self.area_code}{self.phone_number}"


__all__ = ["Number", "TimestampedModel"]
