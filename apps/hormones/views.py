from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.animals.models import Animal
from .forms import HormoneReleaseForm, HormoneReservoirForm
from .models import HormoneRelease, HormoneReservoir


class HormoneReservoirListView(LoginRequiredMixin, ListView):
    """Display hormone reservoirs with search, low-stock filter, and pagination"""
    model = HormoneReservoir
    template_name = 'hormones/reservoir_list.html'
    context_object_name = 'reservoirs'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = HormoneReservoir.objects.all()

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(hormone_type__icontains=search_query)

        low_stock = self.request.GET.get('low_stock') == 'on'
        if low_stock:
            queryset = queryset.filter(current_quantity__lte=F('low_threshold'))

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['search_query'] = self.request.GET.get('search', '')
        context['low_stock'] = self.request.GET.get('low_stock') == 'on'
        context['query_params'] = query_params.urlencode()
        return context


class HormoneReservoirDetailView(LoginRequiredMixin, DetailView):
    """Display detailed reservoir inventory information"""
    model = HormoneReservoir
    template_name = 'hormones/reservoir_detail.html'
    context_object_name = 'reservoir'
    login_url = '/auth/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_releases'] = (
            self.object.releases
            .select_related('animal', 'performed_by')
            .order_by('-timestamp')[:10]
        )
        return context


class HormoneReservoirCreateView(LoginRequiredMixin, CreateView):
    """Create a new hormone reservoir"""
    model = HormoneReservoir
    form_class = HormoneReservoirForm
    template_name = 'hormones/reservoir_form.html'
    success_url = reverse_lazy('hormones:reservoir_list')
    login_url = '/auth/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Reservoir for {form.instance.hormone_type} created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Hormone Reservoir'
        context['submit_text'] = 'Create Reservoir'
        return context


class HormoneReservoirUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing hormone reservoir"""
    model = HormoneReservoir
    form_class = HormoneReservoirForm
    template_name = 'hormones/reservoir_form.html'
    login_url = '/auth/login/'

    def get_success_url(self):
        return reverse_lazy('hormones:reservoir_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Reservoir for {form.instance.hormone_type} updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Reservoir: {self.object.hormone_type}'
        context['submit_text'] = 'Update Reservoir'
        return context


class HormoneReservoirDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a hormone reservoir with confirmation"""
    model = HormoneReservoir
    template_name = 'hormones/reservoir_confirm_delete.html'
    success_url = reverse_lazy('hormones:reservoir_list')
    context_object_name = 'reservoir'
    login_url = '/auth/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Reservoir for {self.object.hormone_type} deleted successfully.')
        return super().form_valid(form)


class HormoneReleaseListView(LoginRequiredMixin, ListView):
    """Display hormone release history with filters and pagination"""
    model = HormoneRelease
    template_name = 'hormones/release_list.html'
    context_object_name = 'releases'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = HormoneRelease.objects.select_related('animal', 'reservoir', 'performed_by').all()

        animal_id = self.request.GET.get('animal', '').strip()
        if animal_id:
            if animal_id.isdigit():
                queryset = queryset.filter(animal_id=animal_id)
            else:
                messages.error(self.request, 'Invalid animal filter selected.')
                queryset = queryset.none()

        hormone_type = self.request.GET.get('hormone_type', '').strip()
        if hormone_type:
            queryset = queryset.filter(reservoir__hormone_type__icontains=hormone_type)

        user_id = self.request.GET.get('user', '').strip()
        if user_id:
            if user_id.isdigit():
                queryset = queryset.filter(performed_by_id=user_id)
            else:
                messages.error(self.request, 'Invalid user filter selected.')
                queryset = queryset.none()

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

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['selected_animal'] = self.request.GET.get('animal', '')
        context['hormone_type_query'] = self.request.GET.get('hormone_type', '')
        context['selected_user'] = self.request.GET.get('user', '')
        context['selected_start_date'] = self.request.GET.get('start_date', '')
        context['selected_end_date'] = self.request.GET.get('end_date', '')
        context['query_params'] = query_params.urlencode()
        context['animals'] = Animal.objects.order_by('animal_id')
        context['users'] = User.objects.filter(hormone_releases__isnull=False).distinct().order_by('username')
        return context


class HormoneReleaseDetailView(LoginRequiredMixin, DetailView):
    """Display detailed hormone release information"""
    model = HormoneRelease
    template_name = 'hormones/release_detail.html'
    context_object_name = 'release'
    login_url = '/auth/login/'

    def get_queryset(self):
        return HormoneRelease.objects.select_related('animal', 'reservoir', 'performed_by')


class HormoneReleaseCreateView(LoginRequiredMixin, CreateView):
    """Record a hormone release and update reservoir inventory"""
    model = HormoneRelease
    form_class = HormoneReleaseForm
    template_name = 'hormones/release_form.html'
    login_url = '/auth/login/'

    def form_valid(self, form):
        with transaction.atomic():
            reservoir = HormoneReservoir.objects.select_for_update().get(pk=form.cleaned_data['reservoir'].pk)
            quantity = form.cleaned_data['quantity']

            if quantity > reservoir.current_quantity:
                form.add_error(None, 'Release quantity exceeds available reservoir quantity.')
                messages.error(self.request, 'Hormone release could not be recorded due to insufficient inventory.')
                return self.form_invalid(form)

            reservoir.current_quantity = reservoir.current_quantity - quantity
            if reservoir.current_quantity < 0:
                form.add_error(None, 'Reservoir inventory cannot become negative.')
                messages.error(self.request, 'Hormone release could not be recorded due to insufficient inventory.')
                return self.form_invalid(form)

            reservoir.save(update_fields=['current_quantity', 'updated_at'])
            self.object = form.save(commit=False)
            self.object.reservoir = reservoir
            self.object.performed_by = self.request.user
            self.object.save()

        messages.success(self.request, 'Hormone release recorded and reservoir inventory updated successfully.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('hormones:release_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Record Hormone Release'
        context['submit_text'] = 'Record Release'
        return context
