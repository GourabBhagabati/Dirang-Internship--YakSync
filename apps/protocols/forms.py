from django import forms

from apps.animals.models import Animal
from .models import ProtocolStep, TreatmentAssignment, TreatmentProtocol


class TreatmentProtocolForm(forms.ModelForm):
    """Form for creating and updating treatment protocols"""

    class Meta:
        model = TreatmentProtocol
        fields = ['name', 'description', 'duration_days']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Protocol name',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Protocol description',
                'rows': 4,
                'required': True,
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Duration in days',
                'min': '1',
                'required': True,
            }),
        }
        labels = {
            'name': 'Protocol Name',
            'description': 'Description',
            'duration_days': 'Duration (days)',
        }

    def clean_duration_days(self):
        duration_days = self.cleaned_data.get('duration_days')
        if duration_days is not None and duration_days <= 0:
            raise forms.ValidationError('Duration must be at least 1 day.')
        return duration_days


class ProtocolStepForm(forms.ModelForm):
    """Form for managing protocol steps"""

    class Meta:
        model = ProtocolStep
        fields = ['step_number', 'description', 'hormone_type', 'dosage', 'day_offset', 'time_of_day']
        widgets = {
            'step_number': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Step number',
                'min': '1',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Step description',
                'rows': 4,
                'required': True,
            }),
            'hormone_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Hormone type',
                'required': True,
            }),
            'dosage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dosage',
                'step': '0.01',
                'min': '0.01',
                'required': True,
            }),
            'day_offset': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Days from start',
                'min': '0',
                'required': True,
            }),
            'time_of_day': forms.TimeInput(format='%H:%M', attrs={
                'class': 'form-input',
                'type': 'time',
                'required': True,
            }),
        }
        labels = {
            'step_number': 'Step Number',
            'description': 'Description',
            'hormone_type': 'Hormone Type',
            'dosage': 'Dosage',
            'day_offset': 'Day Offset',
            'time_of_day': 'Time of Day',
        }

    def __init__(self, *args, **kwargs):
        self.protocol = kwargs.pop('protocol', None)
        super().__init__(*args, **kwargs)
        self.fields['time_of_day'].input_formats = ['%H:%M', '%H:%M:%S']

    def clean_step_number(self):
        step_number = self.cleaned_data.get('step_number')
        if step_number is not None and step_number <= 0:
            raise forms.ValidationError('Step number must be greater than 0.')

        if self.protocol and step_number is not None:
            qs = ProtocolStep.objects.filter(protocol=self.protocol, step_number=step_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This step number already exists for the protocol.')
        return step_number

    def clean_day_offset(self):
        day_offset = self.cleaned_data.get('day_offset')
        if day_offset is not None and day_offset < 0:
            raise forms.ValidationError('Day offset cannot be negative.')
        if self.protocol and day_offset is not None and day_offset > self.protocol.duration_days:
            raise forms.ValidationError('Day offset cannot exceed protocol duration.')
        return day_offset

    def clean_dosage(self):
        dosage = self.cleaned_data.get('dosage')
        if dosage is not None and dosage <= 0:
            raise forms.ValidationError('Dosage must be greater than 0.')
        return dosage


class TreatmentAssignmentForm(forms.ModelForm):
    """Form for assigning treatment protocols to animals"""

    class Meta:
        model = TreatmentAssignment
        fields = ['animal', 'protocol', 'start_date', 'end_date', 'status', 'progress']
        widgets = {
            'animal': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'protocol': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': True,
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': True,
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0-100',
                'min': '0',
                'max': '100',
                'required': True,
            }),
        }
        labels = {
            'animal': 'Animal',
            'protocol': 'Treatment Protocol',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'status': 'Status',
            'progress': 'Progress (%)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].queryset = Animal.objects.order_by('animal_id')
        self.fields['animal'].empty_label = 'Select animal'
        self.fields['protocol'].queryset = TreatmentProtocol.objects.order_by('name')
        self.fields['protocol'].empty_label = 'Select protocol'

    def clean_progress(self):
        progress = self.cleaned_data.get('progress')
        if progress is not None and (progress < 0 or progress > 100):
            raise forms.ValidationError('Progress must be between 0% and 100%.')
        return progress

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')
        progress = cleaned_data.get('progress')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date cannot be before start date.')

        if status == 'pending' and progress != 0:
            self.add_error('progress', 'Pending assignments must have 0% progress.')
        elif status == 'in_progress' and progress is not None and not 1 <= progress <= 99:
            self.add_error('progress', 'In-progress assignments must be between 1% and 99%.')
        elif status == 'completed' and progress != 100:
            self.add_error('progress', 'Completed assignments must have 100% progress.')

        return cleaned_data
