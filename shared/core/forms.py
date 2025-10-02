"""Reusable forms shared between services."""

from __future__ import annotations

from typing import Iterable

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import Number
from .validators import area_code_validator, phone_number_validator


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Please enter a correct username and password.",
        "inactive": "This account is inactive.",
    }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            if not self.user.is_active:
                raise forms.ValidationError(self.error_messages["inactive"], code="inactive")
        return cleaned_data

    def get_user(self):
        return getattr(self, "user", None)


class ChangeCredentialsForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_username = forms.CharField(max_length=150, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned = super().clean()
        new_username = cleaned.get("new_username")
        new_password = cleaned.get("new_password")
        if not new_username and not new_password:
            raise forms.ValidationError("Provide a new username, password, or both.")
        if new_password:
            validate_password(new_password, self.user)
        return cleaned

    def apply(self):
        updated = False
        update_fields: list[str] = []
        new_username = self.cleaned_data.get("new_username")
        new_password = self.cleaned_data.get("new_password")
        if new_username and new_username != self.user.username:
            self.user.username = new_username
            updated = True
            update_fields.append("username")
        if new_password:
            self.user.set_password(new_password)
            updated = True
            update_fields.append("password")
        if updated:
            self.user.save(update_fields=update_fields)
        return updated


class NumberForm(forms.ModelForm):
    class Meta:
        model = Number
        fields = ["area_code", "phone_number", "cost"]
        widgets = {
            "area_code": forms.TextInput(attrs={"maxlength": 3}),
            "phone_number": forms.TextInput(attrs={"maxlength": 7}),
            "cost": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_area_code(self):
        value = self.cleaned_data["area_code"]
        area_code_validator(value)
        return value

    def clean_phone_number(self):
        value = self.cleaned_data["phone_number"]
        phone_number_validator(value)
        return value


class BulkUploadForm(forms.Form):
    file = forms.FileField()
    dry_run = forms.BooleanField(required=False, initial=False)
    upsert = forms.BooleanField(required=False, initial=False)

    def clean_file(self):
        upload = self.cleaned_data["file"]
        if upload.size == 0:
            raise forms.ValidationError("Uploaded file is empty.")
        return upload


__all__ = [
    "LoginForm",
    "ChangeCredentialsForm",
    "NumberForm",
    "BulkUploadForm",
]
