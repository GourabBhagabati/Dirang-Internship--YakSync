from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.SensorReadingListView.as_view(), name='list'),
    path('<int:pk>/', views.SensorReadingDetailView.as_view(), name='detail'),
]
