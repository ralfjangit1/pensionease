"""
Pension computation logic, kept separate from views so the formula
can be audited, tested, and adjusted independently of request handling.
"""
from decimal import Decimal, ROUND_HALF_UP
from .models import PensionComputation

TWO_PLACES = Decimal("0.01")


def compute_pension(retiree, rate_per_year=Decimal("0.0250"), adjustments=Decimal("0.00"), remarks=""):
    """
    Computes and stores a PensionComputation for the given retiree.

    base_pension = monthly_salary * years_of_service * rate_per_year
    net_monthly_pension = base_pension + adjustments

    rate_per_year is the accrual rate per year of service (e.g. 0.025 = 2.5%
    of monthly salary per year of service), a common pattern in government
    pension formulas. Adjust to match your institution's actual policy.
    """
    years = Decimal(str(retiree.years_of_service()))
    salary = retiree.monthly_salary
    rate = Decimal(str(rate_per_year))
    adj = Decimal(str(adjustments))

    base_pension = (salary * years * rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    net_pension = (base_pension + adj).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    computation = PensionComputation.objects.create(
        retiree=retiree,
        years_of_service=years,
        rate_per_year=rate,
        base_pension=base_pension,
        adjustments=adj,
        net_monthly_pension=net_pension,
        remarks=remarks,
    )
    return computation
