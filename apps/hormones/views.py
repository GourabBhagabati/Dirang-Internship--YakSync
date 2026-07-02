from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date, parse_time
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
        try:
            from django.core.management import call_command
            call_command('makemigrations', interactive=False)
            call_command('migrate', interactive=False)
        except Exception as e:
            print(f"Automatic migration error: {e}")

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


# --- API Endpoints for Hormone Management Dashboard ---
import json
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.alerts.models import Alert
from apps.logs.models import ActivityLog
from apps.logs.signals import get_client_ip, get_user_role
from .models import HormoneSchedule


@login_required(login_url='/auth/login/')
def api_fetch_animals(request):
    """Fetch all animals for dropdown selection"""
    animals = Animal.objects.all().order_by('animal_id')
    data = []
    for animal in animals:
        data.append({
            'id': animal.id,
            'animal_id': animal.animal_id,
            'name': animal.name,
            'breed': animal.breed,
            'age': animal.age,
            'health_status': animal.get_health_status_display(),
            'reproductive_status': animal.get_reproductive_status_display(),
        })
    return JsonResponse({'animals': data})


@login_required(login_url='/auth/login/')
def api_fetch_reservoirs(request):
    """Fetch hormone reservoirs with labels, levels, and thresholds"""
    reservoirs = HormoneReservoir.objects.all().order_by('id')
    data = []
    for index, res in enumerate(reservoirs):
        letter = chr(65 + index)  # Reservoir A, Reservoir B, etc.
        fill_pct = 0
        if res.initial_quantity > 0:
            fill_pct = round((res.current_quantity / res.initial_quantity) * 100, 2)
        data.append({
            'id': res.id,
            'label': f"Reservoir {letter}",
            'hormone_type': res.hormone_type,
            'initial_quantity': float(res.initial_quantity),
            'current_quantity': float(res.current_quantity),
            'unit': res.unit,
            'low_threshold': float(res.low_threshold),
            'is_low': res.is_low,
            'fill_percentage': fill_pct,
        })
    return JsonResponse({'reservoirs': data})


@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def api_release_hormone(request):
    """Handle immediate release of hormone from selected reservoir to selected animal"""
    try:
        body = json.loads(request.body)
        animal_id = body.get('animal_id')
        reservoir_id = body.get('reservoir_id')
        quantity = Decimal(str(body.get('quantity')))
        notes = body.get('notes', '')
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)
        
    if quantity <= 0:
        return JsonResponse({'error': 'Quantity must be greater than zero'}, status=400)
        
    try:
        animal = Animal.objects.get(pk=animal_id)
        reservoir = HormoneReservoir.objects.get(pk=reservoir_id)
    except (Animal.DoesNotExist, HormoneReservoir.DoesNotExist):
        return JsonResponse({'error': 'Animal or Reservoir not found'}, status=404)
        
    if quantity > reservoir.current_quantity:
        return JsonResponse({'error': 'Release quantity exceeds available reservoir quantity.'}, status=400)
        
    with transaction.atomic():
        reservoir = HormoneReservoir.objects.select_for_update().get(pk=reservoir_id)
        if quantity > reservoir.current_quantity:
            return JsonResponse({'error': 'Release quantity exceeds available reservoir quantity.'}, status=400)
            
        reservoir.current_quantity -= quantity
        reservoir.save(update_fields=['current_quantity', 'updated_at'])
        
        release = HormoneRelease.objects.create(
            reservoir=reservoir,
            animal=animal,
            quantity=quantity,
            performed_by=request.user,
            notes=notes or 'Immediate hormone release from dashboard'
        )
        
        # Log action manually
        ActivityLog.objects.create(
            user=request.user,
            user_role=get_user_role(request.user),
            action_type='create',
            module_accessed='hormones',
            description=f"User \"{request.user.username}\" released {quantity} {reservoir.unit} of {reservoir.hormone_type} to animal {animal.animal_id}.",
            ip_address=get_client_ip(request)
        )
        
    return JsonResponse({
        'message': 'Release command sent successfully',
        'release': {
            'id': release.id,
            'quantity': float(release.quantity),
            'timestamp': release.timestamp.isoformat(),
        }
    })


@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def api_schedule_hormone(request):
    """Schedule a hormone release for a future date/time"""
    try:
        body = json.loads(request.body)
        animal_id = body.get('animal_id')
        reservoir_id = body.get('reservoir_id')
        quantity = Decimal(str(body.get('quantity')))
        date_str = body.get('release_date')
        time_str = body.get('release_time')
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)
        
    if quantity <= 0:
        return JsonResponse({'error': 'Quantity must be greater than zero'}, status=400)
        
    parsed_date = parse_date(date_str)
    parsed_time = parse_time(time_str)
    
    if not parsed_date or not parsed_time:
        return JsonResponse({'error': 'Invalid date or time format'}, status=400)
        
    try:
        animal = Animal.objects.get(pk=animal_id)
        reservoir = HormoneReservoir.objects.get(pk=reservoir_id)
    except (Animal.DoesNotExist, HormoneReservoir.DoesNotExist):
        return JsonResponse({'error': 'Animal or Reservoir not found'}, status=404)
        
    schedule = HormoneSchedule.objects.create(
        animal=animal,
        reservoir=reservoir,
        quantity=quantity,
        release_date=parsed_date,
        release_time=parsed_time,
        status='scheduled',
        performed_by=request.user
    )
    
    # Log action manually
    ActivityLog.objects.create(
        user=request.user,
        user_role=get_user_role(request.user),
        action_type='create',
        module_accessed='hormones',
        description=f"User \"{request.user.username}\" scheduled release of {quantity} {reservoir.unit} of {reservoir.hormone_type} for animal {animal.animal_id} on {date_str} at {time_str}.",
        ip_address=get_client_ip(request)
    )
    
    return JsonResponse({
        'message': 'Schedule created successfully',
        'schedule': {
            'id': schedule.id,
            'date': schedule.release_date.isoformat(),
            'time': schedule.release_time.isoformat(),
        }
    })


