from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('api/updates/', views.DashboardUpdatesAPIView.as_view(), name='updates_api'),
]
