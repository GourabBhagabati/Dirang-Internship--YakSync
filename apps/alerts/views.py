from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from apps.animals.models import Animal
from .models import Alert


class AlertListView(LoginRequiredMixin, ListView):
    """Alert Dashboard displaying active and resolved alerts with filtering"""
    model = Alert
    template_name = 'alerts/alerts_dashboard.html'
    context_object_name = 'alerts'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = Alert.objects.select_related('animal', 'device', 'sensor_reading', 'resolved_by', 'acknowledged_by').all()

        # Filtering by severity
        severity = self.request.GET.get('severity', '').strip()
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filtering by alert type
        alert_type = self.request.GET.get('alert_type', '').strip()
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)

        # Filtering by status
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)

        # Filtering by animal
        animal_id = self.request.GET.get('animal', '').strip()
        if animal_id:
            if animal_id.isdigit():
                queryset = queryset.filter(animal_id=animal_id)
            else:
                messages.error(self.request, 'Invalid animal filter selected.')
                queryset = queryset.none()

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['selected_severity'] = self.request.GET.get('severity', '')
        context['selected_alert_type'] = self.request.GET.get('alert_type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_animal'] = self.request.GET.get('animal', '')
        context['query_params'] = query_params.urlencode()
        
        # Options for dropdowns
        context['animals'] = Animal.objects.order_by('animal_id')
        context['severity_choices'] = Alert.SEVERITY_CHOICES
        context['alert_type_choices'] = Alert.ALERT_TYPE_CHOICES
        context['status_choices'] = Alert.STATUS_CHOICES
        
        # Statistics for dashboard summary cards
        context['active_count'] = Alert.objects.filter(status='active').count()
        context['acknowledged_count'] = Alert.objects.filter(status='acknowledged').count()
        context['resolved_count'] = Alert.objects.filter(status='resolved').count()
        context['total_count'] = Alert.objects.count()

        return context


class AlertAcknowledgeView(LoginRequiredMixin, View):
    """View to mark an alert as Acknowledged"""
    login_url = '/auth/login/'

    def post(self, request, pk):
        alert = get_object_or_404(Alert, pk=pk)
        if alert.status == 'active':
            alert.status = 'acknowledged'
            alert.acknowledged_at = timezone.now()
            alert.acknowledged_by = request.user
            alert.save(update_fields=['status', 'acknowledged_at', 'acknowledged_by'])
            messages.success(request, f"Alert '{alert.title}' acknowledged successfully.")
        else:
            messages.warning(request, f"Alert '{alert.title}' cannot be acknowledged (current status: {alert.status}).")
        
        # Redirect back to the referrer or alerts dashboard
        next_url = request.META.get('HTTP_REFERER', 'alerts:dashboard')
        if not next_url or 'javascript' in next_url:
            next_url = 'alerts:dashboard'
        return redirect(next_url)


class AlertResolveView(LoginRequiredMixin, View):
    """View to mark an alert as Resolved"""
    login_url = '/auth/login/'

    def post(self, request, pk):
        alert = get_object_or_404(Alert, pk=pk)
        if alert.status in ['active', 'acknowledged']:
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save(update_fields=['status', 'resolved_at', 'resolved_by'])
            messages.success(request, f"Alert '{alert.title}' resolved successfully.")
        else:
            messages.warning(request, f"Alert '{alert.title}' is already resolved.")
        
        # Redirect back to the referrer or alerts dashboard
        next_url = request.META.get('HTTP_REFERER', 'alerts:dashboard')
        if not next_url or 'javascript' in next_url:
            next_url = 'alerts:dashboard'
        return redirect(next_url)

