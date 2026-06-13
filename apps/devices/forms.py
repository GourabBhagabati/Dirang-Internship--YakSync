from django import forms
from apps.animals.models import Animal
from .models import Device


class DeviceForm(forms.ModelForm):
    """Form for creating and updating devices"""

    class Meta:
        model = Device
        fields = [
            'device_id', 'name', 'device_type', 'installation_location',
            'status', 'battery_level', 'assigned_animal', 'last_communication',
        ]
        widgets = {
            'device_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., DEV001',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Device name',
                'required': True,
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'installation_location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Pasture A, North Field',
                'required': True,
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'battery_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0-100',
                'required': True,
                'min': '0',
                'max': '100',
            }),
            'assigned_animal': forms.Select(attrs={
                'class': 'form-input',
            }),
            'last_communication': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'class': 'form-input',
                    'type': 'datetime-local',
                },
            ),
        }
        labels = {
            'device_id': 'Device ID',
            'name': 'Device Name',
            'device_type': 'Device Type',
            'installation_location': 'Installation Location',
            'status': 'Status',
            'battery_level': 'Battery Level (%)',
            'assigned_animal': 'Assigned Animal',
            'last_communication': 'Last Communication Time',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_animal'].queryset = Animal.objects.all().order_by('animal_id')
        self.fields['assigned_animal'].required = False
        self.fields['assigned_animal'].empty_label = 'No animal assigned'
        self.fields['last_communication'].required = False
        self.fields['last_communication'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]

    def clean_device_id(self):
        device_id = self.cleaned_data.get('device_id')
        qs = Device.objects.filter(device_id=device_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Device ID already exists.')
        return device_id

    def clean_battery_level(self):
        battery_level = self.cleaned_data.get('battery_level')
        if battery_level is not None and (battery_level < 0 or battery_level > 100):
            raise forms.ValidationError('Battery level must be between 0 and 100.')
        return battery_level
