from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.SensorReadingListView.as_view(), name='list'),
    path('<int:pk>/', views.SensorReadingDetailView.as_view(), name='detail'),
    path('api/telemetry/', views.HerdTelemetryAPIView.as_view(), name='api_herd_telemetry'),
    path('api/telemetry/<int:animal_id>/', views.AnimalTelemetryAPIView.as_view(), name='api_animal_telemetry'),
]
