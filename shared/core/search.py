"""Search utilities shared between services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from django.db.models import QuerySet

from .models import Number


@dataclass(slots=True)
class RankedNumber:
    area_code: str
    phone_number: str
    cost: int
    distance: int
    similarity_score: float
    created_at: "datetime"

    @property
    def full_number(self) -> str:
        return f"{self.area_code}{self.phone_number}"


def levenshtein_distance(a: str, b: str) -> int:
    """Compute Levenshtein distance using a dynamic programming table."""

    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current_row = [i]
        for j, cb in enumerate(b, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def trigram_set(value: str) -> set[str]:
    return {value[i : i + 3] for i in range(len(value) - 2)} if len(value) >= 3 else {value}


def trigram_jaccard(a: str, b: str) -> float:
    """Return Jaccard similarity of trigrams."""

    set_a = trigram_set(a)
    set_b = trigram_set(b)
    intersection = len(set_a & set_b)
    union = len(set_a | set_b) or 1
    return intersection / union


def _prepare_candidates(
    queryset: QuerySet[Number],
    query_area_code: str,
    query_phone_number: str,
    limit: int = 10,
) -> Sequence[Number]:
    full_number = f"{query_area_code}{query_phone_number}"
    candidates: List[Number] = list(
        queryset.with_area_code(query_area_code).exclude(area_code=query_area_code, phone_number=query_phone_number)
    )

    if len(candidates) >= limit:
        return candidates

    last_four = query_phone_number[-4:]
    extra = queryset.exclude(area_code=query_area_code, phone_number=query_phone_number).with_last_four(last_four)
    seen_ids = {c.id for c in candidates}
    for candidate in extra:
        if candidate.id in seen_ids:
            continue
        candidates.append(candidate)
        seen_ids.add(candidate.id)
        if len(candidates) >= limit * 5:
            # avoid overly large in-memory sets; scoring will trim to limit
            break

    return candidates


def rank_related_numbers(
    queryset: QuerySet[Number],
    query_area_code: str,
    query_phone_number: str,
    limit: int = 10,
) -> List[dict]:
    """Return related numbers ranked by similarity.

    This is the default Python implementation that works on SQLite and Postgres.
    """

    candidates = _prepare_candidates(queryset, query_area_code, query_phone_number, limit)
    query_full = f"{query_area_code}{query_phone_number}"

    ranked: List[RankedNumber] = []
    for candidate in candidates:
        distance = levenshtein_distance(query_phone_number, candidate.phone_number)
        similarity = trigram_jaccard(query_full, candidate.full_number)
        ranked.append(
            RankedNumber(
                area_code=candidate.area_code,
                phone_number=candidate.phone_number,
                cost=candidate.cost,
                distance=distance,
                similarity_score=similarity,
                created_at=candidate.created_at,
            )
        )

    ranked.sort(
        key=lambda item: (
            item.distance,
            -item.similarity_score,
            item.cost,
            -item.created_at.timestamp(),
        )
    )

    results = []
    for item in ranked[:limit]:
        results.append(
            {
                "area_code": item.area_code,
                "phone_number": item.phone_number,
                "full_number": item.full_number,
                "cost": item.cost,
                "distance": item.distance,
                "similarity_score": round(item.similarity_score, 6),
            }
        )
    return results


__all__ = [
    "rank_related_numbers",
    "levenshtein_distance",
    "trigram_jaccard",
]
