from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm, RegisterForm, UserUpdateForm, UserProfileUpdateForm
from .models import UserProfile


class LoginView(View):
    template_name = 'authentication/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    template_name = 'authentication/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('authentication:login')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('authentication:login')


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'authentication/profile_edit.html'

    def get(self, request):
        # Ensure UserProfile exists for this user (safeguard for older/superuser accounts)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Automatically replace the old image when a new one is uploaded
            old_image = profile.profile_image
            new_image = profile_form.cleaned_data.get('profile_image')
            
            if new_image and old_image and old_image != new_image:
                try:
                    import os
                    if os.path.exists(old_image.path):
                        os.remove(old_image.path)
                except Exception:
                    pass
            
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('authentication:profile_edit')
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile
        }
        return render(request, self.template_name, context)

