"""
URL configuration for yaksync_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard:index', permanent=False)),
    path('auth/', include('apps.authentication.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('animals/', include('apps.animals.urls')),
    path('devices/', include('apps.devices.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('hormones/', include('apps.hormones.urls')),
    path('protocols/', include('apps.protocols.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('reports/', include('apps.reports.urls')),
    path('activity-logs/', include('apps.logs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