@login_required(login_url='/auth/login/')
def api_fetch_schedules(request):
    """Fetch scheduled releases for a specific animal"""
    animal_id = request.GET.get('animal_id')
    if not animal_id:
        return JsonResponse({'error': 'animal_id is required'}, status=400)
        
    schedules = HormoneSchedule.objects.filter(animal_id=animal_id, status='scheduled').order_by('release_date', 'release_time')
    data = []
    for s in schedules:
        data.append({
            'id': s.id,
            'hormone_type': s.reservoir.hormone_type,
            'quantity': float(s.quantity),
            'unit': s.reservoir.unit,
            'release_date': s.release_date.isoformat(),
            'release_time': s.release_time.isoformat(),
            'status': s.status,
        })
    return JsonResponse({'schedules': data})


@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def api_cancel_schedule(request):
    """Cancel a scheduled hormone release"""
    try:
        body = json.loads(request.body)
        schedule_id = body.get('schedule_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)
        
    try:
        schedule = HormoneSchedule.objects.get(pk=schedule_id)
    except HormoneSchedule.DoesNotExist:
        return JsonResponse({'error': 'Schedule not found'}, status=404)
        
    if schedule.status != 'scheduled':
        return JsonResponse({'error': 'Only scheduled releases can be cancelled'}, status=400)
        
    schedule.status = 'cancelled'
    schedule.save(update_fields=['status'])
    
    # Log action manually
    ActivityLog.objects.create(
        user=request.user,
        user_role=get_user_role(request.user),
        action_type='update',
        module_accessed='hormones',
        description=f"User \"{request.user.username}\" cancelled scheduled hormone release (ID {schedule.id}) for animal {schedule.animal.animal_id}.",
        ip_address=get_client_ip(request)
    )
    
    return JsonResponse({'message': 'Schedule cancelled successfully'})


@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def api_emergency_stop(request):
    """Perform emergency stop for an animal, cancelling all pending scheduled releases and raising critical alert"""
    try:
        body = json.loads(request.body)
        animal_id = body.get('animal_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)
        
    try:
        animal = Animal.objects.get(pk=animal_id)
    except Animal.DoesNotExist:
        return JsonResponse({'error': 'Animal not found'}, status=404)
        
    schedules = HormoneSchedule.objects.filter(animal=animal, status='scheduled')
    count = schedules.count()
    schedules.update(status='cancelled')
    
    # Create critical alert in system
    Alert.objects.create(
        title="Emergency Stop Activated",
        alert_type="missed_schedule",
        severity="critical",
        description=f"Emergency stop activated. {count} scheduled releases cancelled for animal {animal.animal_id}.",
        animal=animal,
        status='active'
    )
    
    # Log action manually
    ActivityLog.objects.create(
        user=request.user,
        user_role=get_user_role(request.user),
        action_type='alert_action',
        module_accessed='hormones',
        description=f"User \"{request.user.username}\" triggered emergency stop for animal {animal.animal_id}. {count} schedules cancelled.",
        ip_address=get_client_ip(request)
    )
    
    return JsonResponse({
        'message': 'Emergency stop activated successfully',
        'cancelled_count': count
    })


@login_required(login_url='/auth/login/')
def api_release_history(request):
    """Fetch hormone release history (optionally filtered by animal)"""
    animal_id = request.GET.get('animal_id')
    
    releases = HormoneRelease.objects.select_related('animal', 'reservoir', 'performed_by').all()
    if animal_id:
        releases = releases.filter(animal_id=animal_id)
        
    releases = releases.order_by('-timestamp')[:20]
    data = []
    for r in releases:
        data.append({
            'id': r.id,
            'animal_id': r.animal.animal_id,
            'animal_name': r.animal.name,
            'hormone_type': r.reservoir.hormone_type,
            'quantity': float(r.quantity),
            'unit': r.reservoir.unit,
            'timestamp': r.timestamp.isoformat(),
            'performed_by': r.performed_by.username if r.performed_by else 'System',
            'notes': r.notes,
        })
    return JsonResponse({'history': data})


import io
from django.core.management import call_command

@login_required(login_url='/auth/login/')
def api_run_debug(request):
    """Run makemigrations and migrate programmatically to sync SQLite database"""
    out = io.StringIO()
    err = io.StringIO()
    try:
        print("--- Running makemigrations ---", file=out)
        call_command('makemigrations', stdout=out, stderr=err)
        print("--- Running migrate ---", file=out)
        call_command('migrate', stdout=out, stderr=err)
        status = "success"
    except Exception as e:
        status = f"error: {str(e)}"
        import traceback
        traceback.print_exc(file=err)
        
    return JsonResponse({
        'status': status,
        'stdout': out.getvalue(),
        'stderr': err.getvalue()
    })


