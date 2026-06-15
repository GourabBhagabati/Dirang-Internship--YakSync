from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('', views.ActivityLogsDashboardView.as_view(), name='dashboard'),
]
