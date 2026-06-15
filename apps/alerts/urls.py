from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.AlertListView.as_view(), name='dashboard'),
    path('<int:pk>/acknowledge/', views.AlertAcknowledgeView.as_view(), name='acknowledge'),
    path('<int:pk>/resolve/', views.AlertResolveView.as_view(), name='resolve'),
]
