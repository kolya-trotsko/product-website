import re
from django import forms


PHONE_RE = re.compile(r"^[0-9+()\\-\\s]{7,20}$")


class OrderForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=100)
    phone = forms.CharField(min_length=7, max_length=20)
    option = forms.CharField(min_length=2, max_length=100)

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or "").strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Invalid phone.")
        return phone


class ServiceOrderForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=100)
    phone = forms.CharField(min_length=7, max_length=20)
    address = forms.CharField(min_length=5, max_length=100)
    services = forms.MultipleChoiceField(required=True)

    def __init__(self, *args, service_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["services"].choices = service_choices or []

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or "").strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Invalid phone.")
        return phone
