from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Animal
from .forms import AnimalForm


class AnimalListView(LoginRequiredMixin, ListView):
    """Display list of animals with search, filter, and pagination"""
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 10
    login_url = '/auth/login/'
    
    def get_queryset(self):
        queryset = Animal.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(animal_id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(breed__icontains=search_query)
            )
        
        # Filter by health status
        health_status = self.request.GET.get('health_status', '').strip()
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        
        # Filter by reproductive status
        reproductive_status = self.request.GET.get('reproductive_status', '').strip()
        if reproductive_status:
            queryset = queryset.filter(reproductive_status=reproductive_status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_health_status'] = self.request.GET.get('health_status', '')
        context['selected_reproductive_status'] = self.request.GET.get('reproductive_status', '')
        
        # Add choices for filters
        context['health_status_choices'] = Animal.HEALTH_STATUS_CHOICES
        context['reproductive_status_choices'] = Animal.REPRODUCTIVE_STATUS_CHOICES
        
        return context


class AnimalDetailView(LoginRequiredMixin, DetailView):
    """Display detailed information about a specific animal"""
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
    login_url = '/auth/login/'


class AnimalCreateView(LoginRequiredMixin, CreateView):
    """Create a new animal"""
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    success_url = reverse_lazy('animals:list')
    login_url = '/auth/login/'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Animal {form.instance.animal_id} created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Animal'
        context['submit_text'] = 'Create Animal'
        return context


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing animal"""
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    login_url = '/auth/login/'
    
    def get_success_url(self):
        return reverse_lazy('animals:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Animal {form.instance.animal_id} updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Animal: {self.object.animal_id}'
        context['submit_text'] = 'Update Animal'
        return context


class AnimalDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an animal with confirmation"""
    model = Animal
    template_name = 'animals/animal_confirm_delete.html'
    success_url = reverse_lazy('animals:list')
    login_url = '/auth/login/'
    
    def delete(self, request, *args, **kwargs):
        animal = self.get_object()
        messages.success(request, f'Animal {animal.animal_id} deleted successfully.')
        return super().delete(request, *args, **kwargs)
