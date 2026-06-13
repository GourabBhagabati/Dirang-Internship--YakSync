from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.DeviceListView.as_view(), name='list'),
    path('create/', views.DeviceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DeviceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DeviceUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='delete'),
]
