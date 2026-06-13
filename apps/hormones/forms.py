from django import forms

from apps.animals.models import Animal
from .models import HormoneRelease, HormoneReservoir


class HormoneReservoirForm(forms.ModelForm):
    """Form for creating and updating hormone reservoirs"""

    class Meta:
        model = HormoneReservoir
        fields = ['hormone_type', 'initial_quantity', 'current_quantity', 'unit', 'low_threshold']
        widgets = {
            'hormone_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Progesterone',
                'required': True,
            }),
            'initial_quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Initial quantity',
                'required': True,
                'step': '0.01',
                'min': '0.01',
            }),
            'current_quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Current quantity',
                'required': True,
                'step': '0.01',
                'min': '0',
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., ml, mg',
                'required': True,
            }),
            'low_threshold': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Low stock threshold',
                'required': True,
                'step': '0.01',
                'min': '0',
            }),
        }
        labels = {
            'hormone_type': 'Hormone Type',
            'initial_quantity': 'Initial Quantity',
            'current_quantity': 'Current Quantity',
            'unit': 'Unit',
            'low_threshold': 'Low Stock Threshold',
        }

    def clean_initial_quantity(self):
        initial_quantity = self.cleaned_data.get('initial_quantity')
        if initial_quantity is not None and initial_quantity <= 0:
            raise forms.ValidationError('Initial quantity must be greater than 0.')
        return initial_quantity

    def clean_current_quantity(self):
        current_quantity = self.cleaned_data.get('current_quantity')
        if current_quantity is not None and current_quantity < 0:
            raise forms.ValidationError('Current quantity cannot be negative.')
        return current_quantity

    def clean_low_threshold(self):
        low_threshold = self.cleaned_data.get('low_threshold')
        if low_threshold is not None and low_threshold < 0:
            raise forms.ValidationError('Low stock threshold cannot be negative.')
        return low_threshold

    def clean(self):
        cleaned_data = super().clean()
        initial_quantity = cleaned_data.get('initial_quantity')
        current_quantity = cleaned_data.get('current_quantity')
        low_threshold = cleaned_data.get('low_threshold')

        if initial_quantity is not None and current_quantity is not None:
            if current_quantity > initial_quantity:
                self.add_error('current_quantity', 'Current quantity cannot exceed initial quantity.')

        if initial_quantity is not None and low_threshold is not None:
            if low_threshold > initial_quantity:
                self.add_error('low_threshold', 'Low stock threshold cannot exceed initial quantity.')

        return cleaned_data


class HormoneReleaseForm(forms.ModelForm):
    """Form for recording hormone release events"""

    class Meta:
        model = HormoneRelease
        fields = ['animal', 'reservoir', 'quantity', 'notes']
        widgets = {
            'animal': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'reservoir': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Quantity released',
                'required': True,
                'step': '0.01',
                'min': '0.01',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Optional notes',
                'rows': 4,
            }),
        }
        labels = {
            'animal': 'Animal',
            'reservoir': 'Hormone Reservoir',
            'quantity': 'Quantity Released',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].queryset = Animal.objects.order_by('animal_id')
        self.fields['animal'].empty_label = 'Select animal'
        self.fields['reservoir'].queryset = HormoneReservoir.objects.order_by('hormone_type')
        self.fields['reservoir'].empty_label = 'Select reservoir'
        self.fields['notes'].required = False

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('Release quantity must be greater than 0.')
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        reservoir = cleaned_data.get('reservoir')
        quantity = cleaned_data.get('quantity')

        if reservoir and quantity and quantity > reservoir.current_quantity:
            raise forms.ValidationError(
                f'Release quantity exceeds available reservoir quantity '
                f'({reservoir.current_quantity} {reservoir.unit}).'
            )

        return cleaned_data
