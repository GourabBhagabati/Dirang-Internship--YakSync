from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import ActivityLog
from .signals import get_client_ip, get_user_role
from apps.alerts.models import Alert


class ActivityLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only log authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
            
        resolver_match = getattr(request, 'resolver_match', None)
        if not resolver_match:
            return response
            
        app_name = resolver_match.app_name
        url_name = resolver_match.url_name
        
        # Prevent logging admin pages or the logs module itself to avoid infinite loops
        if app_name in ['admin', 'logs']:
            return response
            
        action_type = None
        module_accessed = None
        description = ""
        
        user_name = request.user.get_full_name() or request.user.username
        role = get_user_role(request.user)
        role_display = role.replace('_', ' ').title() if role else 'Unknown'
        
        # Log page view entries (GET requests)
        if request.method == 'GET':
            if url_name in ['list', 'index', 'dashboard', 'detail', 'profile_edit'] or app_name == 'dashboard':
                action_type = 'view'
                module_accessed = app_name if app_name != 'authentication' else 'profile'
                
                module_display = module_accessed.title()
                if module_accessed == 'monitoring':
                    module_display = 'Monitoring'
                elif module_accessed == 'hormones':
                    module_display = 'Hormone'
                elif module_accessed == 'protocols':
                    module_display = 'Treatment Protocols'
                
                # Check for PDF report downloads and dashboard preview generations
                if app_name == 'reports' and url_name == 'pdf_export':
                    action_type = 'download_pdf'
                    report_type = request.GET.get('report_type', 'analytical').replace('_', ' ').title()
                    description = f"User \"{user_name}\" generated an {report_type} PDF report."
                elif app_name == 'reports' and url_name == 'dashboard' and request.GET.get('report_type'):
                    action_type = 'generate_report'
                    report_type = request.GET.get('report_type').replace('_', ' ').title()
                    description = f"User \"{user_name}\" generated an {report_type} preview report."
                else:
                    description = f"User \"{user_name}\" viewed the {module_display} module."
                    
        # Log database state mutations (POST requests)
        elif request.method == 'POST':
            if response.status_code in [200, 302]:
                module_accessed = app_name if app_name != 'authentication' else 'profile'
                
                if 'create' in url_name or 'add' in url_name:
                    action_type = 'create'
                    description = f"User \"{user_name}\" created a new {module_accessed.rstrip('s')}."
                    
                    # Custom descriptions for protocols
                    if app_name == 'protocols' and 'step' in url_name:
                        description = f"User \"{user_name}\" added a step to treatment protocol."
                    elif app_name == 'protocols':
                        description = f"User \"{user_name}\" created a new treatment protocol."
                elif 'edit' in url_name or 'update' in url_name or 'profile_edit' in url_name:
                    action_type = 'update'
                    description = f"User \"{user_name}\" updated a record in {module_accessed.title()} module."
                    
                    if app_name == 'authentication':
                        description = f"User \"{user_name}\" updated user profile settings."
                elif 'delete' in url_name:
                    action_type = 'delete'
                    description = f"User \"{user_name}\" deleted a record from {module_accessed.title()} module."
                elif url_name in ['acknowledge', 'resolve'] and app_name == 'alerts':
                    action_type = 'alert_action'
                    alert_id = resolver_match.kwargs.get('pk')
                    
                    # Fetch alert details dynamically to build exact descriptions
                    try:
                        alert = Alert.objects.get(pk=alert_id)
                        alert_name = alert.alert_type.replace('_', ' ').lower()
                        # e.g., Acknowledged / Resolved
                        past_action = "acknowledged" if url_name == 'acknowledge' else "resolved"
                        description = f"User \"{user_name}\" {past_action} a {alert_name} alert."
                    except Exception:
                        description = f"User \"{user_name}\" performed {url_name} action on alert ID {alert_id}."
                elif 'assign' in url_name:
                    action_type = 'create'
                    description = f"User \"{user_name}\" assigned a treatment protocol."
                    
        # Save log if resolved
        if action_type and module_accessed:
            ip = get_client_ip(request)
            
            valid_modules = ['dashboard', 'animals', 'devices', 'monitoring', 'hormones', 'protocols', 'alerts', 'reports', 'profile']
            if module_accessed in valid_modules:
                ActivityLog.objects.create(
                    user=request.user,
                    user_role=role,
                    action_type=action_type,
                    module_accessed=module_accessed,
                    description=description,
                    ip_address=ip
                )
                
        return response
