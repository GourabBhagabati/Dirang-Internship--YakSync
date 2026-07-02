from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'hormones'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='hormones:reservoir_list', permanent=False), name='index'),
    path('reservoirs/', views.HormoneReservoirListView.as_view(), name='reservoir_list'),
    path('reservoirs/create/', views.HormoneReservoirCreateView.as_view(), name='reservoir_create'),
    path('reservoirs/<int:pk>/', views.HormoneReservoirDetailView.as_view(), name='reservoir_detail'),
    path('reservoirs/<int:pk>/edit/', views.HormoneReservoirUpdateView.as_view(), name='reservoir_edit'),
    path('reservoirs/<int:pk>/delete/', views.HormoneReservoirDeleteView.as_view(), name='reservoir_delete'),
    path('releases/', views.HormoneReleaseListView.as_view(), name='release_list'),
    path('releases/create/', views.HormoneReleaseCreateView.as_view(), name='release_create'),
    path('releases/<int:pk>/', views.HormoneReleaseDetailView.as_view(), name='release_detail'),
    
    # API endpoints for frontend-backend interaction
    path('api/animals/', views.api_fetch_animals, name='api_fetch_animals'),
    path('api/reservoirs/', views.api_fetch_reservoirs, name='api_fetch_reservoirs'),
    path('api/release/', views.api_release_hormone, name='api_release_hormone'),
    path('api/schedule/', views.api_schedule_hormone, name='api_schedule_hormone'),
    path('api/schedules/', views.api_fetch_schedules, name='api_fetch_schedules'),
    path('api/schedule/cancel/', views.api_cancel_schedule, name='api_cancel_schedule'),
    path('api/emergency-stop/', views.api_emergency_stop, name='api_emergency_stop'),
    path('api/history/', views.api_release_history, name='api_release_history'),
    path('api/run-debug/', views.api_run_debug, name='api_run_debug'),
]


