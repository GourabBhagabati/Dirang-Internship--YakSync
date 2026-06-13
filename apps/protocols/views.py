from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.animals.models import Animal
from .forms import ProtocolStepForm, TreatmentAssignmentForm, TreatmentProtocolForm
from .models import ProtocolStep, TreatmentAssignment, TreatmentProtocol


class TreatmentProtocolListView(LoginRequiredMixin, ListView):
    """Display treatment protocols with search and pagination"""
    model = TreatmentProtocol
    template_name = 'protocols/protocol_list.html'
    context_object_name = 'protocols'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = TreatmentProtocol.objects.select_related('created_by').annotate(step_count=Count('steps'))

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        context['search_query'] = self.request.GET.get('search', '')
        context['query_params'] = query_params.urlencode()
        return context


class TreatmentProtocolDetailView(LoginRequiredMixin, DetailView):
    """Display protocol details, steps, and recent assignments"""
    model = TreatmentProtocol
    template_name = 'protocols/protocol_detail.html'
    context_object_name = 'protocol'
    login_url = '/auth/login/'

    def get_queryset(self):
        return TreatmentProtocol.objects.select_related('created_by').prefetch_related('steps')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.order_by('step_number')
        context['recent_assignments'] = (
            self.object.assignments
            .select_related('animal', 'assigned_by')
            .order_by('-created_at')[:10]
        )
        return context


class TreatmentProtocolCreateView(LoginRequiredMixin, CreateView):
    """Create a new treatment protocol"""
    model = TreatmentProtocol
    form_class = TreatmentProtocolForm
    template_name = 'protocols/protocol_form.html'
    success_url = reverse_lazy('protocols:list')
    login_url = '/auth/login/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Protocol {form.instance.name} created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Treatment Protocol'
        context['submit_text'] = 'Create Protocol'
        return context


class TreatmentProtocolUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing treatment protocol"""
    model = TreatmentProtocol
    form_class = TreatmentProtocolForm
    template_name = 'protocols/protocol_form.html'
    login_url = '/auth/login/'

    def get_success_url(self):
        return reverse_lazy('protocols:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Protocol {form.instance.name} updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Protocol: {self.object.name}'
        context['submit_text'] = 'Update Protocol'
        return context


class TreatmentProtocolDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a treatment protocol with confirmation"""
    model = TreatmentProtocol
    template_name = 'protocols/protocol_confirm_delete.html'
    context_object_name = 'protocol'
    success_url = reverse_lazy('protocols:list')
    login_url = '/auth/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Protocol {self.object.name} deleted successfully.')
        return super().form_valid(form)


class ProtocolStepMixin(LoginRequiredMixin):
    model = ProtocolStep
    form_class = ProtocolStepForm
    login_url = '/auth/login/'

    def dispatch(self, request, *args, **kwargs):
        self.protocol = get_object_or_404(TreatmentProtocol, pk=kwargs['protocol_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['protocol'] = self.protocol
        return kwargs

    def get_success_url(self):
        return reverse_lazy('protocols:detail', kwargs={'pk': self.protocol.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = self.protocol
        return context


class ProtocolStepCreateView(ProtocolStepMixin, CreateView):
    """Add a step to a protocol"""
    template_name = 'protocols/step_form.html'

    def form_valid(self, form):
        form.instance.protocol = self.protocol
        messages.success(self.request, f'Step {form.instance.step_number} added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Add Step to {self.protocol.name}'
        context['submit_text'] = 'Add Step'
        return context


class ProtocolStepUpdateView(ProtocolStepMixin, UpdateView):
    """Update an existing protocol step"""
    template_name = 'protocols/step_form.html'

    def get_queryset(self):
        return ProtocolStep.objects.filter(protocol=self.protocol)

    def form_valid(self, form):
        messages.success(self.request, f'Step {form.instance.step_number} updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Step {self.object.step_number}'
        context['submit_text'] = 'Update Step'
        return context


class ProtocolStepDeleteView(ProtocolStepMixin, DeleteView):
    """Delete a protocol step with confirmation"""
    template_name = 'protocols/step_confirm_delete.html'
    context_object_name = 'step'

    def get_queryset(self):
        return ProtocolStep.objects.filter(protocol=self.protocol)

    def form_valid(self, form):
        messages.success(self.request, f'Step {self.object.step_number} deleted successfully.')
        return super().form_valid(form)


class TreatmentAssignmentListView(LoginRequiredMixin, ListView):
    """Display treatment assignments with filters and pagination"""
    model = TreatmentAssignment
    template_name = 'protocols/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = TreatmentAssignment.objects.select_related('animal', 'protocol', 'assigned_by').all()

        animal_id = self.request.GET.get('animal', '').strip()
        if animal_id:
            if animal_id.isdigit():
                queryset = queryset.filter(animal_id=animal_id)
            else:
                messages.error(self.request, 'Invalid animal filter selected.')
                queryset = queryset.none()

        protocol_id = self.request.GET.get('protocol', '').strip()
        if protocol_id:
            if protocol_id.isdigit():
                queryset = queryset.filter(protocol_id=protocol_id)
            else:
                messages.error(self.request, 'Invalid protocol filter selected.')
                queryset = queryset.none()

        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)

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
                queryset = queryset.filter(start_date__gte=parsed_start_date)
            if parsed_end_date:
                queryset = queryset.filter(start_date__lte=parsed_end_date)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['selected_animal'] = self.request.GET.get('animal', '')
        context['selected_protocol'] = self.request.GET.get('protocol', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_start_date'] = self.request.GET.get('start_date', '')
        context['selected_end_date'] = self.request.GET.get('end_date', '')
        context['query_params'] = query_params.urlencode()
        context['animals'] = Animal.objects.order_by('animal_id')
        context['protocols'] = TreatmentProtocol.objects.order_by('name')
        context['status_choices'] = TreatmentAssignment.STATUS_CHOICES
        return context


class TreatmentAssignmentDetailView(LoginRequiredMixin, DetailView):
    """Display treatment assignment details"""
    model = TreatmentAssignment
    template_name = 'protocols/assignment_detail.html'
    context_object_name = 'assignment'
    login_url = '/auth/login/'

    def get_queryset(self):
        return TreatmentAssignment.objects.select_related('animal', 'protocol', 'assigned_by')


class TreatmentAssignmentCreateView(LoginRequiredMixin, CreateView):
    """Create a treatment assignment"""
    model = TreatmentAssignment
    form_class = TreatmentAssignmentForm
    template_name = 'protocols/assignment_form.html'
    login_url = '/auth/login/'

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        messages.success(self.request, 'Treatment assignment created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('protocols:assignment_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Treatment Assignment'
        context['submit_text'] = 'Create Assignment'
        return context


class TreatmentAssignmentUpdateView(LoginRequiredMixin, UpdateView):
    """Update a treatment assignment"""
    model = TreatmentAssignment
    form_class = TreatmentAssignmentForm
    template_name = 'protocols/assignment_form.html'
    login_url = '/auth/login/'

    def get_queryset(self):
        return TreatmentAssignment.objects.select_related('animal', 'protocol', 'assigned_by')

    def get_success_url(self):
        return reverse_lazy('protocols:assignment_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Treatment assignment updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Assignment: {self.object.animal.animal_id}'
        context['submit_text'] = 'Update Assignment'
        return context
