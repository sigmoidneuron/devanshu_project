"""Pagination utilities for Django views and APIs."""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(request: HttpRequest, queryset: Sequence, per_page: int = 25):
    page_number = request.GET.get("page") or 1
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    return page_obj


@dataclass(slots=True)
class PaginationResult:
    items: List[dict]
    total: int
    limit: int
    offset: int


def limit_offset_paginate(items: Iterable[dict], limit: int, offset: int) -> PaginationResult:
    items_list = list(items)
    sliced = items_list[offset : offset + limit]
    return PaginationResult(items=sliced, total=len(items_list), limit=limit, offset=offset)


__all__ = ["paginate", "PaginationResult", "limit_offset_paginate"]
