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
]
