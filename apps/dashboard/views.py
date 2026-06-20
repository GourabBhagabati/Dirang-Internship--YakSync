from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from apps.animals.models import Animal
from apps.devices.models import Device
from apps.protocols.models import TreatmentAssignment
from apps.alerts.models import Alert
from apps.hormones.models import HormoneReservoir
from apps.logs.models import ActivityLog
from .weather import get_weather_data


class DashboardView(LoginRequiredMixin, View):
    login_url = '/auth/login/'
    template_name = 'dashboard/dashboard.html'
    
    def get(self, request):
        from django.conf import settings
        
        # Fetch the last communication of any device as the system sync time
        last_device_comm = Device.objects.filter(last_communication__isnull=False).order_by('-last_communication').first()
        last_sync = last_device_comm.last_communication if last_device_comm else None

        # Fetch weather data for Dirang
        weather = get_weather_data()

        # Aggregate statistics from database
        context = {
            'total_animals': Animal.objects.count(),
            'total_devices': Device.objects.count(),
            'active_devices': Device.objects.filter(status='active').count(),
            'inactive_devices': Device.objects.filter(status='inactive').count(),
            'maintenance_devices': Device.objects.filter(status='maintenance').count(),
            'active_protocols': TreatmentAssignment.objects.filter(status__in=['pending', 'in_progress']).count(),
            'active_alerts': Alert.objects.filter(status='active').count(),
            'hormone_reservoirs': HormoneReservoir.objects.all()[:5],
            'recent_alerts': Alert.objects.filter(status='active').order_by('-timestamp')[:5],
            'recent_activities': ActivityLog.objects.select_related('user').order_by('-timestamp')[:10],
            'last_sync': last_sync,
            'weather': weather,
            'animals': Animal.objects.all().order_by('animal_id'),
            'firebase_config': getattr(settings, 'FIREBASE_CONFIG', None),
        }
        return render(request, self.template_name, context)


from django.http import JsonResponse
from django.template.loader import render_to_string

class DashboardUpdatesAPIView(LoginRequiredMixin, View):
    """API endpoint to get dynamic updates for stats counters and page fragments"""
    login_url = '/auth/login/'

    def get(self, request):
        # Aggregated statistics
        total_animals = Animal.objects.count()
        total_devices = Device.objects.count()
        active_devices = Device.objects.filter(status='active').count()
        inactive_devices = Device.objects.filter(status='inactive').count()
        maintenance_devices = Device.objects.filter(status='maintenance').count()
        active_protocols = TreatmentAssignment.objects.filter(status__in=['pending', 'in_progress']).count()
        active_alerts = Alert.objects.filter(status='active').count()
        unread_critical_count = Alert.objects.filter(status='active', severity='critical').count()

        # Datasets for pre-rendering
        recent_alerts = Alert.objects.filter(status='active').order_by('-timestamp')[:5]
        recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
        hormone_reservoirs = HormoneReservoir.objects.all()[:5]

        # Context for templates
        navbar_context = {'recent_active_alerts': recent_alerts}
        alerts_context = {'recent_alerts': recent_alerts}
        activities_context = {'recent_activities': recent_activities}
        hormones_context = {'hormone_reservoirs': hormone_reservoirs}

        # Pre-render template fragments
        navbar_alerts_html = render_to_string('includes/navbar_alerts_fragment.html', navbar_context, request=request)
        dashboard_alerts_html = render_to_string('dashboard/includes/recent_alerts_fragment.html', alerts_context, request=request)
        dashboard_activities_html = render_to_string('dashboard/includes/recent_activities_fragment.html', activities_context, request=request)
        dashboard_hormones_html = render_to_string('dashboard/includes/hormones_status_fragment.html', hormones_context, request=request)

        data = {
            'unread_critical_count': unread_critical_count,
            'stats': {
                'total_animals': total_animals,
                'total_devices': total_devices,
                'active_devices': active_devices,
                'inactive_devices': inactive_devices,
                'maintenance_devices': maintenance_devices,
                'active_protocols': active_protocols,
                'active_alerts': active_alerts,
            },
            'html': {
                'navbar_alerts': navbar_alerts_html,
                'dashboard_alerts': dashboard_alerts_html,
                'dashboard_activities': dashboard_activities_html,
                'dashboard_hormones': dashboard_hormones_html,
            }
        }
        return JsonResponse(data)


