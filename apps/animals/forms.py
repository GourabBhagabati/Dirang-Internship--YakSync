from django import forms
from .models import Animal


class AnimalForm(forms.ModelForm):
    """Form for creating and updating animals"""
    
    class Meta:
        model = Animal
        fields = ['animal_id', 'name', 'species', 'breed', 'age', 'gender', 
                  'weight', 'health_status', 'reproductive_status']
        widgets = {
            'animal_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., YAK001',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Animal name',
                'required': True,
            }),
            'species': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Yak, Cattle, Sheep',
                'required': True,
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Highland Yak',
                'required': True,
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Age in years',
                'required': True,
                'min': '0',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Weight in kg',
                'required': True,
                'step': '0.01',
                'min': '0',
            }),
            'health_status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'reproductive_status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
        }
        labels = {
            'animal_id': 'Animal ID',
            'name': 'Name',
            'species': 'Species',
            'breed': 'Breed',
            'age': 'Age (years)',
            'gender': 'Gender',
            'weight': 'Weight (kg)',
            'health_status': 'Health Status',
            'reproductive_status': 'Reproductive Status',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].initial = 'female'
        self.fields['gender'].widget = forms.HiddenInput(attrs={'value': 'female'})
    
    def clean_animal_id(self):
        animal_id = self.cleaned_data.get('animal_id')
        # Check for uniqueness, excluding current instance during updates
        qs = Animal.objects.filter(animal_id=animal_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Animal ID already exists.')
        return animal_id
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and age < 0:
            raise forms.ValidationError('Age cannot be negative.')
        if age is not None and age > 30:
            raise forms.ValidationError('Age seems unusually high. Please verify.')
        return age
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise forms.ValidationError('Weight must be greater than 0.')
        return weight
