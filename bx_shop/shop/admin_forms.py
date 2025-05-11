from django import forms


class DiscountForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    percentage = forms.DecimalField(label="Discount Percentage", min_value=1, max_value=100)
