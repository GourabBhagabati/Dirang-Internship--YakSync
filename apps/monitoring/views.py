from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.generic import DetailView, ListView

from apps.animals.models import Animal
from apps.devices.models import Device
from .models import SensorReading


class SensorReadingListView(LoginRequiredMixin, ListView):
    """Display sensor readings with search, filters, and pagination"""
    model = SensorReading
    template_name = 'monitoring/sensor_reading_list.html'
    context_object_name = 'readings'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = SensorReading.objects.select_related('animal', 'device').all()

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(animal__animal_id__icontains=search_query) |
                Q(animal__name__icontains=search_query) |
                Q(device__device_id__icontains=search_query) |
                Q(device__name__icontains=search_query) |
                Q(unit__icontains=search_query)
            )

        animal_id = self.request.GET.get('animal', '').strip()
        if animal_id:
            if animal_id.isdigit():
                queryset = queryset.filter(animal_id=animal_id)
            else:
                messages.error(self.request, 'Invalid animal filter selected.')
                queryset = queryset.none()

        device_id = self.request.GET.get('device', '').strip()
        if device_id:
            if device_id.isdigit():
                queryset = queryset.filter(device_id=device_id)
            else:
                messages.error(self.request, 'Invalid device filter selected.')
                queryset = queryset.none()

        sensor_type = self.request.GET.get('sensor_type', '').strip()
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()
        parsed_start_date = parse_date(start_date) if start_date else None
        parsed_end_date = parse_date(end_date) if end_date else None

        if start_date and parsed_start_date is None:
            messages.error(self.request, 'Invalid start date. Please use a valid date.')
            queryset = queryset.none()
        elif end_date and parsed_end_date is None:
            messages.error(self.request, 'Invalid end date. Please use a valid date.')
            queryset = queryset.none()
        elif parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
            messages.error(self.request, 'Start date cannot be later than end date.')
            queryset = queryset.none()
        else:
            if parsed_start_date:
                queryset = queryset.filter(timestamp__date__gte=parsed_start_date)
            if parsed_end_date:
                queryset = queryset.filter(timestamp__date__lte=parsed_end_date)

        abnormal_only = self.request.GET.get('abnormal_only') == 'on'
        if abnormal_only:
            queryset = queryset.filter(is_abnormal=True)

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['search_query'] = self.request.GET.get('search', '')
        context['selected_animal'] = self.request.GET.get('animal', '')
        context['selected_device'] = self.request.GET.get('device', '')
        context['selected_sensor_type'] = self.request.GET.get('sensor_type', '')
        context['selected_start_date'] = self.request.GET.get('start_date', '')
        context['selected_end_date'] = self.request.GET.get('end_date', '')
        context['abnormal_only'] = self.request.GET.get('abnormal_only') == 'on'
        context['query_params'] = query_params.urlencode()
        context['animals'] = Animal.objects.order_by('animal_id')
        context['devices'] = Device.objects.order_by('device_id')
        context['sensor_type_choices'] = SensorReading.SENSOR_TYPE_CHOICES
        return context


class SensorReadingDetailView(LoginRequiredMixin, DetailView):
    """Display detailed sensor reading information and recent related history"""
    model = SensorReading
    template_name = 'monitoring/sensor_reading_detail.html'
    context_object_name = 'reading'
    login_url = '/auth/login/'

    def get_queryset(self):
        return SensorReading.objects.select_related('animal', 'device')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_history'] = (
            SensorReading.objects.select_related('animal', 'device')
            .filter(
                animal=self.object.animal,
                sensor_type=self.object.sensor_type,
            )
            .exclude(pk=self.object.pk)
            .order_by('-timestamp')[:10]
        )
        return context


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

class HerdTelemetryAPIView(LoginRequiredMixin, View):
    """API endpoint returning latest telemetry for the herd"""
    login_url = '/auth/login/'

    def get(self, request):
        readings = SensorReading.objects.select_related('animal').order_by('-timestamp')[:30]
        
        temp_readings = [r for r in readings if r.sensor_type == 'temperature']
        move_readings = [r for r in readings if r.sensor_type == 'movement']
        
        temp_data = [{
            'timestamp': r.timestamp.strftime('%H:%M'),
            'value': float(r.value),
            'animal_id': r.animal.animal_id,
        } for r in reversed(temp_readings)]
        
        move_data = [{
            'timestamp': r.timestamp.strftime('%H:%M'),
            'value': float(r.value),
            'animal_id': r.animal.animal_id,
        } for r in reversed(move_readings)]
        
        return JsonResponse({
            'temp_data': temp_data,
            'move_data': move_data
        })


class AnimalTelemetryAPIView(LoginRequiredMixin, View):
    """API endpoint returning latest telemetry for a specific animal"""
    login_url = '/auth/login/'

    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, pk=animal_id)
        
        temp_readings = SensorReading.objects.filter(animal=animal, sensor_type='temperature').order_by('-timestamp')[:30]
        move_readings = SensorReading.objects.filter(animal=animal, sensor_type='movement').order_by('-timestamp')[:30]
        
        temp_data = [{
            'timestamp': r.timestamp.strftime('%m-%d %H:%M'),
            'value': float(r.value)
        } for r in reversed(temp_readings)]
        
        move_data = [{
            'timestamp': r.timestamp.strftime('%m-%d %H:%M'),
            'value': float(r.value)
        } for r in reversed(move_readings)]
        
        return JsonResponse({
            'animal_id': animal.animal_id,
            'name': animal.name,
            'temp_data': temp_data,
            'move_data': move_data
        })

