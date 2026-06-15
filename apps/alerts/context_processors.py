from apps.alerts.models import Alert

def unread_alerts_processor(request):
    """Context processor to provide unread critical alert counts and recent active alerts globally"""
    if request.user.is_authenticated:
        unread_critical_count = Alert.objects.filter(status='active', severity='critical').count()
        recent_active_alerts = Alert.objects.filter(status='active').order_by('-timestamp')[:5]
        return {
            'unread_critical_count': unread_critical_count,
            'recent_active_alerts': recent_active_alerts,
        }
    return {
        'unread_critical_count': 0,
        'recent_active_alerts': [],
    }
