import uuid
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Retiree, PensionComputation, Document
from .forms import RetireeForm, ComputationForm
from .services import compute_pension
from .pdf_utils import generate_certificate_pdf, generate_retiree_list_report_pdf


# ---------- Dashboard ----------

def dashboard(request):
    total_retirees = Retiree.objects.count()
    pending = Retiree.objects.filter(status="pending").count()
    active = Retiree.objects.filter(status="active").count()
    documents_issued = Document.objects.count()
    recent = Retiree.objects.order_by("-updated_at")[:6]
    context = {
        "total_retirees": total_retirees,
        "pending": pending,
        "active": active,
        "documents_issued": documents_issued,
        "recent": recent,
        "active_nav": "dashboard",
    }
    return render(request, "retirees/dashboard.html", context)


# ---------- CRUD ----------

class RetireeListView(ListView):
    model = Retiree
    template_name = "retirees/retiree_list.html"
    context_object_name = "retirees"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(last_name__icontains=q) | Q(first_name__icontains=q) |
                Q(employee_id__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_nav"] = "retirees"
        return ctx


class RetireeDetailView(DetailView):
    model = Retiree
    template_name = "retirees/retiree_detail.html"
    context_object_name = "retiree"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["computations"] = self.object.computations.all()[:5]
        ctx["documents"] = self.object.documents.all()[:5]
        ctx["active_nav"] = "retirees"
        return ctx


class RetireeCreateView(CreateView):
    model = Retiree
    form_class = RetireeForm
    template_name = "retirees/retiree_form.html"
    success_url = reverse_lazy("retiree_list")

    def form_valid(self, form):
        messages.success(self.request, "Retiree record saved.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_nav"] = "add-retiree"
        return ctx


class RetireeUpdateView(UpdateView):
    model = Retiree
    form_class = RetireeForm
    template_name = "retirees/retiree_form.html"
    success_url = reverse_lazy("retiree_list")

    def form_valid(self, form):
        messages.success(self.request, "Retiree record updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_nav"] = "retirees"
        return ctx


class RetireeDeleteView(DeleteView):
    model = Retiree
    template_name = "retirees/retiree_confirm_delete.html"
    success_url = reverse_lazy("retiree_list")

    def form_valid(self, form):
        messages.success(self.request, "Retiree record deleted.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_nav"] = "retirees"
        return ctx


# ---------- Computation ----------

def compute_pension_view(request, pk):
    retiree = get_object_or_404(Retiree, pk=pk)
    if request.method == "POST":
        form = ComputationForm(request.POST)
        if form.is_valid():
            computation = compute_pension(
                retiree,
                rate_per_year=form.cleaned_data["rate_per_year"],
                adjustments=form.cleaned_data["adjustments"] or 0,
                remarks=form.cleaned_data["remarks"],
            )
            messages.success(request, f"Pension computed: PHP {computation.net_monthly_pension:,.2f}")
            return redirect("retiree_detail", pk=retiree.pk)
    else:
        form = ComputationForm()
    return render(request, "retirees/compute_pension.html",
                  {"retiree": retiree, "form": form, "active_nav": "retirees"})


# ---------- Reports ----------

def reports_home(request):
    return render(request, "retirees/reports.html", {"active_nav": "reports"})


def report_retiree_master_list(request):
    retirees = Retiree.objects.all()
    pdf_bytes = generate_retiree_list_report_pdf(retirees)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="retiree_master_list.pdf"'
    return response


def report_status_overview(request):
    counts = Retiree.objects.values("status").annotate(total=Count("id"))
    return render(request, "retirees/report_status_overview.html",
                  {"counts": counts, "active_nav": "reports"})


# ---------- Documents ----------

def documents_home(request):
    retirees = Retiree.objects.all()
    return render(request, "retirees/documents.html",
                  {"retirees": retirees, "active_nav": "documents"})


def generate_document(request, pk):
    retiree = get_object_or_404(Retiree, pk=pk)
    doc_type = request.GET.get("type", "award")
    label_map = dict(Document.DOC_TYPES)
    label = label_map.get(doc_type, "Certificate of Pension Award")

    certificate_no = f"PE-{retiree.date_retired.year}-{retiree.employee_id.split('-')[-1]}-{uuid.uuid4().hex[:4].upper()}"
    latest_computation = retiree.computations.first()

    pdf_bytes = generate_certificate_pdf(retiree, label, certificate_no, computation=latest_computation)

    Document.objects.create(
        retiree=retiree, document_type=doc_type, certificate_no=certificate_no,
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{retiree.employee_id}_{doc_type}.pdf"'
    return response
