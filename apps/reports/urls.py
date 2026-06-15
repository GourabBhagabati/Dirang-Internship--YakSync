from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.ReportsDashboardView.as_view(), name='dashboard'),
    path('pdf/', views.GenerateReportPDFView.as_view(), name='pdf_export'),
]
