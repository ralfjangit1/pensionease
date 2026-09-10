from django.contrib import admin
from .models import Retiree, PensionComputation, Document


@admin.register(Retiree)
class RetireeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "last_name", "first_name", "position", "date_retired", "status")
    search_fields = ("employee_id", "last_name", "first_name")
    list_filter = ("status", "department")


@admin.register(PensionComputation)
class PensionComputationAdmin(admin.ModelAdmin):
    list_display = ("retiree", "net_monthly_pension", "computed_at")
    list_filter = ("computed_at",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("retiree", "document_type", "certificate_no", "issued_at")
    list_filter = ("document_type",)
