from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    warehouse_description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'city',
            'delivery_provider',
            'delivery_type',
            'street',
            'house_number',
            'flat_number',
            'warehouse_description'
        ]

        widgets = {
            'street': forms.TextInput(attrs={'placeholder': 'Street name'}),
            'house_number': forms.TextInput(attrs={'placeholder': 'House number'}),
            'flat_number': forms.TextInput(attrs={'placeholder': 'Flat number'})
        }

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        delivery_provider = cleaned_data.get('delivery_provider')

        if delivery_type == 'courier':
            required_fields = ['street', 'house_number', 'flat_number']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for courier delivery.')

        elif delivery_type == 'branch':
            if delivery_provider == 'nova_poshta':
                if not cleaned_data.get('warehouse_description'):
                    raise forms.ValidationError('Please select a warehouse for Nova Poshta branch delivery.')
            else:
                # For other providers
                pass

        return cleaned_data
