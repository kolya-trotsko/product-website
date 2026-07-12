from django import forms

from ks_klimat_kh.validators import validate_phone


class OrderForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=100)
    phone = forms.CharField(min_length=7, max_length=20)
    option = forms.CharField(min_length=2, max_length=100)

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        return validate_phone(phone)


class ServiceOrderForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=100)
    phone = forms.CharField(min_length=7, max_length=20)
    address = forms.CharField(min_length=5, max_length=100)
    services = forms.MultipleChoiceField(required=True)

    def __init__(self, *args, service_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["services"].choices = service_choices or []

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        return validate_phone(phone)
