from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.paginator import Paginator
from .models import ActivityLog
from apps.authentication.models import UserProfile


def is_administrator(user):
    """Check if the user has Administrator privileges (superuser or role == administrator)"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return hasattr(user, 'profile') and user.profile.role == 'administrator'


class ActivityLogsDashboardView(LoginRequiredMixin, View):
    template_name = 'logs/activity_dashboard.html'
    denied_template_name = 'errors/access_denied.html'

    def get(self, request):
        # Enforce Administrator-only access control
        if not is_administrator(request.user):
            return render(request, self.denied_template_name, status=403)

        # Fetch summaries for counters
        total_activities = ActivityLog.objects.count()
        
        # Calculate distinct users active today
        today = timezone.now().date()
        active_users_today = ActivityLog.objects.filter(
            timestamp__date=today
        ).values('user').distinct().count()
        
        login_sessions = ActivityLog.objects.filter(action_type='login').count()
        
        # Combined sum of generated preview reports and downloaded PDFs
        reports_generated = ActivityLog.objects.filter(
            action_type__in=['generate_report', 'download_pdf']
        ).count()

        # Handle filtering inputs
        search_query = request.GET.get('search', '').strip()
        role_filter = request.GET.get('role', '')
        action_filter = request.GET.get('action_type', '')
        module_filter = request.GET.get('module_accessed', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        # Build database query
        queryset = ActivityLog.objects.all().select_related('user')

        # Apply search and filter constraints
        if search_query:
            queryset = queryset.filter(user__username__icontains=search_query)
        if role_filter:
            queryset = queryset.filter(user_role=role_filter)
        if action_filter:
            queryset = queryset.filter(action_type=action_filter)
        if module_filter:
            queryset = queryset.filter(module_accessed=module_filter)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        # Paginate results (20 per page)
        paginator = Paginator(queryset, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Choice lists for select filters
        action_choices = ActivityLog.ACTION_TYPE_CHOICES
        module_choices = ActivityLog.MODULE_CHOICES
        role_choices = UserProfile.ROLE_CHOICES

        # Prepare query parameters for pagination links
        query_params = request.GET.copy()
        query_params.pop('page', None)

        context = {
            'page_obj': page_obj,
            'total_activities': total_activities,
            'active_users_today': active_users_today,
            'login_sessions': login_sessions,
            'reports_generated': reports_generated,
            'action_choices': action_choices,
            'module_choices': module_choices,
            'role_choices': role_choices,
            'selected_search': search_query,
            'selected_role': role_filter,
            'selected_action': action_filter,
            'selected_module': module_filter,
            'selected_start_date': start_date,
            'selected_end_date': end_date,
            'query_params': query_params.urlencode(),
        }
        return render(request, self.template_name, context)
