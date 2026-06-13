from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from apps.animals.models import Animal
from apps.devices.models import Device
from apps.protocols.models import TreatmentAssignment
from apps.alerts.models import Alert
from apps.hormones.models import HormoneReservoir
from apps.logs.models import ActivityLog


class DashboardView(LoginRequiredMixin, View):
    login_url = '/auth/login/'
    template_name = 'dashboard/dashboard.html'
    
    def get(self, request):
        # Aggregate statistics from database
        context = {
            'total_animals': Animal.objects.count(),
            'total_devices': Device.objects.count(),
            'active_devices': Device.objects.filter(status='active').count(),
            'active_protocols': TreatmentAssignment.objects.filter(status__in=['pending', 'in_progress']).count(),
            'active_alerts': Alert.objects.filter(status='active').count(),
            'hormone_reservoirs': HormoneReservoir.objects.all()[:5],
            'recent_alerts': Alert.objects.filter(status='active').order_by('-timestamp')[:5],
            'recent_activities': ActivityLog.objects.select_related('user').order_by('-timestamp')[:10],
        }
        return render(request, self.template_name, context)

