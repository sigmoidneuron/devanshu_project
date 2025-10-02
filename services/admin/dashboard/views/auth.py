from __future__ import annotations

from django.conf import settings
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.core.forms import ChangeCredentialsForm, LoginForm


@ratelimit(key="ip", rate=settings.LOGIN_RATE_LIMIT, method="POST", block=True)
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("numbers_list")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Signed in successfully.")
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "Signed out.")
    return redirect("login")


@login_required
def change_credentials_view(request: HttpRequest) -> HttpResponse:
    form = ChangeCredentialsForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.apply()
        messages.success(request, "Credentials updated. Please sign in again.")
        logout(request)
        return redirect("login")
    return render(request, "settings.html", {"form": form})


@login_required
def me_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"username": request.user.username, "is_superuser": request.user.is_superuser})


class LoginApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    @method_decorator(ratelimit(key="ip", rate=settings.LOGIN_RATE_LIMIT, method="POST", block=True))
    def post(self, request: HttpRequest) -> Response:
        form = LoginForm(request.data)
        if form.is_valid():
            login(request, form.get_user())
            return Response({"ok": True, "username": request.user.username})
        return Response({"error": {"code": "invalid_credentials", "message": "Invalid username or password."}}, status=400)


class LogoutApiView(APIView):
    def post(self, request: HttpRequest) -> Response:
        logout(request)
        return Response({"ok": True})


class MeApiView(APIView):
    def get(self, request: HttpRequest) -> Response:
        return Response({"username": request.user.username, "is_superuser": request.user.is_superuser})


class ChangeCredentialsApiView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = ChangeCredentialsForm(request.data, user=request.user)
        if form.is_valid():
            form.apply()
            update_session_auth_hash(request, request.user)
            return Response({"ok": True})
        return Response({"error": {"code": "validation_error", "message": form.errors}}, status=400)
