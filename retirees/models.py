from django.db import models
from django.urls import reverse
from decimal import Decimal


class Retiree(models.Model):
    SEX_CHOICES = [("F", "Female"), ("M", "Male")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("review", "In Review"),
        ("active", "Active"),
    ]

    employee_id = models.CharField(max_length=20, unique=True)
    last_name = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default="F")
    address = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    position = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)
    date_hired = models.DateField()
    date_retired = models.DateField()
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)

    beneficiary_name = models.CharField(max_length=160, blank=True)
    beneficiary_relationship = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.employee_id})"

    def full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"

    def years_of_service(self):
        days = (self.date_retired - self.date_hired).days
        return round(days / 365.25, 2)

    def get_absolute_url(self):
        return reverse("retiree_detail", args=[self.pk])


class PensionComputation(models.Model):
    """
    Stores a computed pension result for a retiree.
    Formula used (standard government-service style formula, adjustable):
        base_pension = monthly_salary * years_of_service * rate_per_year
        net_pension  = base_pension + adjustments
    """
    retiree = models.ForeignKey(Retiree, on_delete=models.CASCADE, related_name="computations")
    years_of_service = models.DecimalField(max_digits=6, decimal_places=2)
    rate_per_year = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.0250"))
    base_pension = models.DecimalField(max_digits=12, decimal_places=2)
    adjustments = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    net_monthly_pension = models.DecimalField(max_digits=12, decimal_places=2)
    computed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-computed_at"]

    def __str__(self):
        return f"Computation for {self.retiree} on {self.computed_at:%Y-%m-%d}"


class Document(models.Model):
    DOC_TYPES = [
        ("award", "Certificate of Pension Award"),
        ("service", "Service Record Certificate"),
        ("computation", "Computation Slip"),
        ("clearance", "Clearance Certificate"),
    ]

    retiree = models.ForeignKey(Retiree, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    certificate_no = models.CharField(max_length=40, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="documents/", blank=True, null=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.retiree}"
