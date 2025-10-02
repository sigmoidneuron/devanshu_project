from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.core.forms import NumberForm
from shared.core.models import Number
from shared.core.pagination import paginate


@login_required
def home_redirect(request: HttpRequest) -> HttpResponse:
    return redirect("numbers_list")


@login_required
def numbers_list_view(request: HttpRequest) -> HttpResponse:
    queryset = Number.objects.all()
    area_filter = request.GET.get("area_code")
    search = request.GET.get("search")
    ordering = request.GET.get("ordering", "area_code")

    if area_filter:
        queryset = queryset.filter(area_code=area_filter)
    if search:
        queryset = queryset.filter(phone_number__icontains=search)

    if ordering not in {"area_code", "-area_code", "phone_number", "-phone_number", "cost", "-cost", "created_at", "-created_at"}:
        ordering = "area_code"
    queryset = queryset.order_by(ordering)

    page_obj = paginate(request, queryset, per_page=25)
    form = NumberForm()
    context = {
        "page_obj": page_obj,
        "form": form,
        "area_filter": area_filter,
        "search": search,
        "ordering": ordering,
    }
    return render(request, "numbers.html", context)


@login_required
def numbers_post_view(request: HttpRequest) -> HttpResponse:
    action = request.POST.get("action")
    if action == "create":
        form = NumberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Number created.")
        else:
            messages.error(request, f"Error creating number: {form.errors}")
    elif action == "update":
        instance = get_object_or_404(Number, pk=request.POST.get("id"))
        form = NumberForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Number updated.")
        else:
            messages.error(request, f"Error updating number: {form.errors}")
    elif action == "delete":
        instance = get_object_or_404(Number, pk=request.POST.get("id"))
        instance.delete()
        messages.info(request, "Number deleted.")
    else:
        messages.error(request, "Unsupported action.")
    return redirect("numbers_list")


class NumbersApiView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="ip", rate=settings.ADMIN_API_RATE_LIMIT, method="GET", block=True))
    def get(self, request: HttpRequest) -> Response:
        try:
            limit = min(max(int(request.GET.get("limit", 50)), 1), 500)
        except ValueError:
            limit = 50
        try:
            offset = max(int(request.GET.get("offset", 0)), 0)
        except ValueError:
            offset = 0
        queryset = Number.objects.all().order_by("area_code", "phone_number")
        total = queryset.count()
        items = [
            {
                "id": str(number.id),
                "area_code": number.area_code,
                "phone_number": number.phone_number,
                "cost": number.cost,
                "created_at": number.created_at.isoformat(),
                "updated_at": number.updated_at.isoformat(),
            }
            for number in queryset[offset : offset + limit]
        ]
        return Response({"results": items, "count": total, "limit": limit, "offset": offset})

    @method_decorator(ratelimit(key="ip", rate=settings.ADMIN_API_RATE_LIMIT, method="POST", block=True))
    def post(self, request: HttpRequest) -> Response:
        form = NumberForm(request.data)
        if form.is_valid():
            instance = form.save()
            return Response(
                {
                    "id": str(instance.id),
                    "area_code": instance.area_code,
                    "phone_number": instance.phone_number,
                    "cost": instance.cost,
                },
                status=201,
            )
        return Response({"error": form.errors}, status=400)


class NumberDetailApiView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="ip", rate=settings.ADMIN_API_RATE_LIMIT, method="PATCH", block=True))
    def patch(self, request: HttpRequest, pk: str) -> Response:
        instance = get_object_or_404(Number, pk=pk)
        form = NumberForm(request.data, instance=instance)
        if form.is_valid():
            instance = form.save()
            return Response({"id": str(instance.id), "area_code": instance.area_code, "phone_number": instance.phone_number, "cost": instance.cost})
        return Response({"error": form.errors}, status=400)

    @method_decorator(ratelimit(key="ip", rate=settings.ADMIN_API_RATE_LIMIT, method="DELETE", block=True))
    def delete(self, request: HttpRequest, pk: str) -> Response:
        instance = get_object_or_404(Number, pk=pk)
        instance.delete()
        return Response(status=204)
