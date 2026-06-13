from django.urls import path
from . import views

app_name = 'protocols'

urlpatterns = [
    path('', views.TreatmentProtocolListView.as_view(), name='list'),
    path('create/', views.TreatmentProtocolCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TreatmentProtocolDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TreatmentProtocolUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TreatmentProtocolDeleteView.as_view(), name='delete'),
    path('<int:protocol_pk>/steps/create/', views.ProtocolStepCreateView.as_view(), name='step_create'),
    path('<int:protocol_pk>/steps/<int:pk>/edit/', views.ProtocolStepUpdateView.as_view(), name='step_edit'),
    path('<int:protocol_pk>/steps/<int:pk>/delete/', views.ProtocolStepDeleteView.as_view(), name='step_delete'),
    path('assignments/', views.TreatmentAssignmentListView.as_view(), name='assignment_list'),
    path('assignments/create/', views.TreatmentAssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/', views.TreatmentAssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.TreatmentAssignmentUpdateView.as_view(), name='assignment_edit'),
]
