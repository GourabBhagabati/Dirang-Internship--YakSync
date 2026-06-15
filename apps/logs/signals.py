from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import ActivityLog


def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_role(user):
    if user.is_superuser:
        return 'administrator'
    if hasattr(user, 'profile'):
        return user.profile.role
    return 'unknown'


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    role = get_user_role(user)
    role_display = role.replace('_', ' ').title() if role else 'Unknown'
    
    # Store login time in request session
    now = timezone.now()
    if request and hasattr(request, 'session'):
        request.session['login_time'] = now.isoformat()
        
    ActivityLog.objects.create(
        user=user,
        user_role=role,
        action_type='login',
        module_accessed='dashboard',
        description=f"User \"{user.get_full_name() or user.username}\" logged in.",
        ip_address=ip,
        login_time=now
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if not user:
        return
        
    ip = get_client_ip(request)
    role = get_user_role(user)
    role_display = role.replace('_', ' ').title() if role else 'Unknown'
    
    logout_time = timezone.now()
    login_time = None
    session_duration = None
    
    # Try to fetch login time from session
    if request and hasattr(request, 'session'):
        login_time_str = request.session.get('login_time')
        if login_time_str:
            try:
                login_time = timezone.datetime.fromisoformat(login_time_str)
            except Exception:
                pass
                
    # Fallback to fetching latest login log from DB
    if not login_time:
        latest_login = ActivityLog.objects.filter(
            user=user,
            action_type='login'
        ).order_by('-timestamp').first()
        if latest_login:
            login_time = latest_login.login_time or latest_login.timestamp
            
    if login_time:
        session_duration = logout_time - login_time
        
    # Generate duration string for description
    duration_str = ""
    if session_duration:
        total_seconds = int(session_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            duration_str = f" after {hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            duration_str = f" after {minutes} minute{'s' if minutes != 1 else ''}"
            
    ActivityLog.objects.create(
        user=user,
        user_role=role,
        action_type='logout',
        module_accessed='dashboard',
        description=f"User logged out{duration_str}.",
        ip_address=ip,
        login_time=login_time,
        logout_time=logout_time,
        session_duration=session_duration
    )
