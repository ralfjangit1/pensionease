from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("retirees/", views.RetireeListView.as_view(), name="retiree_list"),
    path("retirees/add/", views.RetireeCreateView.as_view(), name="retiree_add"),
    path("retirees/<int:pk>/", views.RetireeDetailView.as_view(), name="retiree_detail"),
    path("retirees/<int:pk>/edit/", views.RetireeUpdateView.as_view(), name="retiree_edit"),
    path("retirees/<int:pk>/delete/", views.RetireeDeleteView.as_view(), name="retiree_delete"),
    path("retirees/<int:pk>/compute/", views.compute_pension_view, name="compute_pension"),

    path("reports/", views.reports_home, name="reports_home"),
    path("reports/retiree-master-list/", views.report_retiree_master_list, name="report_master_list"),
    path("reports/status-overview/", views.report_status_overview, name="report_status_overview"),

    path("documents/", views.documents_home, name="documents_home"),
    path("documents/<int:pk>/generate/", views.generate_document, name="generate_document"),
]
