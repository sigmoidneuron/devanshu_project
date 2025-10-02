from django.contrib import admin

from .models import Number


@admin.register(Number)
class NumberAdmin(admin.ModelAdmin):
    list_display = ("area_code", "phone_number", "cost", "created_at", "updated_at")
    search_fields = ("area_code", "phone_number")
    list_filter = ("area_code",)
    ordering = ("area_code", "phone_number")
    readonly_fields = ("created_at", "updated_at")
