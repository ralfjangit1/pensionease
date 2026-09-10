from django import forms
from .models import Retiree, PensionComputation


class RetireeForm(forms.ModelForm):
    class Meta:
        model = Retiree
        fields = [
            "employee_id", "last_name", "first_name", "middle_name",
            "date_of_birth", "sex", "address", "contact_number", "email",
            "position", "department", "date_hired", "date_retired",
            "monthly_salary", "beneficiary_name", "beneficiary_relationship",
            "notes", "status",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "date_hired": forms.DateInput(attrs={"type": "date"}),
            "date_retired": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "address": forms.TextInput(),
        }

    def clean(self):
        cleaned = super().clean()
        hired = cleaned.get("date_hired")
        retired = cleaned.get("date_retired")
        if hired and retired and retired <= hired:
            raise forms.ValidationError("Date retired must be after date hired.")
        return cleaned


class ComputationForm(forms.Form):
    rate_per_year = forms.DecimalField(
        max_digits=5, decimal_places=4, initial="0.0250",
        label="Accrual rate per year of service",
        help_text="e.g. 0.0250 = 2.5% of monthly salary per year of service",
    )
    adjustments = forms.DecimalField(
        max_digits=12, decimal_places=2, initial="0.00", required=False,
        label="Adjustments (+/-)",
    )
    remarks = forms.CharField(max_length=255, required=False)
