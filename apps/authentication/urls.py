from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]
