from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Device
from .forms import DeviceForm


class DeviceListView(LoginRequiredMixin, ListView):
    """Display list of devices with search, filter, and pagination"""
    model = Device
    template_name = 'devices/device_list.html'
    context_object_name = 'devices'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = Device.objects.select_related('assigned_animal').all()

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(device_id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(installation_location__icontains=search_query)
            )

        device_type = self.request.GET.get('device_type', '').strip()
        if device_type:
            queryset = queryset.filter(device_type=device_type)

        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-registration_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_device_type'] = self.request.GET.get('device_type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['device_type_choices'] = Device.DEVICE_TYPE_CHOICES
        context['status_choices'] = Device.STATUS_CHOICES
        return context


class DeviceDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a specific device"""
    model = Device
    template_name = 'devices/device_detail.html'
    context_object_name = 'device'
    login_url = '/auth/login/'

    def get_queryset(self):
        return Device.objects.select_related('assigned_animal')


class DeviceCreateView(LoginRequiredMixin, CreateView):
    """Create a new device"""
    model = Device
    form_class = DeviceForm
    template_name = 'devices/device_form.html'
    success_url = reverse_lazy('devices:list')
    login_url = '/auth/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Device {form.instance.device_id} created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Device'
        context['submit_text'] = 'Create Device'
        return context


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing device"""
    model = Device
    form_class = DeviceForm
    template_name = 'devices/device_form.html'
    login_url = '/auth/login/'

    def get_success_url(self):
        return reverse_lazy('devices:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Device {form.instance.device_id} updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Device: {self.object.device_id}'
        context['submit_text'] = 'Update Device'
        return context


class DeviceDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a device with confirmation"""
    model = Device
    template_name = 'devices/device_confirm_delete.html'
    success_url = reverse_lazy('devices:list')
    login_url = '/auth/login/'

    def delete(self, request, *args, **kwargs):
        device = self.get_object()
        messages.success(request, f'Device {device.device_id} deleted successfully.')
        return super().delete(request, *args, **kwargs)
